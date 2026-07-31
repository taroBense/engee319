from geminiENGEE319 import set_instructions, ask_gemini_keep_history

my_instructions = """
	I have a lamp which can be set by giving hue saturation and value levels
	with hue between 0-255 and hue and saturation beettween 0-100.
	I will write descriptions of colours and you should respond in the 
	format \"h s v\" substituting appropriate values for 
	the numbers in my format. Don't add any extra text
"""

set_instructions(my_instructions)
while True:
	# Read text from the keyboard
	my_input_text = input("You: ")
	if my_input_text == "exit":
		break
	# Send it to gemini and print the response	
	answer = ask_gemini_keep_history(my_input_text)
	print("Gemini: ", answer)
	
