import os
import csv
import json
import time
from pymodbus.client import ModbusSerialClient
import paho.mqtt.client as mqtt

# 1. Setup the MQTT cloud broker and topic
BROKER_IP = "broker.hivemq.com"
TOPIC = "solar/status/waikato112233" 

mqtt_client = mqtt.Client()
mqtt_client.connect(BROKER_IP, 1883, 60)
mqtt_client.loop_start() # Run network traffic in the background

# 2. Set up the csv file to save the telemetry
CSV_FILE_PATH = "solar_telemetry.csv"

#3. Setup the Modbus Client for the COM-USB port
modbus_client = ModbusSerialClient(port='/dev/ttyACM0', baudrate=115200, bytesize=8, stopbits=1, parity='N', timeout=1)
modbus_inverter = ModbusSerialClient(port='/dev/ttyACM1', baudrate=115200, bytesize=8, stopbits=1, parity='N', timeout=1)

def read_u16(addr):
    rr = modbus_client.read_input_registers(address=addr, count=1, device_id=1)
    if not rr.isError():
        return rr.registers[0]
    return 0
    
def read_u32(addr):
    rr = modbus_client.read_input_registers(address=addr, count=2, device_id=1)
    if not rr.isError():
        low = rr.registers[0]
        high = rr.registers[1]
        return (high << 16) | low
    return 0
    
def read_inv16(addr):
    rr = modbus_inverter.read_input_registers(address=addr, count=1, device_id=3)
    if not rr.isError():
        return rr.registers[0]
    return 0
    
def read_inv32(addr):
    rr = modbus_inverter.read_input_registers(address=addr, count=2, device_id=3)
    if not rr.isError():
        low = rr.registers[0]
        high = rr.registers[1]
        return (high << 16) | low
    return 0
    
def get_solar_data():
    return {
        "pv_voltage": read_u16(0x3100) / 100,
        "pv_current": read_u16(0x3101) / 100, 
        "pv_power": read_u32(0x3102) / 100,
        "battery_voltage": read_u16(0x331A) / 100, 
        "battery_current": read_u32(0x331B) / 100, 
        "battery_temp": read_u16(0x3110) / 100,
        "load_voltage": read_inv16(0x310C) / 100, 
        "load_current": read_inv16(0x310D) / 100, 
        "load_power": read_inv32(0x310E) / 100,
        "daily_energy": read_u32(0x330C) * 10,
        "battery_soc": read_u16(0x311A),
        "timestamp": time.time()
    }

#4. Get the json payload
if modbus_client.connect():
    print("Connected to charge controller. Publishing to cloud...")
    try:
        while True:
            #a. Live data from MPPT controller 
            data = get_solar_data()
            
            #b. Log the data into csv file
            file_exists = os.path.isfile(CSV_FILE_PATH)
            try:
                with open(CSV_FILE_PATH, mode='a', newline='', encoding='utf-8') as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=data.keys())
                    if not file_exists:
                        writer.writeheader() # Writes the keys as headers only on first creation
                    writer.writerow(data)
            except Exception as e:
                print(f"Failed to write to CSV: {e}")
            
            #c. Publish data on MQTT broker
            payload = json.dumps(data)
            mqtt_client.publish(TOPIC, payload)
            print(f"Published: {payload}")
            
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nStopping publisher...")
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        modbus_client.close()
else:
    print("Can't connect to Modbus device")
