"""
Sprite classes for the Football Game.
Contains all sprite-based game objects.
"""

import pygame
import math
import random
from typing import Tuple, Optional
import config
from assets import asset_manager


class Ball(pygame.sprite.Sprite):
    """The football/ball sprite."""
    
    def __init__(self, pos: Tuple[int, int]):
        super().__init__()
        self.image = asset_manager.get_image("ball")
        if self.image is None:
            # Fallback if image not loaded
            self.image = pygame.Surface((config.BALL_RADIUS * 2, config.BALL_RADIUS * 2))
            pygame.draw.circle(self.image, config.GREEN, 
                             (config.BALL_RADIUS, config.BALL_RADIUS), 
                             config.BALL_RADIUS)
            
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)
        self.radius = config.BALL_RADIUS
        
    def update(self):
        """Update ball physics."""
        # Update position
        self.pos += self.vel
        
        # Apply friction
        self.vel *= config.BALL_FRICTION
        
        # Stop if velocity is very low
        if abs(self.vel.x) < config.BALL_STOP_VELOCITY:
            self.vel.x = 0
        if abs(self.vel.y) < config.BALL_STOP_VELOCITY:
            self.vel.y = 0
            
        # Keep rect in sync with position
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
    def check_boundaries(self) -> Optional[str]:
        """
        Check and handle boundary collisions.
        Returns 'left' or 'right' if ball went out, None otherwise.
        """
        # Top/bottom wall collision
        if self.pos.y - self.radius <= 0 or self.pos.y + self.radius >= config.SCREEN_HEIGHT:
            self.vel.y = -self.vel.y
            self.pos.y = max(self.radius, min(config.SCREEN_HEIGHT - self.radius, self.pos.y))
            
        # Left/right goal detection
        if self.pos.x - self.radius <= 0:
            return 'left'
        elif self.pos.x + self.radius >= config.SCREEN_WIDTH:
            return 'right'
            
        return None
        
    def apply_force(self, angle: float, magnitude: float):
        """Apply force to the ball in given direction."""
        force_x = math.cos(angle) * magnitude
        force_y = math.sin(angle) * magnitude
        self.vel.x += force_x
        self.vel.y += force_y
        
    def reset(self, pos: Tuple[int, int]):
        """Reset ball to given position with zero velocity."""
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)
        self.rect.center = pos
        
    def is_moving(self) -> bool:
        """Check if ball is still moving."""
        return self.vel.length() > config.BALL_STOP_VELOCITY


class Cannon(pygame.sprite.Sprite):
    """Cannon sprite that can rotate and charge power."""
    
    def __init__(self, pos: Tuple[int, int], player_num: int):
        super().__init__()
        self.player_num = player_num
        self.pos = pygame.Vector2(pos)
        self.base_image = asset_manager.get_image(f"cannon{player_num}")
        
        if self.base_image is None:
            # Fallback if image not loaded
            self.base_image = pygame.Surface(config.CANNON_SIZE)
            self.base_image.fill(config.RED if player_num == 1 else config.BLUE)
            
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=pos)
        self.angle = 0
        self.power = 0
        self.power_bullets = config.POWER_BULLETS_COUNT
        self.precision_bullets = config.PRECISION_BULLETS_COUNT
        
    def rotate_to_angle(self, angle: float):
        """Rotate cannon to specified angle."""
        self.angle = angle
        self.image = pygame.transform.rotate(self.base_image, angle)
        self.rect = self.image.get_rect(center=self.pos)
        
    def charge_power(self, amount: float):
        """Increase cannon power by amount, capped at MAX_POWER."""
        self.power = min(self.power + amount, config.MAX_POWER)
        
    def reset_power(self):
        """Reset cannon power to 0."""
        self.power = 0
        
    def reset_ammo(self):
        """Reset ammunition counts."""
        self.power_bullets = config.POWER_BULLETS_COUNT
        self.precision_bullets = config.PRECISION_BULLETS_COUNT
        
    def use_bullet(self, bullet_type: str) -> bool:
        """
        Try to use a bullet of given type.
        Returns True if successful, False if out of ammo.
        """
        if bullet_type == "power" and self.power_bullets > 0:
            self.power_bullets -= 1
            return True
        elif bullet_type == "precision" and self.precision_bullets > 0:
            self.precision_bullets -= 1
            return True
        return False
        
    def get_ammo_count(self, bullet_type: str) -> int:
        """Get remaining ammo count for bullet type."""
        if bullet_type == "power":
            return self.power_bullets
        elif bullet_type == "precision":
            return self.precision_bullets
        return 0


class Bullet(pygame.sprite.Sprite):
    """Bullet sprite fired from cannons."""
    
    def __init__(self, pos: Tuple[int, int], angle: float, power: float, 
                 bullet_type: str, owner_id: int):
        super().__init__()
        self.bullet_type = bullet_type
        self.owner_id = owner_id
        
        # Create bullet image
        self.radius = config.BULLET_RADIUS
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        color = config.RED if bullet_type == "power" else config.BLACK
        pygame.draw.circle(self.image, color, (self.radius, self.radius), self.radius)
        
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        
        # Apply angle error for power bullets
        actual_angle = angle
        if bullet_type == "power":
            error = random.uniform(-config.POWER_BULLET_ANGLE_ERROR, 
                                 config.POWER_BULLET_ANGLE_ERROR)
            actual_angle += error
            
        # Calculate velocity
        angle_rad = math.radians(actual_angle)
        self.vel = pygame.Vector2(
            math.cos(angle_rad) * config.BULLET_SPEED,
            -math.sin(angle_rad) * config.BULLET_SPEED
        )
        
        self.power = power
        
    def update(self):
        """Update bullet position."""
        self.pos += self.vel
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
    def is_out_of_bounds(self) -> bool:
        """Check if bullet is outside screen."""
        return (self.pos.x < 0 or self.pos.x > config.SCREEN_WIDTH or
                self.pos.y < 0 or self.pos.y > config.SCREEN_HEIGHT)
                
    def check_ball_collision(self, ball: Ball) -> bool:
        """Check collision with ball."""
        distance = (self.pos - ball.pos).length()
        return distance <= self.radius + ball.radius
        
    def apply_force_to_ball(self, ball: Ball):
        """Apply force to ball on collision."""
        # Calculate angle from bullet to ball
        angle = math.atan2(ball.pos.y - self.pos.y, ball.pos.x - self.pos.x)
        
        # Calculate force magnitude
        multiplier = config.POWER_BULLET_MULTIPLIER if self.bullet_type == "power" else 1
        magnitude = self.power * config.POWER_INCREMENT * multiplier
        
        # Apply force
        ball.apply_force(angle, magnitude)


class PowerBar(pygame.sprite.Sprite):
    """Visual power bar for cannons."""
    
    def __init__(self, cannon: Cannon):
        super().__init__()
        self.cannon = cannon
        self.width = 50
        self.height = 10
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.update_position()
        
    def update(self):
        """Update power bar display."""
        self.update_position()
        
        # Draw background
        self.image.fill(config.GRAY)
        
        # Draw power level
        if self.cannon.power > 0:
            power_width = int(self.width * (self.cannon.power / config.MAX_POWER))
            color = config.RED if self.cannon.player_num == 1 else config.BLUE
            pygame.draw.rect(self.image, color, 
                           (0, 0, power_width, self.height))
                           
    def update_position(self):
        """Update position relative to cannon."""
        self.rect.centerx = self.cannon.rect.centerx
        self.rect.top = self.cannon.rect.bottom + 20
