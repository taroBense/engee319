from pocketsphinx import LiveSpeech

for speech in LiveSpeech(
  sampling_rate=16000,
  kws='keyphrases.kws',
  kws_threshold=1e-50
  ):
  for alt in speech:
    print(alt.segments(detailed=True))
    print('Result is ', alt)
    if str(alt).strip() == 'exit':
      print("Stopping")
      exit()