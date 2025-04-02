#!/usr/bin/env python3

import click
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import datetime
from dataclasses import dataclass
from typing import Tuple, Optional

@dataclass
class AchievementStyle:
    """Configuration class for achievement appearance."""
    width: int = 520
    height: int = 96
    icon_size: int = 64
    padding: int = 16
    corner_radius: int = 4
    title_font_size: int = 15
    desc_font_size: int = 13
    background_color: Tuple[int, int, int] = (22, 24, 28)
    container_color: Tuple[int, int, int] = (38, 40, 44)
    text_color: Tuple[int, int, int] = (255, 255, 255)
    desc_color: Tuple[int, int, int] = (128, 128, 128)
    glow_color: Tuple[int, int, int] = (255, 180, 50)
    glow_alpha: int = 160
    glow_size_extra: int = 80
    glow_radius: int = 40

class FontManager:
    """Handles font loading and management."""
    FONT_PATHS = [
        "/usr/share/fonts/google-noto/NotoSans-Bold.ttf",
        "/usr/share/fonts/google-noto/NotoSans-Regular.ttf",
    ]
    
    FONT_PATHS_REGULAR = [
        "/usr/share/fonts/google-noto/NotoSans-Regular.ttf",
    ]
    
    @staticmethod
    def find_font(font_paths: list[str], size: int) -> ImageFont.FreeTypeFont:
        """Load a font from the list of possible paths."""
        for path in font_paths:
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
                
        try:
            import subprocess
            font_path = subprocess.check_output(
                ['fc-match', '-f', '%{file}', 'Noto Sans']
            ).decode('utf-8').strip()
            return ImageFont.truetype(font_path, size)
        except:
            return ImageFont.load_default()

class TextRenderer:
    """Handles text wrapping and rendering."""
    @staticmethod
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

    @staticmethod
    def render_text_block(
        draw: ImageDraw.Draw,
        text: str,
        font: ImageFont.FreeTypeFont,
        start_pos: Tuple[int, int],
        max_width: int,
        color: Tuple[int, int, int],
        line_spacing: int
    ) -> int:
        """Render a block of text and return the new Y position."""
        lines = TextRenderer.wrap_text(text, font, max_width)
        current_y = start_pos[1]
        
        for line in lines[:2]:  # Limit to 2 lines
            draw.text((start_pos[0], current_y), line, font=font, fill=color)
            current_y += line_spacing
        
        return current_y

class GlowEffect:
    """Handles creation and application of the glow effect."""
    @staticmethod
    def create_glow_mask(size: Tuple[int, int], radius: int = 40) -> Image.Image:
        """Create a radial gradient mask for the glow effect."""
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        
        for i in range(radius, 0, -1):
            opacity = int((1 - (i / radius) ** 1.5) * 255)
            draw.ellipse([
                size[0]//2 - i, size[1]//2 - i,
                size[0]//2 + i, size[1]//2 + i
            ], fill=opacity)
        
        return mask

    @staticmethod
    def apply_glow(
        base_image: Image.Image,
        icon_pos: Tuple[int, int],
        style: AchievementStyle
    ) -> None:
        """Apply glow effect to the base image."""
        glow_size = style.icon_size + style.glow_size_extra
        glow = Image.new('RGBA', (glow_size, glow_size), (0, 0, 0, 0))
        
        mask = GlowEffect.create_glow_mask((glow_size, glow_size), style.glow_radius)
        
        glow_pixels = glow.load()
        mask_pixels = mask.load()
        for y in range(glow_size):
            for x in range(glow_size):
                alpha = mask_pixels[x, y]
                glow_pixels[x, y] = (*style.glow_color, min(alpha, style.glow_alpha))
        
        glow = glow.filter(ImageFilter.GaussianBlur(5))
        glow = glow.filter(ImageFilter.GaussianBlur(3))
        
        offset = style.glow_size_extra // 2
        base_image.paste(glow, 
                        (icon_pos[0] - offset, icon_pos[1] - offset),
                        glow)

