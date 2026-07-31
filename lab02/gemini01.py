from google import genai
from  google.genai import types
import creds
import os

# My general instructions to the AI model - this can be setting tone,
# style, etc. In this case I am telling it how to interpret the input
# and format the output. Note the use of triple quotes to allow a 
# multi-line string

my_instructions = """
	I have a lamp which can be set by giving hue saturation and value levels
	with hue between 0-255 and hue and saturation beettween 0-100.
	I will write descriptions of colours and you should respond in the 
	format \"h s v\" substituting appropriate values for 
	the numbers in my format. Don't add any extra text
"""

client = genai.Client(api_key=creds.api_key)
model = "gemini-3.1-flash-lite"
config = types.GenerateContentConfig(
			temperature=0,
			thinking_config = types.ThinkingConfig(thinking_budget=-1),
			safety_settings=[
			  types.SafetySetting(
			      category="HARM_CATEGORY_HARASSMENT",
			      threshold="BLOCK_LOW_AND_ABOVE",	# Block most
			  ),
			  types.SafetySetting(
			      category="HARM_CATEGORY_HATE_SPEECH",
			      threshold="BLOCK_LOW_AND_ABOVE",	# Block most
			  ),
			  types.SafetySetting(
			      category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
			      threshold="BLOCK_LOW_AND_ABOVE",	# Block most
			  ),
			  types.SafetySetting(
			      category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
			      threshold="BLOCK_LOW_AND_ABOVE",	# Block most
			  )

			],
			# tools=[types.Tool(googleSearch=types.GoogleSearch())],

			system_instruction=[types.Part.from_text(text=my_instructions)])

while True:
	my_input_text=input("You: ")

	if my_input_text == "exit":
		break

	contents = [types.Content (role="user",
					parts=[types.Part.from_text(text=my_input_text)])]
	response = client.models.generate_content(model=model, 
					contents=contents, config=config)
	# response = client.models.generate_content(model=model, 
	# 				contents=contents)
					
	print("Gemini: ", response.text)