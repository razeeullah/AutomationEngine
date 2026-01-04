import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")
if not api_key:
    print("Error: ELEVENLABS_API_KEY not found in .env")
else:
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": api_key}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        voices_data = response.json()
        print("ElevenLabs Connection Successful!")
        print(f"Number of available voices: {len(voices_data.get('voices', []))}")
    else:
        print(f"Error connecting to ElevenLabs: {response.status_code} - {response.text}")
