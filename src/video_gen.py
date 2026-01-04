import os
import requests
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
from dotenv import load_dotenv
from src.sora_gen import sora_generate_full

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

def create_video(audio_path, video_save_path, keywords=None, script_text=None, source="stock", sora_api_key=None):
    """
    Combines audio with video footage (Stock or Sora AI) and adds subtitles.
    """
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    
    clips = []
    
    if source == "sora":
        # Generative Video path
        try:
            temp_sora = "outputs/videos/temp_sora.mp4"
            # Use the script or keywords to prompt Sora
            sora_prompt = script_text[:500] if script_text else " ".join(keywords)
            sora_generate_full(sora_prompt, temp_sora, api_key=sora_api_key)
            clips = [VideoFileClip(temp_sora).resize(height=1080)]
        except Exception as e:
            print(f"Sora generation failed: {e}. Falling back to stock footage.")
            source = "stock"

    if source == "stock":
        # Stock Footage path (Pexels)
        search_queries = keywords if keywords else ["finance", "money", "growth", "savings"]
        current_duration = 0
        q_idx = 0
        
        while current_duration < duration:
            query = search_queries[q_idx % len(search_queries)]
            video_url = fetch_stock_video(query)
            
            if not video_url:
                video_url = fetch_stock_video("finance")
            
            if not video_url: break
                
            temp_stock = f"outputs/videos/temp_stock_{len(clips)}.mp4"
            download_file(video_url, temp_stock)
            
            clip = VideoFileClip(temp_stock)
            remaining = duration - current_duration
            use_duration = min(clip.duration, 10, remaining)
            
            if use_duration < remaining and use_duration < 3:
                use_duration = min(clip.duration, remaining)

            clip = clip.subclip(0, use_duration).resize(height=1080)
            clips.append(clip)
            current_duration += use_duration
            q_idx += 1
            if len(clips) > 20: break

    if not clips:
        # Fallback to a solid color if no footage found
        from moviepy import ColorClip
        clips = [ColorClip(size=(1920, 1080), color=(0,0,0), duration=duration)]
    
    # Concatenate all clips
    video_base = concatenate_videoclips(clips, method="compose")
    
    # If still shorter than audio (rare), loop the whole thing
    if video_base.duration < duration:
        video_base = video_base.loop(duration=duration)
    else:
        video_base = video_base.subclip(0, duration)
    
    # Add Subtitles if script_text is provided
    final_clips = [video_base]
    if script_text:
        # Simple subtitle logic: split by sentences and distribute over duration
        import re
        sentences = re.split(r'(?<=[.!?]) +', script_text.strip())
        sentences = [s for s in sentences if s.strip()]
        
        if sentences:
            time_per_sentence = duration / len(sentences)
            for i, sentence in enumerate(sentences):
                # Clean sentence for display
                txt = sentence.strip()
                if len(txt) > 60: txt = txt[:57] + "..." # Truncate long sentences
                
                try:
                    subtitle = (TextClip(text=txt, font_size=50, color='white', font='Arial', 
                                         stroke_color='black', stroke_width=2, 
                                         method='caption', size=(video_base.w * 0.8, None))
                                .with_start(i * time_per_sentence)
                                .with_duration(time_per_sentence)
                                .with_position(('center', video_base.h * 0.8)))
                    final_clips.append(subtitle)
                except Exception as e:
                    print(f"Warning: Could not create subtitle clip: {e}")

    final_video = CompositeVideoClip(final_clips).set_audio(audio)
    
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
