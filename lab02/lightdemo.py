from kasa import Discover
import asyncio
import creds

async def main():
  dev = await Discover.discover_single(creds.ip_add,
                  username=creds.username,
                  password=creds.password)

  # Print basic id information
  await dev.update()
  print(dev)

  # Turn the light on off on
  await dev.turn_on()
  await asyncio.sleep(1)
  await dev.turn_off()
  await asyncio.sleep(1)
  await dev.turn_on()
  await asyncio.sleep(1)

  # Get the 'Light' module for changing parameters
  light_module = dev.modules.get("Light")

  await light_module.set_brightness(10)
  await asyncio.sleep(1)
  await light_module.set_brightness(50)
  await asyncio.sleep(1)
  await light_module.set_brightness(100)
  await asyncio.sleep(1)

  # Set a starting colour value
  await light_module.set_hsv(0, 0, 100)
  await asyncio.sleep(1)

  # Display a range of colours
  for hue in range(0, 360, 36):
    await light_module.set_hsv(hue, 100, 100)
    await asyncio.sleep(1)

  # Set back to starting value
  await light_module.set_hsv(0, 0, 100)
  await asyncio.sleep(1)

  # Display the current colour
  await dev.update()
  hsv = light_module.hsv
  print("HSV: ", hsv.hue, ",", hsv.saturation, ",", hsv.value)

  # Shut down the interface to the light
  await dev.disconnect()
  return

asyncio.run(main())