import os
import requests
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
from dotenv import load_dotenv

load_dotenv()

def fetch_stock_video(query, api_key=None, limit=1):
    """
    Fetches stock video URLs from Pexels API.
    """
    key = api_key or os.getenv("PEXELS_API_KEY")
    if not key:
        raise ValueError("Pexels API Key not found.")

    url = f"https://api.pexels.com/videos/search?query={query}&per_page={limit}"
    headers = {"Authorization": key}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['videos']:
            # Get the first video link (usually HD or SD)
            video_files = data['videos'][0]['video_files']
            # Try to find a vertical one or just the first high quality one
            return video_files[0]['link']
    return None

def download_file(url, output_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return output_path
    return None

def create_video(audio_path, video_save_path, keywords=None):
    """
    Combines audio with stock footage to create a final video.
    """
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    
    # Use a set of keywords or repeat the primary one
    search_queries = keywords if keywords else ["finance", "money", "growth", "savings"]
    
    clips = []
    current_duration = 0
    
    # We want to fill the duration with multiple clips of ~5-10 seconds each
    q_idx = 0
    while current_duration < duration:
        query = search_queries[q_idx % len(search_queries)]
        video_url = fetch_stock_video(query)
        
        if not video_url:
            # Fallback to general finance if specific keyword fails
            video_url = fetch_stock_video("finance")
            
        if not video_url:
            break
            
        temp_stock = f"outputs/videos/temp_stock_{len(clips)}.mp4"
        download_file(video_url, temp_stock)
        
        clip = VideoFileClip(temp_stock)
        
        # Determine how much of this clip to use
        remaining = duration - current_duration
        use_duration = min(clip.duration, 10, remaining) # Max 10s per clip for variety
        
        if use_duration < remaining and use_duration < 3:
            # If clip is too short, loop it slightly or just take it all
            use_duration = min(clip.duration, remaining)

        clip = clip.subclip(0, use_duration).resize(height=1080) # Resize to standard height
        clips.append(clip)
        current_duration += use_duration
        q_idx += 1
        
        # Optimization: limit number of clips to avoid massive memory usage
        if len(clips) > 20:
            break

    if not clips:
        raise Exception("Could not find any stock footage.")
    
    # Concatenate all clips
    final_clip = concatenate_videoclips(clips, method="compose")
    
    # If still shorter than audio (rare), loop the whole thing
    if final_clip.duration < duration:
        final_clip = final_clip.loop(duration=duration)
    else:
        final_clip = final_clip.subclip(0, duration)
    
    final_video = final_clip.set_audio(audio)
    
    # Write output
    final_video.write_videofile(video_save_path, fps=24, codec="libx264", audio_codec="aac")
    
    # Cleanup
    for i in range(len(clips)):
        temp_path = f"outputs/videos/temp_stock_{i}.mp4"
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    return video_save_path

if __name__ == "__main__":
    # Test
    # try:
    #     create_video("outputs/audio/test_voice.mp3", "outputs/videos/test_output.mp4", ["money"])
    # except Exception as e:
    #     print(f"Error: {e}")
    pass
