import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def generate_script(topic, api_key=None):
    """
    Generates a 60-second YouTube script for a specific topic.
    """
    if api_key:
        genai.configure(api_key=api_key)
    elif os.getenv("GEMINI_API_KEY"):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    else:
        raise ValueError("Gemini API Key not found.")

    model = genai.GenerativeModel('gemini-3-flash-preview')
    
    prompt = f"""
    Write a 60-second faceless YouTube script on "{topic}". 
    Include:
    1. A hook (first 3 seconds)
    2. 3 key points
    3. A call-to-action (subscribe, like, etc.)
    
    Target length: 200-400 words.
    Tone: Actionable, informative, and professional.
    Language: English.
    Return only the script text.
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()

if __name__ == "__main__":
    # Test
    try:
        test_script = generate_script("How to save $1000 in a month")
        print("Generated Script:")
        print(test_script)
    except Exception as e:
        print(f"Error: {e}")
