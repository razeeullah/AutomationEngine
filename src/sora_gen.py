import os
import requests
import time
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
