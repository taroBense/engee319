import speech_recognition
import tkinter
import threading
from tkinter import PhotoImage
from tkinter.ttk import *
from subprocess import call
from geminiENGEE319 import set_instructions, ask_gemini_keep_history

# Module to use Google Speech Recognition for colour setting

# Global variables to hold the current colour values
red = 0
green = 0
blue = 0
changeHandler = None
b_recording = False

MY_INSTRUCTIONS = """
    I have a lamp which can be set by giving red green and blue light levels
    as numbers between 0 and 255, where 0 is dark and 255 is brightest.
    I will write descriptions of colours and you should respond in the 
    format "100,100,100" substituting appropriate values for 
    the numbers in my format. Don't add any extra text.
"""
set_instructions(MY_INSTRUCTIONS)

# Update function to be called when colour values may have changed
def updateColours():
    global red, green, blue
    global changeHandler

    red = max(0, min(255, red))
    green = max(0, min(255, green))
    blue = max(0, min(255, blue))

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

  if not text.strip():
    return

  answer = ask_gemini_keep_history(text)

  print(f"Gemini output: {answer}")

  try:
    rgb_vals = [int(colour.strip()) for colour in answer.split(",")]
    if len(rgb_vals) == 3:
      red, green, blue = rgb_vals
      updateColours()
    else:
      print("Received invalid RGB tuple structure from Gemini.")
  except ValueError:
    print("Could not parse integer RGB values from Gemini output.")

def waitForInput():
  global b_recording

  while b_recording:
    audio = listen()

    if audio:
      text = recognize(audio)

    print(f"I heard: {text}")

    if 'exit' in text:
      print("Stopping")
      b_recording = False
      break

    processMessage(text)

def on_click():
  global b_recording

  if not b_recording:
    b_recording = True
    print("Starting recording...")
    threading.Thread(target=waitForInput, daemon=True).start()
  else:
    print("Stopping recording...")
    b_recording = False

# Start with GUI set correctly
updateColours()
reco = speech_recognition.Recognizer()


# build GUI here:
# main window
window = tkinter.Tk()

mic = PhotoImage(file="mic.png")
mic = mic.subsample(10, 10)

# frames, top and bottom
input_frame = tkinter.Frame(window)
input_frame.pack(side="top")
output_frame = tkinter.Frame(window)
output_frame.pack(side="bottom")

# input frame content
instruction_label = tkinter.Label(input_frame,
    text="Press buttton to record:")
instruction_label.pack(side="top")

record_button = tkinter.Button(input_frame,
    text="Record",
    image=mic,
    compound="left"
    )
record_button.pack(side="bottom")

record_button.image = mic

# output frame content
bulb_label = tkinter.Label(output_frame,
    text=f"bulb colour: {[r, g, b]}")
bulb_label.pack(side="bottom")

# generate GUI
window.mainloop()