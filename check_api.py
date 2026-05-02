import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

def check_api_key():
    print("Loading environment variables...")
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[Error] OPENAI_API_KEY not found in .env file or environment.")
        sys.exit(1)
        
    print("Initializing OpenAI client...")
    client = OpenAI(api_key=api_key)
    
    try:
        print("Attempting to connect to OpenAI API...")
        # Send a prompt to the model and get a response
        print("Sending prompt to gpt-4o-mini...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! This is a test message. Please respond with a short greeting and confirm you received this."}
            ]
        )
        
        # If we get here, the request was successful
        print("\n[Success] The API key is valid and working.")
        print("\n--- Response from OpenAI ---")
        print(response.choices[0].message.content)
        print("----------------------------")
        
    except Exception as e:
        print("\n[Error] validating API key:")
        print(f"Exception details: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    check_api_key()
