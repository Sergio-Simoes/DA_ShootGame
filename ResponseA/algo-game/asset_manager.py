"""Asset manager module for loading and caching game assets."""

import os
import pygame

class AssetManager:
    def __init__(self):
        self.images = {}
        self.fonts = {}
        self.sounds = {}

    def load_image(self, name, filepath, scale=None, flip=False, colorkey=None):
        """Load an image into the cache or return from cache if already loaded."""
        if name in self.images:
            return self.images[name]
        
        try:
            image = pygame.image.load(filepath)
            if scale:
                image = pygame.transform.scale(image, scale)
            if flip:
                image = pygame.transform.flip(image, False, True)
            if colorkey is not None:
                image = image.convert()
                image.set_colorkey(colorkey)
            else:
                image = image.convert_alpha()
                
            self.images[name] = image
            return image
        except pygame.error as e:
            print(f"Failed to load image '{filepath}': {e}")
            # Return a placeholder image for error cases
            placeholder = pygame.Surface((50, 50))
            placeholder.fill((255, 0, 255))  # Hot pink for visibility
            return placeholder

    def get_image(self, name):
        """Get an image from the cache by name."""
        if name in self.images:
            return self.images[name]
        print(f"Warning: Image '{name}' not found in cache")
        # Return placeholder for missing images
        placeholder = pygame.Surface((50, 50))
        placeholder.fill((255, 0, 255))
        return placeholder

    def load_font(self, name, size=None, custom_filepath=None):
        """Load a font into the cache or return from cache if already loaded."""
        key = f"{name}_{size}"
        if key in self.fonts:
            return self.fonts[key]
        
        try:
            if custom_filepath and os.path.exists(custom_filepath):
                font = pygame.font.Font(custom_filepath, size)
            else:
                font = pygame.font.Font(None, size)  # Use default font
                
            self.fonts[key] = font
            return font
        except pygame.error as e:
            print(f"Failed to load font: {e}")
            return pygame.font.Font(None, size if size else 24)  # Default fallback

    def get_font(self, name, size=None):
        """Get a font from the cache by name and size."""
        key = f"{name}_{size}"
        if key in self.fonts:
            return self.fonts[key]
        # Auto-load if not found
        return self.load_font(name, size)

    def load_sound(self, name, filepath):
        """Load a sound into the cache or return from cache if already loaded."""
        if name in self.sounds:
            return self.sounds[name]
        
        try:
            sound = pygame.mixer.Sound(filepath)
            self.sounds[name] = sound
            return sound
        except pygame.error as e:
            print(f"Failed to load sound '{filepath}': {e}")
            return None

    def get_sound(self, name):
        """Get a sound from the cache by name."""
        if name in self.sounds:
            return self.sounds[name]
        print(f"Warning: Sound '{name}' not found in cache")
        return None

    def preload_assets(self):
        """Preload common game assets."""
        # Load images
        self.load_image('cannon1', 'cannon.png', scale=(60, 20))
        self.load_image('cannon2', 'cannon.png', scale=(60, 20), flip=True)
        
        # Load fonts
        self.load_font('title', 64)
        self.load_font('game', 36)
        self.load_font('bullet_count', 24)
        self.load_font('winner', 84)

# Global asset manager instance that can be imported by other modules
asset_manager = AssetManager()
