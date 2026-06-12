# test_qwen.py
# This script tests that we can call the Qwen AI model on HuggingFace

# Step 1: Import the libraries we need
import os                          # lets us read environment variables
from dotenv import load_dotenv     # reads our .env file
from huggingface_hub import InferenceClient  # connects to HuggingFace

# Step 2: Load the secret token from our .env file
load_dotenv()
token = os.getenv("HUGGINGFACE_API_TOKEN")
print("Token loaded:", token is not None)
print("Token value:", token[:10] if token else "None")
# Step 3: Create a connection to the Qwen model
# Think of this like dialing a phone number to reach the AI
client = InferenceClient(
    model="Qwen/Qwen2.5-72B-Instruct",  # the AI model we want to use
    token=token                           # our password to access it
)

# Step 4: Send a message to the AI and get a response
# messages is a list of turns in the conversation
# role "user" means we are asking the question
# role "assistant" would mean the AI's previous responses
response = client.chat_completion(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant for Karnataka State Police."
        },
        {
            "role": "user",
            "content": "What is your role in the KSP Crime Intelligence Platform?"
        }
    ],
    max_tokens=200   # maximum length of the response
)

# Step 5: Extract and print the text response
# response.choices[0].message.content is where HuggingFace puts the AI's answer
answer = response.choices[0].message.content
print("AI Response:")
print(answer)
print("\nTest passed! The Qwen API is working correctly.")