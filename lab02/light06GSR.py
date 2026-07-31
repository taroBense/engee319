import speech_recognition
from subprocess import call

# Module to use Google Speech Recognition for colour setting

# Global variables to hold the current colour values
red = 0
green = 0
blue = 0
changeHandler = None

# Update function to be called when colour values may have changed
def updateColours():
    global red, green, blue
    global changeHandler
    if red < 0:     red = 0
    if red > 100:   red = 100
    if green < 0:   green = 0
    if green > 100: green = 100
    if blue < 0:    blue = 0
    if blue > 100:  blue = 100
    text = "set R G B to " + str(red) + " " + str(green) + " " + str(blue)
    call(["espeak", "-s200 -ven -z", text])

    # Call change handler if registered
    if changeHandler:
      changeHandler(red, green, blue)

# Functions to set and get colour values
def setUIColours(r, g, b):
  global red, blue, green
  red = r
  blue = b
  green = g
  updateColours()

def getUIColours():
  global red, blue, green
  return [red, green, blue]

# Function to set change handler
def setUIHandler(h):
  global changeHandler
  changeHandler = h;

# Google Speech Recognition User Interface

def listen():
  with speech_recognition.Microphone(device_index = 0) as source:
    reco.adjust_for_ambient_noise(source)
    print("Say something")
    audio = reco.listen(source)
    print("... got it")
  return audio

def recognize(audio):
  try:
    text = reco.recognize_google(audio)
    print("You said: ", text)
    return text
  except speech_recognition.UnknownValueError:
    print("Unknown value error")
    return ""
  except speech_recognition.RequestError:
    print("Request error")
    return ""

def processMessage(text):
  global red, green, blue
  heardRed = False
  for word in text.split():
    if word == 'blue':
      heardRed = True
    if word == 'more':
      if heardRed:
        red = red + 10
        updateColours()
    if word == 'less':
      if heardRed:
        red = red - 10
        updateColours()

def waitForInput():
  while True:
    audio = listen()
    text = recognize(audio)
    processMessage(text)
    if text.find('exit') >= 0:
      print("Stopping")
      return

# Start with GUI set correctly
updateColours()
reco = speech_recognition.Recognizer()
