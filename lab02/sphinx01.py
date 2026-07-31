from pocketsphinx import LiveSpeech

for phrase in LiveSpeech(sampling_rate=16000):
  print(phrase)
  if str(phrase).strip() == 'stop':
    print("Stopping")
    exit()