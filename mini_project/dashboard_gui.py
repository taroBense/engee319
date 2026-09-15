import tkinter as tk
from tkinter import messagebox, ttk
import asyncio
from kasa import Discover, Device

root = tk.Tk()
root.title("Device Control Dashboard")
root.geometry("1920x1080")
root.attributes('-fullscreen', True)

device_frame = ttk.LabelFrame(root, text="Devices")
device_frame.pack(pady=20)

add_device_button = tk.Button(root, text="Add Device", command=lambda: messagebox.showinfo("Info", "Add Device functionality not implemented yet."))
add_device_button.pack(pady=10)

quit_button = tk.Button(root, text="Quit", command=root.quit)
quit_button.pack(pady=10)

class Device:
    def __init__(self, name, row):
        self.name = name
        self.row = row
        self.status = tk.StringVar(value="OFF")
        self.create_widgets()

    def create_widgets(self):
        # Create a label for the device name
        self.label = tk.Label(device_frame, text=self.name)
        self.label.grid(row=self.row, column=0, padx=10, pady=5)

        # Create a button to toggle the device status
        self.toggle_button = tk.Button(
            device_frame, textvariable=self.status, command=self.toggle_status
        )
        self.toggle_button.grid(row=self.row, column=1, padx=10, pady=5)

    def toggle_status(self):
        if self.status.get() == "OFF":
            self.status.set("ON")
        else:
            self.status.set("OFF")

async def connect_to_device(device):
    # Simulate an asynchronous connection to the device
    await asyncio.sleep(1)  # Simulate network delay
    print(f"Connected to {device.name}")

# Create instances of Device for each device
devices = [
    Device("Device 1", 0),
    Device("Device 2", 1),
    Device("Device 3", 2)
]

root.mainloop()

