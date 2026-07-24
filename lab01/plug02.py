from kasa import Discover
import asyncio

async def main():
  dev = await Discover.discover_single('10.1.1.176')
  print(dev)

asyncio.run(main())
