import datetime
import requests
import RPi.GPIO as GPIO
from time import sleep, time
from ina219 import INA219
import time
# user modules
import clearsky_solar_pred
import load

try:
    import creds
except ImportError:
    creds = None

MIN_POWER_THRESHOLD = 1

# —— Thresholds (NiMH 7S: 6 x 1.4V, 6 x 1.2V nominal = 8.4V) ——
V_FULL       = 8.6    # V: stop charging at/above this (battery full)
V_LOW        = 7.2    # V: attempt to charge below this (nominal)
V_LOAD_OK    = 7.2    # V: loads allowed at/above this
V_LOAD_CUT   = 7      # V: loads cut off below this (protect battery)
V_MIN        = 0.5    # V: minimum valid voltage reading from ADC

# 3 optocoupler outputs
BAT_PIN      = 18     # BCM 18 = Optocoupler 1 (charge control)
LOAD_PIN     = 23     # BCM 23 = Optocoupler 2 (load control)

# 2 INA219 I2C sensors
PV_SENSOR_ADDR = 0x40
BAT_SENSOR_ADDR = 0x41

INTERVAL     = 5.0    # s: normal loop period
FORECAST_HOURS = 48     # Number of future hourly net-power values to use

API_KEY      = creds.API_KEY if creds else ""
TS_URL       = "https://api.thingspeak.com/update"
UPLOAD_INTVL = 15     # s: ThingSpeak free-tier minimum

# Load status codes (numeric, so ThingSpeak field5 can chart them)
LOAD_OFF, LOAD_ON, LOAD_HOLD = 0, 1, 2
LOAD_NAME = {LOAD_OFF: "LOAD_OFF", LOAD_ON: "LOAD_ON", LOAD_HOLD: "LOAD_HOLD"}

# —— Hardware init ————————————————————————————
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(BAT_PIN, GPIO.OUT)
GPIO.setup(LOAD_PIN, GPIO.OUT)
GPIO.output(BAT_PIN, GPIO.LOW)
GPIO.output(LOAD_PIN, GPIO.LOW)

# INA219 voltage/current monitors
def configure_sensor(address):
    try:
        sensor = INA219(shunt_ohms=0.1, max_expected_amps=3.0,
                        busnum=1, address=address)
        sensor.reset()
        sensor.configure(
            voltage_range=sensor.RANGE_32V,
            gain=sensor.GAIN_AUTO,
            bus_adc=sensor.ADC_4SAMP,
            shunt_adc=sensor.ADC_4SAMP,
        )
        return sensor
    except Exception as exc:
        print(f"INA219 {address:#x} unavailable: {exc}")
        return None


pv_sensor = configure_sensor(PV_SENSOR_ADDR)
bat_sensor = configure_sensor(BAT_SENSOR_ADDR)

last_upload = 0.0

def bat_on():  GPIO.output(BAT_PIN, GPIO.LOW)
def bat_off(): GPIO.output(BAT_PIN, GPIO.HIGH)
def load_on():      GPIO.output(LOAD_PIN, GPIO.HIGH)
def load_off():     GPIO.output(LOAD_PIN, GPIO.LOW)

def read_ina_sensor(sensor):
    if sensor is None:
        return 0.0, 0.0

    try:
        v = sensor.voltage()
        i = sensor.current()
        if v < V_MIN:
            return 0.0, 0.0
        return v, i
    except Exception:
        return 0.0, 0.0


def read_power(sensor):
    """Return voltage, current, and power measured by an INA219."""
    voltage, current = read_ina_sensor(sensor)
    return voltage, current, max(0.0, voltage * current)

def manage_load(v_bat):
    """Protect the battery while allowing loads above the low-voltage limit."""
    if v_bat >= V_LOAD_OK:
        load_on()
        return LOAD_ON

    if v_bat < V_LOAD_CUT:
        load_off()
        return LOAD_OFF

    return LOAD_HOLD

def get_inputs(hours=FORECAST_HOURS):
    """Return current PV forecast, load, and net power over the next hours."""
    now = datetime.datetime.now().astimezone()
    load_profile = load.get_load_power()
    generation = clearsky_solar_pred.get_power_output(now)
    consumption = load_profile.get(now.strftime("%H:00"), 0.0)

    net_power = []
    for hour in range(hours):
        timestamp = now + datetime.timedelta(hours=hour)
        solar = clearsky_solar_pred.get_power_output(timestamp)
        demand = load_profile.get(timestamp.strftime("%H:00"), 0.0)
        net_power.append(solar - demand)

    return generation, consumption, net_power


def choose_battery_state(net_power, v_bat):
    """Implement the new controller table and full-battery isolation rule."""
    if v_bat >= V_FULL:
        return "ISOLATED"
    if any(power < -MIN_POWER_THRESHOLD for power in net_power):
        return "IN_USE"
    if any(power >= MIN_POWER_THRESHOLD for power in net_power):
        return "CHARGING"
    return "IN_USE"


def apply_battery_state(state):
    if state == "ISOLATED":
        bat_off()
    else:
        bat_on()

def upload(params, status, load_state):
    """Upload measured voltages, controller state, and load state."""
    global last_upload

    if not API_KEY or time() - last_upload < UPLOAD_INTVL:
        return

    params = {
        "api_key": API_KEY,
        "field1": round(params['v_bat'], 3),
        "field2": round(params['v_pv'], 3),
        "field3": status,
        "field4": load_state,
    }

    try:
        r = requests.get(TS_URL, params=params, timeout=8)

        if r.ok:
            last_upload = time()

    except requests.RequestException:
        pass

def ts():
    return datetime.datetime.now().strftime("%H:%M:%S")

def main():
    try:
        while True:
            v_pv, i_pv, pv_power = read_power(pv_sensor)
            v_bat, i_bat, bat_power = read_power(bat_sensor)
            generation, consumption, net_power = get_inputs()
            battery_state = choose_battery_state(net_power, v_bat)
            apply_battery_state(battery_state)
            load_state = manage_load(v_bat)

            now = ts()
            print(
                f"[{now}] PV={v_pv:.3f}V/{i_pv:.3f}A ({pv_power:.2f}W) "
                f"Battery={v_bat:.3f}V/{i_bat:.3f}A ({bat_power:.2f}W) "
                f"Forecast net={sum(net_power):.2f}W "
                f"[{battery_state}] {LOAD_NAME[load_state]}"
            )
            upload({"v_bat": v_bat, "v_pv": v_pv}, battery_state, load_state)
            sleep(INTERVAL)

    except KeyboardInterrupt:
        print("Exiting...")
        bat_off()
        load_off()
        GPIO.cleanup()


    if __name__ == "__main__":
        main()
