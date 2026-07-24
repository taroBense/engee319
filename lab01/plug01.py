from kasa import Discover
import asyncio

async def main():
  devs = await Discover.discover()
  print('Discovered ', len(devs), ' devices')
  for dev in devs:
    print(dev)

asyncio.run(main())