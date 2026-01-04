import streamlit as st
import os
from dotenv import load_dotenv
from src.topic_gen import generate_finance_topics
from src.script_writer import generate_script
from src.voiceover import generate_voiceover
from src.video_gen import create_video
from src.thumbnail_gen import generate_thumbnail
from src.uploader import get_authenticated_service, upload_video
from src.scheduler import add_to_queue, get_queue, process_queue, QUEUE_FILE
from datetime import datetime, timedelta

load_dotenv()

def save_key_to_env(key_name, key_value):
    if not key_value:
        return
    
    with open(".env", "r") as f:
        lines = f.readlines()
    
    found = False
    with open(".env", "w") as f:
        for line in lines:
            if line.startswith(f"{key_name}="):
                f.write(f"{key_name}={key_value}\n")
                found = True
            else:
                f.write(line)
        if not found:
            f.write(f"{key_name}={key_value}\n")
    
    os.environ[key_name] = key_value

st.set_page_config(page_title="Faceless Finance Automation", layout="wide")

st.title("💰 Faceless Finance Channel Automation")
st.markdown("Automate your content creation pipeline from topics to YouTube uploads.")

with st.sidebar:
    st.header("Settings")
    gemini_key = st.text_input("Gemini API Key", value=os.getenv("GEMINI_API_KEY", ""), type="password")
    eleven_key = st.text_input("ElevenLabs API Key", value=os.getenv("ELEVENLABS_API_KEY", ""), type="password")
    
    if st.button("Save API Keys"):
        save_key_to_env("GEMINI_API_KEY", gemini_key)
        save_key_to_env("ELEVENLABS_API_KEY", eleven_key)
        st.success("Keys saved to .env and updated for this session!")

