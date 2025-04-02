#!/usr/bin/env python3

import click
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import datetime
import os

# Constants for achievement appearance
ACHIEVEMENT_WIDTH = 520  # Wider to match Steam style
ACHIEVEMENT_HEIGHT = 96  # Shorter to match Steam style
ICON_SIZE = 64
PADDING = 16
CORNER_RADIUS = 4
TITLE_FONT_SIZE = 15
DESC_FONT_SIZE = 13
BACKGROUND_COLOR = (22, 24, 28)  # Darker background
CONTAINER_COLOR = (38, 40, 44)  # Achievement container color
TEXT_COLOR = (255, 255, 255)  # White text
DESC_COLOR = (128, 128, 128)  # Lighter gray for description

# Font paths - try multiple options to ensure compatibility
FONT_PATHS = [
    "/usr/share/fonts/google-noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/google-noto/NotoSans-Regular.ttf",  # Fallback to regular if bold not found
]

FONT_PATHS_REGULAR = [
    "/usr/share/fonts/google-noto/NotoSans-Regular.ttf",
]

def find_font(font_paths: list[str], size: int) -> ImageFont.FreeTypeFont:
    """Try to load a font from the list of possible paths."""
    # First try the specified paths
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
            
    # If that fails, try to find Noto Sans using fc-match
    try:
        import subprocess
        font_path = subprocess.check_output(['fc-match', '-f', '%{file}', 'Noto Sans']).decode('utf-8').strip()
        return ImageFont.truetype(font_path, size)
    except:
        return ImageFont.load_default()

def rounded_rectangle(draw: ImageDraw, xy: tuple, corner_radius: int, fill=None):
    """Draw a rounded rectangle"""
    x1, y1, x2, y2 = xy
    draw.rectangle((x1 + corner_radius, y1, x2 - corner_radius, y2), fill=fill)
    draw.rectangle((x1, y1 + corner_radius, x2, y2 - corner_radius), fill=fill)
    
    # Draw corners
    draw.pieslice((x1, y1, x1 + corner_radius * 2, y1 + corner_radius * 2), 180, 270, fill=fill)
    draw.pieslice((x2 - corner_radius * 2, y1, x2, y1 + corner_radius * 2), 270, 360, fill=fill)
    draw.pieslice((x1, y2 - corner_radius * 2, x1 + corner_radius * 2, y2), 90, 180, fill=fill)
    draw.pieslice((x2 - corner_radius * 2, y2 - corner_radius * 2, x2, y2), 0, 90, fill=fill)

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
    # Create base image with dark background
    achievement = Image.new('RGBA', (ACHIEVEMENT_WIDTH, ACHIEVEMENT_HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(achievement)
    
    # Draw rounded rectangle container
    container_padding = 2
    rounded_rectangle(draw, 
                     (container_padding, 
                      container_padding, 
                      ACHIEVEMENT_WIDTH - container_padding, 
                      ACHIEVEMENT_HEIGHT - container_padding),
                     CORNER_RADIUS,
                     CONTAINER_COLOR)
    
    # Load and resize the achievement icon
    icon = Image.open(icon_path).convert('RGBA')
    icon = icon.resize((ICON_SIZE, ICON_SIZE), Image.Resampling.LANCZOS)
    
    # Calculate positions
    icon_x = PADDING
    icon_y = (ACHIEVEMENT_HEIGHT - ICON_SIZE) // 2
    text_start_x = icon_x + ICON_SIZE + PADDING
    
    # Paste the icon
    achievement.paste(icon, (icon_x, icon_y), icon)
    
    # Load fonts with UTF-8 support
    title_font = find_font(FONT_PATHS, TITLE_FONT_SIZE)
    desc_font = find_font(FONT_PATHS_REGULAR, DESC_FONT_SIZE)
    
    # Calculate text area width
    text_area_width = ACHIEVEMENT_WIDTH - text_start_x - PADDING
    
    # Draw title
    text_y = icon_y + 5  # Align with top of icon with small offset
    title_lines = wrap_text(name, title_font, text_area_width)
    for line in title_lines[:2]:  # Limit to 2 lines
        draw.text((text_start_x, text_y), line, font=title_font, fill=TEXT_COLOR)
        text_y += TITLE_FONT_SIZE + 2
    
    # Draw description
    text_y += 4  # Space between title and description
    desc_lines = wrap_text(description, desc_font, text_area_width)
    for line in desc_lines[:2]:  # Limit to 2 lines
        draw.text((text_start_x, text_y), line, font=desc_font, fill=DESC_COLOR)
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