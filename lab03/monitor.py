# monitor.py — Lab 3: solar monitoring + ThingSpeak upload
# Platform: Raspberry Pi 4B, OS Bookworm, Python 3.11, kernel 6.1
# Note: download from Moodle to avoid PDF line-wrap errors.
from ina219 import INA219
import RPi.GPIO as GPIO
from time import sleep, time
import requests
import creds

RELAY_PIN = 18
API_KEY = creds.API_KEY
TS_URL = "https://api.thingspeak.com/update"
UPLOAD_INTVL = 15  # s: ThingSpeak free-tier minimum

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
# Change RELAY_STATE to complete the Observation Table
# GPIO.HIGH = Relay Closed GPIO.LOW = Relay Open
RELAY_STATE = GPIO.LOW
GPIO.output(RELAY_PIN, RELAY_STATE)
state_str = "CLOSED" if RELAY_STATE == GPIO.HIGH else "OPEN"
ina = INA219(shunt_ohms=0.1, max_expected_amps=3.0, busnum=1, address=0x40)
ina.reset()
ina.configure(
    voltage_range=ina.RANGE_32V,
    gain=ina.GAIN_AUTO,
    bus_adc=ina.ADC_4SAMP,
    shunt_adc=ina.ADC_4SAMP,
)
last_upload = 0.0


def upload(v, i, p):
    global last_upload

    if time() - last_upload < UPLOAD_INTVL:
        return

    params = {
        "api_key": API_KEY,
        "field1": round(v, 3),
        "field2": round(i, 1),
        "field3": round(p, 4),
    }

    try:
        r = requests.get(TS_URL, params=params, timeout=8)

        if r.ok:
            last_upload = time()

    except requests.RequestException:
        pass

    print(f"Monitoring. Relay: {state_str}. Ctrl+C to stop.")

    try:
        while True:
            v = ina.voltage()
            i = ina.current()
            p = v * (i / 1000.0)
            print(f"Relay:{state_str} | V={v:.3f}V | I={i:.1f}mA | P={p:.4f}W")
            upload(v, i, p)
            sleep(0.5)
    except KeyboardInterrupt:
        GPIO.output(RELAY_PIN, GPIO.LOW)
        GPIO.cleanup()
        print("Relay opened safely.")
