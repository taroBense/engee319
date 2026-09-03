import datetime, requests
import RPi.GPIO as GPIO
from time import sleep, time
from ina219 import INA219
# user modules
import creds
import clearsky_solar_pred
import load

MIN_POWER_THRESHOLD = 1

# —— Thresholds (NiMH 7S: 6 x 1.4V, 6 x 1.2V nominal = 8.4V) ——
V_FULL       = 8.6    # V: stop charging at/above this (battery full)
V_LOW        = 7.2    # V: attempt to charge below this (nominal)
V_LOAD_OK    = 7.2    # V: loads allowed at/above this
V_LOAD_CUT   = 7      # V: loads cut off below this (protect battery)
V_MIN        = 0.5    # V: minimum valid voltage reading from ADC

# 3 optocoupler outputs
CHARGE_PIN   = 18     # BCM 18 = Optocoupler 1 (charge control)
LOAD_PIN     = 23     # BCM 23 = Optocoupler 2 (load control)
AUX_PIN      = 24     # BCM 24 = Optocoupler 3 (auxiliary control output)

# 2 INA219 I2C sensors
BAT_SENSOR_ADDR = 0x40
PV_SENSOR_ADDR  = 0x41

INTERVAL     = 5.0    # s: normal loop period
SLEEP_NOSUN  = 60     # s: pause after No Sun detection
PROBE_DELAY  = 2.0    # s: settle time after closing charge relay

API_KEY      = creds.API_KEY
TS_URL       = "https://api.thingspeak.com/update"
UPLOAD_INTVL = 15     # s: ThingSpeak free-tier minimum

# Load status codes (numeric, so ThingSpeak field5 can chart them)
LOAD_OFF, LOAD_ON, LOAD_HOLD = 0, 1, 2
LOAD_NAME = {LOAD_OFF: "LOAD_OFF", LOAD_ON: "LOAD_ON", LOAD_HOLD: "LOAD_HOLD"}

# —— Hardware init ————————————————————————————
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(CHARGE_PIN, GPIO.OUT)
GPIO.setup(LOAD_PIN, GPIO.OUT)
GPIO.setup(AUX_PIN, GPIO.OUT)
GPIO.output(CHARGE_PIN, GPIO.LOW)   # charge relay OPEN on startup (safe)
GPIO.output(LOAD_PIN, GPIO.LOW)      # load relay OPEN on startup (safe)
GPIO.output(AUX_PIN, GPIO.LOW)       # aux relay OPEN on startup (safe)

# INA219 voltage/current monitors
try:
    bat_sensor = INA219(shunt_ohms=0.1, max_expected_amps=3.0, busnum=1, address=BAT_SENSOR_ADDR)
    pv_sensor = INA219(shunt_ohms=0.1, max_expected_amps=3.0, busnum=1, address=PV_SENSOR_ADDR)

    bat_sensor.reset(); pv_sensor.reset()
    bat_sensor.configure(voltage_range=bat_sensor.RANGE_32V, gain=bat_sensor.GAIN_AUTO,
                        bus_adc=bat_sensor.ADC_4SAMP, shunt_adc=bat_sensor.ADC_4SAMP)
    pv_sensor.configure(voltage_range=pv_sensor.RANGE_32V, gain=pv_sensor.GAIN_AUTO,
                       bus_adc=pv_sensor.ADC_4SAMP, shunt_adc=pv_sensor.ADC_4SAMP)
    sensor_ready = True
except Exception:
    bat_sensor = None
    pv_sensor = None
    sensor_ready = False

last_upload = 0.0

def charge_open():  GPIO.output(CHARGE_PIN, GPIO.LOW)
def charge_close(): GPIO.output(CHARGE_PIN, GPIO.HIGH)
def load_on():      GPIO.output(LOAD_PIN, GPIO.HIGH)
def load_off():     GPIO.output(LOAD_PIN, GPIO.LOW)
def aux_on():       GPIO.output(AUX_PIN, GPIO.HIGH)
def aux_off():      GPIO.output(AUX_PIN, GPIO.LOW)

def read_voltage_sensor(sensor):
    """Read the bus voltage from an INA219 sensor."""
    if sensor is None:
        return 0.0

    try:
        v = sensor.voltage()
        if v < V_MIN:
            return 0.0
        return v
    except Exception:
        return 0.0

