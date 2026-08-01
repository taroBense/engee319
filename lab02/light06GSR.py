import speech_recognition
from subprocess import call
from geminiENGEE319 import set_instructions, ask_gemini_keep_history

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

    # changeHandler(red, green, blue)

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
    reco.adjust_for_ambient_noise(source, duration=1)
    print("Say something")
    audio = reco.listen(source, timeout=5, phrase_time_limit=10)
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

  my_instructions = """
	I have a lamp which can be set by giving red green and blue light levels
	as numbers between 0 and 255, where 0 is dark and 255 is brightest.
	I will write descriptions of colours and you should respond in the 
	format \"100,100,100\" substituting appropriate values for 
	the numbers in my format. Don't add any extra text
  """

  set_instructions(my_instructions)

  answer = ask_gemini_keep_history(text)

  print(f"Gemini output: {answer}")

  answer = answer.split(",")

  red = int(answer[0])
  green = int(answer[1])
  blue = int(answer[2])

  updateColours()

def waitForInput():
  while True:
    audio = listen()
    text = recognize(audio)
    print(f"I heard: {text}")
    processMessage(text)
    if text.find('exit') >= 0:
      print("Stopping")
      return None

# Start with GUI set correctly
updateColours()
reco = speech_recognition.Recognizer()
