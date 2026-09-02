import datetime, requests
import RPi.GPIO as GPIO
from time import sleep, time
from ina219 import INA219
# user modules
import creds
import clearsky_solar_pred
import load

# input and output data from solar prediction and load modules
generation = clearsky_solar_pred.get_power_output()
consumption = load.get_load_power()

# —— Thresholds (NiMH 7S: 6 x 1.4V, 6 x 1.2V nominal = 8.4V) ——
V_FULL       = 8.6    # V: stop charging at/above this (battery full)
V_LOW        = 7.2    # V: attempt to charge below this (nominal)
V_LOAD_OK    = 7.2    # V: loads allowed at/above this
V_LOAD_CUT   = 7   # V: loads cut off below this (protect battery)
I_MIN        = 10.0   # mA: below this means no usable solar

CHARGE_PIN   = 18     # BCM 18 = Relay 1 (charge control)
LOAD_PIN     = 23     # BCM 23 = Relay 2 (load control)
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
GPIO.output(CHARGE_PIN, GPIO.LOW)   # charge relay OPEN on startup (safe)
GPIO.output(LOAD_PIN, GPIO.LOW)   # load relay OPEN on startup (safe)

ina = INA219(shunt_ohms=0.1, max_expected_amps=3.0, busnum=1, address=0x40)
ina.reset()
ina.configure(voltage_range=ina.RANGE_32V, gain=ina.GAIN_AUTO,
              bus_adc=ina.ADC_4SAMP, shunt_adc=ina.ADC_4SAMP)
last_upload = 0.0

def charge_open():  GPIO.output(CHARGE_PIN, GPIO.LOW)
def charge_close(): GPIO.output(CHARGE_PIN, GPIO.HIGH)
def load_on():      GPIO.output(LOAD_PIN, GPIO.HIGH)
def load_off():     GPIO.output(LOAD_PIN, GPIO.LOW)

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

def upload(v, i, p, status, load):
    # status (field4) and load (field5) are both numeric codes.
    global last_upload

    if time() - last_upload < UPLOAD_INTVL:
        return

    params = {"api_key": API_KEY,
              "field1": round(v, 3),
              "field2": round(i, 1),
              "field3": round(p, 4),
              "field4": status,
              "field5": load
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
            charge_open(); sleep(0.5)
            v_bat = ina.voltage()
            # Mock mode: comment out the line above, uncomment below for testing.
            # v_bat = float(input("Mock voltage (V): "))
            load = manage_load(v_bat)            # numeric load decision every loop
            now = ts()

            if v_bat >= V_FULL:
                print(f"[{now}] V={v_bat:.3f}V [Full/Standby] {LOAD_NAME[load]}")
                upload(v_bat, 0, 0, 2, load); sleep(INTERVAL); continue

            if v_bat < V_LOW:
                charge_close(); sleep(PROBE_DELAY)
                v = ina.voltage(); i = ina.current(); p = v * (i / 1000)
                if i < I_MIN:
                    charge_open()
                    print(f"[{now}] V={v:.3f}V I={i:.1f}mA [No Sun/Standby] {LOAD_NAME[load]}")
                    upload(v, i, p, 0, load); sleep(SLEEP_NOSUN); continue
                print(f"[{now}] V={v:.3f}V I={i:.1f}mA P={p:.4f}W [Charging] {LOAD_NAME[load]}")
                upload(v, i, p, 1, load); sleep(INTERVAL)
            else:
                print(f"[{now}] V={v_bat:.3f}V [Monitoring] {LOAD_NAME[load]}")
                upload(v_bat, 0, 0, 3, load); sleep(INTERVAL)

    except KeyboardInterrupt:
        charge_open(); load_off(); GPIO.cleanup()
        print("Relays opened. Controller stopped.")

if __name__ == "__main__":
    main()