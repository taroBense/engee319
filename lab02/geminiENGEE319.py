# To run this code you need to install the following dependencies:
# pip install google-genai

from google import genai
from google.genai import types
import creds

client = genai.Client(api_key=creds.api_key)

model = "gemini-3.1-flash-lite"

config = types.GenerateContentConfig(
            temperature=0,
            thinking_config = types.ThinkingConfig(thinking_budget=-1),
            safety_settings=[
              types.SafetySetting(
                  category="HARM_CATEGORY_HARASSMENT",
                  threshold="BLOCK_LOW_AND_ABOVE",  # Block most
              ),
              types.SafetySetting(
                  category="HARM_CATEGORY_HATE_SPEECH",
                  threshold="BLOCK_LOW_AND_ABOVE",  # Block most
              ),
              types.SafetySetting(
                  category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                  threshold="BLOCK_LOW_AND_ABOVE",  # Block most
              ),
              types.SafetySetting(
                  category="HARM_CATEGORY_DANGEROUS_CONTENT",
                  threshold="BLOCK_LOW_AND_ABOVE",  # Block most
              )
          ],
          # tools=[types.Tool(googleSearch=types.GoogleSearch())]
          )

def set_instructions(instructions):
  config.system_instruction = [types.Part.from_text(text=instructions)]

history = []

def ask_gemini(input_text):
  history = [(types.Content(role="user", parts=[types.Part.from_text(text=input_text)]))]
  response = client.models.generate_content(model=model, contents=history, config=config)
  return response.text

def ask_gemini_keep_history(input_text):
  history.append(types.Content(role="user", parts=[types.Part.from_text(text=input_text)]))
  response = client.models.generate_content(model=model, contents=history, config=config)
  history.append(types.Content(role="model", parts=[types.Part.from_text(text=response.text)]))
  return response.text