st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }
    .stButton>button {
        border-radius: 20px;
        background-color: #4CAF50;
        color: white;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }
    .stTab {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

tabs = st.tabs(["Topic & Script", "Voiceover", "Video Gen", "YouTube Upload", "Queue & Schedule", "Analytics"])

with tabs[0]:
    st.header("1. Topic & Script Generation")
    
    col1, col2 = st.columns(2)
    with col1:
        topic_query = st.text_input("Niche / Hook", value="Personal Finance for Gen Z")
        num_topics = st.slider("Number of topics", 1, 50, 10)
        
        if st.button("Generate Topics"):
            with st.spinner("Generating topics..."):
                try:
                    topics = generate_finance_topics(topic_query, num_topics, api_key=gemini_key)
                    st.session_state['topics'] = topics
                    st.success(f"Generated {len(topics)} topics!")
                except Exception as e:
                    st.error(f"Error: {e}")

    with col2:
        if 'topics' in st.session_state:
            selected_topic = st.selectbox("Select a topic to write a script for", st.session_state['topics'])
            if st.button("Write Script"):
                with st.spinner("Writing script..."):
                    try:
                        script = generate_script(selected_topic, api_key=gemini_key)
                        st.session_state['current_script'] = script
                        st.session_state['current_topic'] = selected_topic
                        st.success("Script generated!")
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.info("Generate topics first.")

    if 'current_script' in st.session_state:
        st.subheader(f"Script for: {st.session_state['current_topic']}")
        st.text_area("Script", value=st.session_state['current_script'], height=300)

with tabs[1]:
    st.header("2. Voiceover Creation")
    if 'current_script' in st.session_state:
        st.write(f"Generate voiceover for: **{st.session_state['current_topic']}**")
        voice_id = st.selectbox("Select Voice", ["Adam (Finance)", "Bella (Soft)", "Antoni (Professional)"], index=0)
        # Map voice names to IDs (placeholders)
        v_map = {"Adam (Finance)": "pNInz6obpgDQGcFmaJgB", "Bella (Soft)": "EXAVITQu4vr4xnSDxMaL", "Antoni (Professional)": "ErXwUjzD78v94vL8l4Ew"}
        
        if st.button("Generate MP3"):
            with st.spinner("Generating voiceover..."):
                try:
                    out_path = f"outputs/audio/{st.session_state['current_topic'].replace(' ', '_')[:20]}.mp3"
                    generate_voiceover(st.session_state['current_script'], out_path, voice_id=v_map[voice_id], api_key=eleven_key)
                    st.session_state['current_audio'] = out_path
                    st.success(f"Voiceover saved to {out_path}")
                    st.audio(out_path)
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.info("Write a script first.")

with tabs[2]:
    st.header("3. Video Assembly")
    if 'current_audio' in st.session_state:
        st.write(f"Create video for: **{st.session_state['current_topic']}**")
        keywords = st.text_input("Footage Keywords (comma separated)", value="finance, money, stock market")
        
        if st.button("Generate Final Video"):
            with st.spinner("Fetching footage and assembling video (this may take a minute)..."):
                try:
                    video_path = f"outputs/videos/{st.session_state['current_topic'].replace(' ', '_')[:20]}.mp4"
                    kw_list = [k.strip() for k in keywords.split(",")]
                    create_video(st.session_state['current_audio'], video_path, keywords=kw_list)
                    st.session_state['current_video'] = video_path
                    st.success(f"Video created: {video_path}")
                    st.video(video_path)
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.info("Generate a voiceover first.")

with tabs[3]:
    st.header("4. YouTube Dashboard")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Thumbnail Generation")
        if 'current_topic' in st.session_state:
            thumb_text = st.text_input("Thumbnail Text", value=st.session_state['current_topic'][:30].upper())
            if st.button("Generate Thumbnail"):
                try:
                    thumb_path = f"outputs/thumbnails/{st.session_state['current_topic'].replace(' ', '_')[:20]}.png"
                    generate_thumbnail(thumb_text, thumb_path)
                    st.session_state['current_thumbnail'] = thumb_path
                    st.image(thumb_path)
                    st.success(f"Thumbnail saved to {thumb_path}")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.info("Write a script first.")

    with col2:
        st.subheader("Upload to YouTube")
        if 'current_video' in st.session_state:
            video_title = st.text_input("YouTube Title", value=st.session_state['current_topic'])
            video_desc = st.text_area("Description", value=f"Check out this video on {st.session_state['current_topic']}\n\n#finance #money #shorts")
            
            if st.button("🚀 Upload Now"):
                st.info("Authenticating via YouTube API...")
                try:
                    # Authenticate and upload
                    youtube = get_authenticated_service()
                    response = upload_video(youtube, st.session_state['current_video'], video_title, video_desc)
                    st.success(f"Upload successful! Video ID: {response.get('id')}")
                    # st.warning("YouTube Upload is in 'Blueprint Mode'. In production, ensure client_secrets.json is configured and OAuth flow is handled.")
                    st.info(f"Video ready at: {st.session_state['current_video']}")
                    st.info(f"Thumbnail ready at: {st.session_state.get('current_thumbnail', 'Not generated')}")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.info("Generate a video first.")

with tabs[4]:
    st.header("5. Queue & Schedule")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Schedule New Video")
        if 'current_video' in st.session_state:
            st.write(f"Scheduling: **{st.session_state['current_topic']}**")
            d = st.date_input("Scheduled Date", datetime.now())
            t = st.time_input("Scheduled Time", datetime.now() + timedelta(hours=1))
            full_dt = datetime.combine(d, t)
            
            if st.button("📅 Add to Queue"):
                add_to_queue(
                    st.session_state['current_video'], 
                    st.session_state['current_topic'], 
                    f"Check out this video on {st.session_state['current_topic']}\n\n#finance #money #shorts",
                    full_dt
                )
                st.success(f"Video queued for {full_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.info("Generate a video in the 'Video Gen' tab first.")

    with col2:
        st.subheader("Current Queue")
        if st.button("🔄 Refresh & Process Queue"):
            process_queue()
            st.rerun()
            
        queue = get_queue()
        if not queue:
            st.info("No videos in queue.")
        else:
            for i, item in enumerate(queue):
                with st.expander(f"{item['status'].upper()}: {item['title']} - {item['schedule_time']}"):
                    st.write(f"Path: {item['video_path']}")
                    st.write(f"Description: {item['description']}")
                    if item['status'] == 'queued':
                        if st.button(f"Cancel {i}", key=f"cancel_{i}"):
                            queue.pop(i)
                            with open(QUEUE_FILE, "w") as f:
                                import json
                                json.dump(queue, f, indent=4)
                            st.rerun()

with tabs[5]:
    st.header("6. Channel Analytics")
    st.info("This is a placeholder for your YouTube channel performance metrics.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Views", "1.2k", "+12%")
    col2.metric("Watch Time", "45h", "+5%")
    col3.metric("Subscribers", "124", "+2")
    
    st.line_chart({"Views": [10, 25, 40, 35, 60, 80, 110]})

