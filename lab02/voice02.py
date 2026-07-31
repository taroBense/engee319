from subprocess import call
import speech_recognition

reco = speech_recognition.Recognizer()
reco.pause_threshold = 1 # Changed from 2
# this value is likely the time limit it waits to 
# register the seperation between words

def listen():
  with speech_recognition.Microphone() as source:
    # likely the time it takes to measure bg noise
    reco.adjust_for_ambient_noise(source, duration=1)
    print("Say something")
    # timeout is recording length, 
    # phrase time limit is how long it registers strings of words to be correlated 
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
    return "Failed on unknown value error"
  except speech_recognition.RequestError:
    print("Request error")
    return "Failed on request error"

while True:
  audio = listen()
  text = recognize(audio)
  call(["espeak", "-s200 -ven -z", text])
  if text == "exit":
    print("Stopping")
    exit()