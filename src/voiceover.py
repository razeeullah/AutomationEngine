import os
import requests
from dotenv import load_dotenv

load_dotenv()

def generate_voiceover(text, output_path, voice_id="pNInz6obpgDQGcFmaJgB", api_key=None):
    """
    Converts text to speech using ElevenLabs API.
    Default voice_id is 'Adam' (Finance-style voice).
    """
    key = api_key or os.getenv("ELEVENLABS_API_KEY")
    if not key:
        raise ValueError("ElevenLabs API Key not found.")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": key
    }
    
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        return output_path
    else:
        raise Exception(f"ElevenLabs API Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    # Test
    try:
        sample_text = "Welcome to your daily finance update. Today we explore passive income."
        out = "outputs/audio/test_voice.mp3"
        generate_voiceover(sample_text, out)
        print(f"Voiceover saved to {out}")
    except Exception as e:
        print(f"Error: {e}")