class AchievementGenerator:
    """Main class for generating achievements."""
    def __init__(self, style: Optional[AchievementStyle] = None):
        self.style = style or AchievementStyle()
        self.font_manager = FontManager()
        self.text_renderer = TextRenderer()
    
    @staticmethod
    def draw_container(draw: ImageDraw.Draw, style: AchievementStyle) -> None:
        """Draw the achievement container with rounded corners."""
        container_padding = 2
        x1, y1 = container_padding, container_padding
        x2 = style.width - container_padding
        y2 = style.height - container_padding
        
        # Draw main rectangles
        draw.rectangle((x1 + style.corner_radius, y1, x2 - style.corner_radius, y2),
                      fill=style.container_color)
        draw.rectangle((x1, y1 + style.corner_radius, x2, y2 - style.corner_radius),
                      fill=style.container_color)
        
        # Draw corners
        for x, y, start, end in [
            (x1, y1, 180, 270),
            (x2 - style.corner_radius * 2, y1, 270, 360),
            (x1, y2 - style.corner_radius * 2, 90, 180),
            (x2 - style.corner_radius * 2, y2 - style.corner_radius * 2, 0, 90)
        ]:
            draw.pieslice(
                (x, y, x + style.corner_radius * 2, y + style.corner_radius * 2),
                start, end, fill=style.container_color
            )

    def create_achievement(
        self,
        name: str,
        description: str,
        icon_path: Path,
        is_rare: bool = False
    ) -> Image.Image:
        """Create an achievement image with the specified parameters."""
        # Create base image
        achievement = Image.new('RGBA', 
                              (self.style.width, self.style.height),
                              self.style.background_color)
        draw = ImageDraw.Draw(achievement)
        
        # Draw container
        self.draw_container(draw, self.style)
        
        # Load and resize icon
        icon = Image.open(icon_path).convert('RGBA')
        icon = icon.resize((self.style.icon_size, self.style.icon_size),
                         Image.Resampling.LANCZOS)
        
        # Calculate positions
        icon_x = self.style.padding
        icon_y = (self.style.height - self.style.icon_size) // 2
        text_start_x = icon_x + self.style.icon_size + self.style.padding
        
        # Add glow for rare achievements
        if is_rare:
            GlowEffect.apply_glow(achievement, (icon_x, icon_y), self.style)
        
        # Paste icon
        achievement.paste(icon, (icon_x, icon_y), icon)
        
        # Load fonts
        title_font = self.font_manager.find_font(
            FontManager.FONT_PATHS,
            self.style.title_font_size
        )
        desc_font = self.font_manager.find_font(
            FontManager.FONT_PATHS_REGULAR,
            self.style.desc_font_size
        )
        
        # Calculate text area width
        text_area_width = self.style.width - text_start_x - self.style.padding
        
        # Render title
        text_y = icon_y + 5
        text_y = self.text_renderer.render_text_block(
            draw, name, title_font,
            (text_start_x, text_y),
            text_area_width,
            self.style.text_color,
            self.style.title_font_size + 2
        )
        
        # Render description
        text_y += 4
        self.text_renderer.render_text_block(
            draw, description, desc_font,
            (text_start_x, text_y),
            text_area_width,
            self.style.desc_color,
            self.style.desc_font_size + 1
        )
        
        return achievement

@click.command()
@click.option('--name', required=True, help='Name of the achievement')
@click.option('--description', required=True, help='Description of the achievement')
@click.option('--image', required=True, type=click.Path(exists=True),
              help='Path to the achievement icon image')
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
    generator = AchievementGenerator()
    achievement = generator.create_achievement(name, description, Path(image), rare)
    
    # Save the achievement
    achievement.save(output_path)
    click.echo(f'Achievement saved to: {output_path}')

if __name__ == '__main__':
    generate_achievement() 