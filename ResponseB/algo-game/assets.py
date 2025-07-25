"""
Asset manager module for the Football Game.
Handles loading and caching of all game assets.
"""

import os
import pygame
import sys
from typing import Dict, Optional
import config


class AssetManager:
    """Manages game assets including images, sounds, and fonts."""
    
    def __init__(self):
        self._images: Dict[str, pygame.Surface] = {}
        self._fonts: Dict[str, pygame.font.Font] = {}
        self._sounds: Dict[str, pygame.mixer.Sound] = {}
        self._base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        
    def load_image(self, name: str, path: str, scale: Optional[tuple] = None, 
                   flip: Optional[tuple] = None) -> pygame.Surface:
        """
        Load an image and optionally scale/flip it.
        
        Args:
            name: Identifier for the image
            path: Path to the image file
            scale: Optional (width, height) tuple for scaling
            flip: Optional (flip_x, flip_y) tuple for flipping
            
        Returns:
            The loaded pygame.Surface
        """
        if name in self._images:
            return self._images[name]
            
        try:
            # Try relative path first
            full_path = os.path.join(self._base_path, path)
            if not os.path.exists(full_path):
                # Try absolute path
                full_path = path
                
            image = pygame.image.load(full_path)
            
            if scale:
                image = pygame.transform.scale(image, scale)
                
            if flip:
                image = pygame.transform.flip(image, flip[0], flip[1])
                
            self._images[name] = image
            return image
            
        except pygame.error as e:
            print(f"Error loading image '{name}' from '{path}': {e}")
            # Return a placeholder surface
            placeholder = pygame.Surface(scale if scale else (50, 50))
            placeholder.fill(config.RED)
            self._images[name] = placeholder
            return placeholder
            
    def load_font(self, name: str, size: int, 
                  font_file: Optional[str] = None) -> pygame.font.Font:
        """
        Load a font.
        
        Args:
            name: Identifier for the font
            size: Font size
            font_file: Optional path to font file (None for default)
            
        Returns:
            The loaded pygame.font.Font
        """
        key = f"{name}_{size}"
        if key in self._fonts:
            return self._fonts[key]
            
        try:
            font = pygame.font.Font(font_file, size)
            self._fonts[key] = font
            return font
        except Exception as e:
            print(f"Error loading font '{name}': {e}")
            # Fallback to default font
            font = pygame.font.Font(None, size)
            self._fonts[key] = font
            return font
            
    def get_image(self, name: str) -> Optional[pygame.Surface]:
        """Get a previously loaded image by name."""
        return self._images.get(name)
        
    def get_font(self, name: str, size: int) -> Optional[pygame.font.Font]:
        """Get a previously loaded font by name and size."""
        key = f"{name}_{size}"
        return self._fonts.get(key)
        
    def load_all_assets(self):
        """Load all game assets."""
        # Load images
        self.load_image("cannon1", config.CANNON_IMAGE_PATH, 
                       scale=config.CANNON_SIZE)
        self.load_image("cannon2", config.CANNON_IMAGE_PATH, 
                       scale=config.CANNON_SIZE, flip=(False, True))
        self.load_image("ball", config.BALL_IMAGE_PATH, 
                       scale=(config.BALL_RADIUS * 2, config.BALL_RADIUS * 2))
        
        # Load fonts
        self.load_font("title", config.TITLE_FONT_SIZE)
        self.load_font("team", config.TEAM_FONT_SIZE)
        self.load_font("bullet_count", config.BULLET_FONT_SIZE)
        self.load_font("default", 36)
        
    def clear(self):
        """Clear all cached assets."""
        self._images.clear()
        self._fonts.clear()
        self._sounds.clear()


# Global asset manager instance
asset_manager = AssetManager()
