# 💰 AutomationEngine: Faceless Finance Channel Automation

AutomationEngine is a powerful, AI-driven content creation pipeline designed to automate the production of faceless finance YouTube Shorts and videos. From trending topic discovery to scheduled YouTube uploads, this tool handles the heavy lifting of content creation.

## 🚀 Key Features

*   **Brainstorming**: Automatically generates click-worthy, trending finance topics using Gemini AI.
*   **Scriptwriting**: Crafts high-retention 60-second scripts tailored for faceless channels.
*   **AI Voiceovers**: Generates professional, human-like narration using ElevenLabs Multilingual V2.
*   **Dynamic Video Assembly**: Automatically fetches and concatenates multiple relevant stock footage clips from Pexels based on your script content.
*   **Premium Dashboard**: A sleek, Streamlit-based UI with a modern dark-gradient aesthetic.
*   **Queue & Scheduler**: Plan your content calendar by scheduling videos for future uploads.
*   **YouTube Integration**: Managed OAuth2 flow for direct video uploads to your channel.

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/razeeullah/AutomationEngine.git
   cd AutomationEngine
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Mac/Linux
   # .venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Keys**:
   Create a `.env` file in the root directory (or use the UI to save them):
   ```env
   GEMINI_API_KEY=your_gemini_key
   ELEVENLABS_API_KEY=your_elevenlabs_key
   PEXELS_API_KEY=your_pexels_key
   ```

5. **YouTube Setup**:
   Place your `client_secrets.json` (downloaded from Google Cloud Console) in the root directory.

## 💻 Usage

Run the Streamlit application:
```bash
streamlit run app.py
```

Follow the pipeline:
1. **Topic & Script**: Generate ideas and write your script.
2. **Voiceover**: Choose a voice and generate narration.
3. **Video Gen**: Assembles the final video with stock footage.
4. **Queue & Schedule**: Set a time and date for your video to go live.

## 🔒 Safety & Privacy

The `.gitignore` is pre-configured to exclude your API keys, OAuth secrets, and generated media files by default. Never share your `.env` or `client_secrets.json` files.

---
Built with ❤️ by Razeeullah.
