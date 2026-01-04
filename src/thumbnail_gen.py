import os
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

load_dotenv()

def generate_thumbnail(text, output_path, bg_color=(0, 0, 0)):
    """
    Generates a simple text-based thumbnail using Pillow.
    """
    # Create a 1280x720 canvas
    width, height = 1280, 720
    image = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(image)
    
    # Try to load a font, fallback to default
    try:
        # On Mac, Arial is usually in this path
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 80)
    except:
        font = ImageFont.load_default()
    
    # Calculate text position (centered)
    # text_width, text_height = draw.textsize(text, font=font) # Older PIL
    # Newer PIL:
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    text_width = right - left
    text_height = bottom - top
    
    position = ((width - text_width) / 2, (height - text_height) / 2)
    
    # Draw text with a shadow for readability
    shadow_pos = (position[0] + 5, position[1] + 5)
    draw.text(shadow_pos, text, font=font, fill=(50, 50, 50))
    draw.text(position, text, font=font, fill=(255, 255, 255))
    
    image.save(output_path)
    return output_path

if __name__ == "__main__":
    # Test
    generate_thumbnail("MAKE $500/DAY", "outputs/thumbnails/test.png")
    print("Thumbnail generated.")
