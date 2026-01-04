import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def generate_finance_topics(niche, num_topics=50, api_key=None):
    """
    Generates trending finance topics using Gemini AI.
    """
    if api_key:
        genai.configure(api_key=api_key)
    elif os.getenv("GEMINI_API_KEY"):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    else:
        raise ValueError("Gemini API Key not found.")

    model = genai.GenerativeModel('gemini-3-flash-preview')
    
    prompt = f"""
    Generate {num_topics} short YouTube video ideas for faceless finance content. 
    Focus on {niche}. 
    Make each title click-worthy, trending, and under 60 characters.
    Return the list as a plain text list, one topic per line.
    No introductory or concluding text.
    """
    
    response = model.generate_content(prompt)
    topics = response.text.strip().split('\n')
    # Filter out empty lines or numbered prefixes if any
    topics = [t.strip().lstrip('0123456789. ') for t in topics if t.strip()]
    
    return topics[:num_topics]

if __name__ == "__main__":
    # Test
    try:
        test_topics = generate_finance_topics("Passive Income", 5)
        print("Generated Topics:")
        for topic in test_topics:
            print(f"- {topic}")
    except Exception as e:
        print(f"Error: {e}")
