#!/usr/bin/env python3

import click
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import datetime
import os

# Constants for achievement appearance
ACHIEVEMENT_WIDTH = 184
ACHIEVEMENT_HEIGHT = 184
ICON_SIZE = 64
PADDING = 10
TITLE_FONT_SIZE = 14
DESC_FONT_SIZE = 11
GLOW_COLOR = (255, 215, 0, 180)  # Golden color with alpha
BACKGROUND_COLOR = (32, 34, 37)  # Steam's dark theme background
TEXT_COLOR = (255, 255, 255)  # White text
DESC_COLOR = (180, 180, 180)  # Gray color for description

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Wrap text to fit within max_width using the specified font."""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        text_width = font.getlength(' '.join(current_line))
        if text_width > max_width:
            if len(current_line) > 1:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(word)
                current_line = []
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def create_achievement_frame(name: str, description: str, icon_path: Path, is_rare: bool = False) -> Image.Image:
    # Create base image with Steam's dark theme background
    achievement = Image.new('RGBA', (ACHIEVEMENT_WIDTH, ACHIEVEMENT_HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(achievement)
    
    # Load and resize the achievement icon
    icon = Image.open(icon_path).convert('RGBA')
    icon = icon.resize((ICON_SIZE, ICON_SIZE), Image.Resampling.LANCZOS)
    
    # Calculate positions
    icon_x = (ACHIEVEMENT_WIDTH - ICON_SIZE) // 2
    icon_y = PADDING
    
    # Add glow effect for rare achievements
    if is_rare:
        glow = Image.new('RGBA', (ICON_SIZE + 20, ICON_SIZE + 20), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        glow_draw.ellipse([0, 0, ICON_SIZE + 20, ICON_SIZE + 20], fill=GLOW_COLOR)
        achievement.paste(glow, (icon_x - 10, icon_y - 10), glow)
    
    # Paste the icon
    achievement.paste(icon, (icon_x, icon_y), icon)
    
    # Load fonts
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", TITLE_FONT_SIZE)
        desc_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", DESC_FONT_SIZE)
    except OSError:
        title_font = ImageFont.load_default()
        desc_font = title_font
    
    # Calculate text area width
    text_area_width = ACHIEVEMENT_WIDTH - (2 * PADDING)
    
    # Wrap and draw title
    title_lines = wrap_text(name, title_font, text_area_width)
    text_y = icon_y + ICON_SIZE + PADDING
    
    for line in title_lines:
        text_width = title_font.getlength(line)
        text_x = (ACHIEVEMENT_WIDTH - text_width) // 2
        draw.text((text_x, text_y), line, font=title_font, fill=TEXT_COLOR)
        text_y += TITLE_FONT_SIZE + 2
    
    # Add small padding between title and description
    text_y += 4
    
    # Wrap and draw description
    desc_lines = wrap_text(description, desc_font, text_area_width)
    for line in desc_lines:
        text_width = desc_font.getlength(line)
        text_x = (ACHIEVEMENT_WIDTH - text_width) // 2
        draw.text((text_x, text_y), line, font=desc_font, fill=DESC_COLOR)
        text_y += DESC_FONT_SIZE + 1
    
    return achievement

@click.command()
@click.option('--name', required=True, help='Name of the achievement')
@click.option('--description', required=True, help='Description of the achievement')
@click.option('--image', required=True, type=click.Path(exists=True), help='Path to the achievement icon image')
@click.option('--rare', is_flag=True, help='Add golden glow effect for rare achievements')
def generate_achievement(name: str, description: str, image: str, rare: bool):
    """Generate a Steam-style achievement image."""
    # Create output directory if it doesn't exist
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    # Generate timestamp for unique filename
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = output_dir / f'achievement_{timestamp}.png'
    
    # Generate the achievement
    achievement = create_achievement_frame(name, description, Path(image), rare)
    
    # Save the achievement
    achievement.save(output_path)
    click.echo(f'Achievement saved to: {output_path}')

if __name__ == '__main__':
    generate_achievement() 