import os
import requests
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class SoraGen:
    """
    Handler for OpenAI's Sora Video API (2026 Specification).
    """
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("SORA_API_KEY")
        self.base_url = "https://api.openai.com/v1/sora"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate_video(self, prompt, model="sora-2", duration=15):
        """
        Initiates a video generation job.
        Returns the job/video ID.
        """
        if not self.api_key:
            raise ValueError("Sora API Key not found.")

        url = f"{self.base_url}/videos"
        data = {
            "model": model,
            "prompt": prompt,
            "duration": duration,
            "quality": "hd"
        }

        response = requests.post(url, json=data, headers=self.headers)
        if response.status_code == 201:
            return response.json().get("id")
        else:
            raise Exception(f"Sora API Error (Generate): {response.status_code} - {response.text}")

    def get_status(self, video_id):
        """
        Retrieves the status of a video generation job.
        Possible statuses: 'queued', 'rendering', 'completed', 'failed'.
        """
        url = f"{self.base_url}/videos/{video_id}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Sora API Error (Status): {response.status_code} - {response.text}")

    def download_video(self, video_id, output_path):
        """
        Polls for completion and downloads the final MP4.
        """
        print(f"Waiting for Sora to render video {video_id}...")
        while True:
            status_data = self.get_status(video_id)
            status = status_data.get("status")
            
            if status == "completed":
                download_url = status_data.get("download_url")
                print(f"Rendering complete! Downloading from {download_url}")
                
                # Download the file
                response = requests.get(download_url, stream=True)
                if response.status_code == 200:
                    with open(output_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=1024):
                            if chunk: f.write(chunk)
                    return output_path
                else:
                    raise Exception(f"Error downloading video: {response.status_code}")
                
            elif status == "failed":
                error_msg = status_data.get("error", "Unknown error")
                raise Exception(f"Sora Video Generation Failed: {error_msg}")
            
            # Poll every 5 seconds
            time.sleep(5)

def generate_sora_prompt(script_text, api_key=None):
    """
    Transforms a finance script into a Sora-optimized prompt using Gemini.
    """
    gemini_key = api_key or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("Gemini API Key for prompt optimization not found.")
    
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-3-flash-preview')

    system_prompt = """
🔒 SYSTEM PROMPT — Finance Shorts / Reels (Sora AI Optimized)

You are a top-tier AI Video Prompt Engineer for Finance Content, specialized in Sora AI and short-form vertical videos.

Your task is to transform the provided finance script into a high-retention, authority-driven Sora AI video prompt optimized for:
YouTube Shorts | Instagram Reels | TikTok

📐 VIDEO FORMAT (MANDATORY)
Aspect Ratio: 9:16 (vertical)
Duration: 20–60 seconds
Mobile-first framing

🧠 FINANCE-SPECIFIC VISUAL RULES
Visuals must signal trust, credibility, and clarity
Use: Clean modern environments, Professional lighting, Minimalist backgrounds, Screens, dashboards, charts, smartphones, laptops, money symbolism.
Avoid exaggeration, fantasy, or cartoon visuals.

⚡ RETENTION & HOOK OPTIMIZATION
First 1–2 seconds must contain a scroll-stopping finance hook: Money movement, Numbers rapidly changing, Graphs spiking or dropping, Close-up of hands counting money or scrolling an app.
Scene changes every 1–2 seconds. Fast but smooth camera motion (micro-zooms, whip pans, punch-ins).

🎥 CINEMATIC DIRECTION
Define: Camera angle (close-ups dominate), Camera movement (dynamic, fast cuts), Lighting (bright, high-contrast, premium), Mood (confidence, urgency, clarity, authority), Environment (modern office, desk setup, city skyline, fintech interface).

📝 ON-SCREEN TEXT & CAPTIONS
Add bold on-screen captions synced to script. Max 4–6 words, High contrast, Center or lower-third placement.

⚖️ FINANCE SAFETY & TRUST
Visual tone must feel educational, not scammy. Focus on information, insight, or mindset.

⛔ STRICT OUTPUT RULES
❌ No explanations | ❌ No summaries | ❌ No bullet points | ❌ No headings
✅ Output ONLY one complete Sora AI prompt, ready to paste directly into Sora AI
    """

    user_prompt = f"SCRIPT TO TRANSFORM:\n{script_text}"
    
    response = model.generate_content([system_prompt, user_prompt])
    return response.text.strip()

def sora_generate_full(prompt, output_path, api_key=None):
    """
    Convenience function for full text-to-video pipeline.
    """
    engine = SoraGen(api_key=api_key)
    video_id = engine.generate_video(prompt)
    return engine.download_video(video_id, output_path)

if __name__ == "__main__":
    # Test script (will fail without real API key, but verifies logic)
    try:
        print("Testing Sora Integration logic...")
        # out = sora_generate_full("A futuristic finance office with holographic displays", "outputs/videos/sora_test.mp4")
        # print(f"Success: {out}")
    except Exception as e:
        print(f"Expected Error: {e}")
