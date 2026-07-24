from kasa import Discover
import asyncio
import creds
import time

async def main():
  start_time = time.time()
  dev = await Discover.discover_single(f"{creds.ip_add}")
  await dev.update()

  if not dev.has_emeter:
    print('Device can not report energy usage')
    return    # this just breaks out of main loop, returns None
  
  e_module = dev.modules.get("Energy")
  voltage = []
  current = []
  power = []
  watt_hours_plt = {}

  while True:
    await asyncio.sleep(1)
    await dev.update()

    end_time = time.time()
    delta_time = end_time - start_time

    watt_hours += ( e_module.voltage * e_module.current ) * ( delta_time / 3600 )
    
    print(f"{e_module.current} A @ {e_module.voltage} V\n{e_module.voltage*e_module.current} W\t{watt_hours} Wh")

    voltage.append(e_module.voltage)
    current.append(e_module.current)
    watt_hours_plt.append(watt_hours)

if __name__ == "__main__":
  asyncio.run(main())