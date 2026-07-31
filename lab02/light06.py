from kasa import Discover, Device
import asyncio
import colorsys
import creds
from light06GSR import setUIColours, getUIColours, setUIHandler, waitForInput

lamp_config = None   # Saved lamp configuration for fast connection

async def getLampConfig():
  global lamp_config
  light_ip = creds.ip_bulb
  username = creds.username
  password = creds.password
  dev = await Discover.discover_single(light_ip, username=username, password=password)
  await dev.update()
  lamp_config = dev.config.to_dict()
  await dev.disconnect()

async def lampConnect():
  global lamp_config
  dev = await Device.connect(config=Device.Config.from_dict(lamp_config))
  return dev

async def turnLampOn():
  dev = await lampConnect()
  await dev.set_brightness(0)
  await dev.turn_on()
  await dev.disconnect()

async def turnLampOff():
  dev = await lampConnect()
  await dev.turn_off()
  await dev.disconnect()

async def setLampHSV(hue, saturation, value):
  # hue 0..360, saturation 0..100, value 1..100
  dev = await lampConnect()
  await dev.set_hsv(hue, saturation, value)
  await dev.disconnect()

async def setLampBrightness(bright):
  # bright 0 .. 100
  dev = await lampConnect()
  await dev.set_brightness(bright)
  await dev.disconnect()

def setLampRGB(r, g, b):
    # Conversion routine expects r, g, b to each be in the range 0..1
    # It produces h(hue), s(saturation), v(value). h and s each in range 0..1
    # Value is the brightness, zero being black and one being full intensity
    h, s, v = colorsys.rgb_to_hsv(r / 100, g / 100, b / 100)
    # HSV values for lamp must be integers (0..360, 0..100, 1..100)
    if v == 0:     # value not allowed to be zero, but brightness can be
      asyncio.run(setLampBrightness(0))
    else:
      asyncio.run(setLampHSV(int(h * 360), int(s * 100), int(v * 100)))

# Program starts here (although import may have already displayed UI)
asyncio.run(getLampConfig())       # Get and save lamp configuration
asyncio.run(turnLampOn())          # Turn lamp on with brightness zero
setUIHandler(setLampRGB)           # Connect colour change handler to UI
setUIColours(0, 100, 0)            # Initialise UI to green colour
waitForInput()                     # Main loop for UI - run until UI completion
asyncio.run(turnLampOff())         # Tidy up by turning lamp off
