"""Game sprite classes for all moving objects."""

import pygame
import math
from config import (
    BALL_RADIUS, BULLET_RADIUS, SCREEN_WIDTH, SCREEN_HEIGHT,
    CANNON_RADIUS, CANNON1_POS, CANNON2_POS
)

class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.vel = [0, 0]  # Velocity as [vx, vy]
        self.radius = BALL_RADIUS
        
        # Create a surface for the ball
        self.image = pygame.Surface((BALL_RADIUS * 2, BALL_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 255, 0), (BALL_RADIUS, BALL_RADIUS), BALL_RADIUS)
        
        # Create a rect for positioning
        self.rect = self.image.get_rect(center=(x, y))
    
    def update(self):
        # Movement is handled by physics engine
        pass
    
    def reset_position(self, x, y):
        self.rect.centerx = x
        self.rect.centery = y
        self.vel = [0, 0]
    
    @property
    def is_moving(self):
        return self.vel[0] != 0 or self.vel[1] != 0
    
    @property
    def position(self):
        return [self.rect.centerx, self.rect.centery]


class Cannon(pygame.sprite.Sprite):
    def __init__(self, x, y, player_num=1):
        super().__init__()
        self.player_num = player_num
        self.angle = 45 if player_num == 1 else 135
        self.power = 0
        self.radius = CANNON_RADIUS
        self.sprite_name = f'cannon{player_num}'
        
        # Create a placeholder surface for the rect
        self.image = pygame.Surface((60, 20), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (150, 150, 150), (0, 0, 60, 20))
        
        # Create a rect for positioning
        self.rect = self.image.get_rect(center=(x, y))
    
    def update(self):
        # Cannon doesn't move automatically
        pass


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, power, bullet_type="precision"):
        super().__init__()
        self.angle = angle
        self.power = power  
        self.bullet_type = bullet_type
        self.radius = BULLET_RADIUS
        
        # Create a surface for the bullet
        self.image = pygame.Surface((BULLET_RADIUS * 2, BULLET_RADIUS * 2), pygame.SRCALPHA)
        color = (255, 0, 0) if bullet_type == "power" else (0, 0, 0)
        pygame.draw.circle(self.image, color, (BULLET_RADIUS, BULLET_RADIUS), BULLET_RADIUS)
        
        # Create a rect for positioning
        self.rect = self.image.get_rect(center=(x, y))
    
    def update(self):
        # Movement is handled by physics engine
        pass
    
    def is_out_of_bounds(self):
        return (self.rect.left < 0 or self.rect.right > SCREEN_WIDTH or
                self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT)
