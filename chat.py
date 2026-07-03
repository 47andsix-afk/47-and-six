from google.genai import Client
import os

client = Client(api_key=os.getenv("GEMINI_API_KEY"))

print("Gemini 3.5 Flash Chat — type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=user_input
    )

    print("Gemini:", response.text, "\n")
