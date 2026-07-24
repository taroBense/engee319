from kasa import Discover
import asyncio

async def main():
  dev = await Discover.discover_single('10.1.1.176')
  await dev.turn_on()
  await asyncio.sleep(1)
  await dev.turn_off()

asyncio.run(main())