def manage_load(v):
    # Smart-home rule: allow loads only when the battery has charge to spare.
    # Returns a numeric code (0/1/2) so it can be charted on ThingSpeak.
    if v >= V_LOAD_OK:
        load_on()
        return LOAD_ON     # 1

    if v < V_LOAD_CUT:
        load_off()
        return LOAD_OFF    # 0

    return LOAD_HOLD                   # 2 (between cut and ok: leave loads as they are)

def get_inputs():
    """Read the current solar forecast and current-hour load estimate."""
    generation = clearsky_solar_pred.get_power_output()
    load_profile = load.get_load_power()
    current_hour = datetime.datetime.now().strftime("%H:00")
    consumption = load_profile.get(current_hour, 0.0)
    return generation, consumption

def upload(v_bat, v_pv, status, load):
    """Upload battery voltage, PV voltage, controller state and relay state."""
    global last_upload

    if time() - last_upload < UPLOAD_INTVL:
        return

    params = {"api_key": API_KEY,
              "field1": round(v_bat, 3),
              "field2": round(v_pv, 3),
              "field3": status,
              "field4": load,
              }

    try:
        r = requests.get(TS_URL, params=params, timeout=8)

        if r.ok:
            last_upload = time()

    except requests.RequestException:
        pass

def ts():
    return datetime.datetime.now().strftime("%H:%M:%S")

print("Controller running. Ctrl+C to stop.")

def main():
    try:
        while True:
            charge_open()
            aux_off()
            sleep(0.5)

            v_bat = read_voltage_sensor(bat_sensor)
            v_pv = read_voltage_sensor(pv_sensor)
            generation, consumption = get_inputs()
            net_power = generation - consumption

            # Mock mode: uncomment below if no INA219 hardware is connected.
            # v_bat = float(input("Mock battery voltage (V): "))
            # v_pv = float(input("Mock PV voltage (V): "))

            load_state = manage_load(v_bat)
            now = ts()

            if v_bat >= V_FULL:
                print(f"[{now}] Vbat={v_bat:.3f}V Vpv={v_pv:.3f}V "
                      f"Generation={generation:.2f}W Load={consumption:.2f}W "
                      f"Net={net_power:.2f}W [Full/Standby] {LOAD_NAME[load_state]}")
                aux_off()
                upload(v_bat, v_pv, 2, load_state)
                sleep(INTERVAL)
                continue

            if v_bat < V_LOW:
                charge_close(); sleep(PROBE_DELAY)
                v_bat = read_voltage_sensor(bat_sensor)
                v_pv = read_voltage_sensor(pv_sensor)

                if v_pv <= V_MIN or net_power < MIN_POWER_THRESHOLD:
                    charge_open()
                    print(f"[{now}] Vbat={v_bat:.3f}V Vpv={v_pv:.3f}V "
                          f"Generation={generation:.2f}W Load={consumption:.2f}W "
                          f"Net={net_power:.2f}W [No Surplus/Standby] {LOAD_NAME[load_state]}")
                    aux_off()
                    upload(v_bat, v_pv, 0, load_state)
                    sleep(SLEEP_NOSUN)
                    continue

                aux_on()
                print(f"[{now}] Vbat={v_bat:.3f}V Vpv={v_pv:.3f}V "
                    f"Generation={generation:.2f}W Load={consumption:.2f}W "
                    f"Net={net_power:.2f}W [Charging] {LOAD_NAME[load_state]}")
                upload(v_bat, v_pv, 1, load_state)
                sleep(INTERVAL)
            else:
                print(f"[{now}] Vbat={v_bat:.3f}V Vpv={v_pv:.3f}V "
                    f"Generation={generation:.2f}W Load={consumption:.2f}W "
                    f"Net={net_power:.2f}W [Monitoring] {LOAD_NAME[load_state]}")
                upload(v_bat, v_pv, 3, load_state)
                sleep(INTERVAL)

    except KeyboardInterrupt:
        charge_open(); load_off(); aux_off(); GPIO.cleanup()
        print("Relays opened. Controller stopped.")

if __name__ == "__main__":
    main()