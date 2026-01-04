from moviepy import TextClip
try:
    # TextClip requires ImageMagick to be installed
    tc = TextClip(text="Test", font_size=24, color='white')
    tc = tc.with_duration(5)
    print("TextClip Success")
except Exception as e:
    print(f"TextClip Error: {e}")
