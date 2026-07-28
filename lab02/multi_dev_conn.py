import time
import asyncio
from kasa import Discover

def map_range(value, in_min, in_max, out_min, out_max):
  # Clamp input to min/max range
  clamped = max(in_min, min(value, in_max))
  # Scale linearly
  return out_min + (clamped - in_min) * (out_max - out_min) / (in_max - in_min)

async def main():
  try:
    user = ""
    pswd = ""
    bulb_ip = "192.168.1.94"
    plug_ip = "192.168.1.92"

    dev_plug = await Discover.discover_single(plug_ip,
      username=user,
      password=pswd)
    dev_bulb = await Discover.discover_single(bulb_ip,
      username=user,
      password=pswd)

    await dev_plug.update()
    await dev_bulb.update()

    print(f"Connected to {dev_plug.alias} at {dev_plug.host}")
    print(f"Connected to {dev_bulb.alias} at {dev_bulb.host}")

  except Exception as e:
    print(f"Error {e}")
    return 0

  while True:
    try:
      # Initial updates
      await dev_bulb.update()
      await dev_plug.update()

      # Initialise device modules
      plug_energy = dev_plug.modules.get("Energy")
      light_module = dev_bulb.modules.get("Light")

      # Set plug variables
      voltage = plug_energy.voltage
      current = plug_energy.current
      power = voltage * current
      print(f"{voltage:.2f} V\t{current:.2f} A\t{power:.2f} W")

      # Power scale HSV hue 0 -> 145 == red -> green
      # Set value based on power consumption
      # Setup mapping function to scale power consumption to hues
      hue = int(map_range(power, 0, 200, 0, 95))
      print(f"Power: {power:.2f} W\tSet Hue: {hue}")
      await light_module.set_hsv(hue, 100, 100)

      await asyncio.sleep(5)

    except asyncio.CancelledError as e:
      print(f"Error: {e}\nExiting...")

      await dev_bulb.disconnect()
      await dev_plug.disconnect()

      break

    except Exception as e:
      print(f"Unexpected Error: {e}")
      await asyncio.sleep(10)

if __name__ == "__main__":
  asyncio.run(main())
