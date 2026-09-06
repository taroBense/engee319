import json
import tkinter as tk
import paho.mqtt.client as mqtt

BROKER_IP = "broker.hivemq.com"  #  broker IP
TOPIC = "solar/status/waikato112233"

# --- 1. GUI Initialize ---
root = tk.Tk()
root.title("Solar Status Dashboard")

# Make it full screen for a clean touchscreen interface
root.attributes('-fullscreen', True) 
root.configure(bg='#121212') # Dark background to save power/eyes

# High-visibility fonts for small displays
TITLE_FONT = ("Helvetica", 24, "bold")
LABEL_FONT = ("Helvetica", 18, "bold")
VALUE_FONT = ("Helvetica", 18)

# Thread-safe variables to hold live UI updates
telemetry = {
    "pv_voltage": tk.StringVar(value="0.0 V"),
    "pv_current": tk.StringVar(value="0.0 A"),
    "pv_power": tk.StringVar(value="0.0 W"),
    "battery_voltage": tk.StringVar(value="0.0 V"),
    "load_power": tk.StringVar(value="0.0 W")
}

# --- 2. Layout Design ---
def build_dashboard():
    # Header
    title = tk.Label(root, text="SOLAR POWER SYSTEMS", font=TITLE_FONT, fg="#FFFFFF", bg="#121212")
    title.pack(pady=30)
    
    # Grid Container for Alignment
    grid_frame = tk.Frame(root, bg="#121212")
    grid_frame.pack(expand=True)
    
    metrics = [
        ("PV Voltage:", telemetry["pv_voltage"], "#00FFCC"),
        ("PV Current:", telemetry["pv_current"], "#00FFCC"),
        ("PV Power:", telemetry["pv_power"], "#FFB300"),
        ("Battery Voltage:", telemetry["battery_voltage"], "#FF3366"),
        ("Load Power:", telemetry["load_power"], "#FFFF33")
    ]
    
    for row_idx, (name, string_var, color) in enumerate(metrics):
        # Data Field Labels
        lbl = tk.Label(grid_frame, text=name, font=LABEL_FONT, fg="#AAAAAA", bg="#121212", anchor="w")
        lbl.grid(row=row_idx, column=0, padx=30, pady=12, sticky="w")
        
        # Live Numerical Values
        val = tk.Label(grid_frame, textvariable=string_var, font=VALUE_FONT, fg=color, bg="#121212", anchor="e")
        val.grid(row=row_idx, column=1, padx=30, pady=12, sticky="e")
        
    # Touch-friendly close button so you aren't trapped in full screen
    btn_close = tk.Button(root, text="× Close App", command=root.destroy, font=("Helvetica", 12), fg="#FFFFFF", bg="#333333", borderwidth=0, padx=10, pady=5)
    btn_close.pack(side="bottom", anchor="s", pady=20)

# --- 3. UI Update Engine ---
def safe_ui_update(data):
    """Safely updates Tkinter variables from the background MQTT thread"""
    if "pv_voltage" in data: telemetry["pv_voltage"].set(f"{data['pv_voltage']} V")
    if "pv_current" in data: telemetry["pv_current"].set(f"{data['pv_current']} A")
    if "pv_power" in data: telemetry["pv_power"].set(f"{data['pv_power']} W")
    if "battery_voltage" in data: telemetry["battery_voltage"].set(f"{data['battery_voltage']} V")
    if "load_power" in data: telemetry["load_power"].set(f"{data['load_power']} W")

# --- 4. MQTT Network Callbacks ---
def on_connect(client, userdata, flags, reason_code, properties=None):
    print("Connected to telemetry stream.")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        
        # Schedule the UI update on Tkinter's main loop thread
        root.after(0, safe_ui_update, data)
    except Exception as e:
        print("Parser error:", e)

# --- 5. Main Execution ---
build_dashboard()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_IP, 1883, 60)
client.loop_start()  # Starts network loop in the background thread

try:
    root.mainloop()  # Keeps GUI active on the primary thread
finally:
    client.loop_stop()  # Cleanly kills network thread when window closes
