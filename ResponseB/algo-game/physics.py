"""
Physics module for the Football Game.
Handles all physics calculations and collision detection.
"""

import pygame
import math
from typing import List, Tuple, Optional
import config
from sprites import Ball, Bullet, Cannon


class PhysicsEngine:
    """Manages physics simulation for the game."""
    
    def __init__(self):
        self.ball: Optional[Ball] = None
        self.bullets: pygame.sprite.Group = pygame.sprite.Group()
        self.cannons: List[Cannon] = []
        
    def set_ball(self, ball: Ball):
        """Set the ball for physics simulation."""
        self.ball = ball
        
    def set_cannons(self, cannons: List[Cannon]):
        """Set the cannons for physics simulation."""
        self.cannons = cannons
        
    def add_bullet(self, bullet: Bullet):
        """Add a bullet to the physics simulation."""
        self.bullets.add(bullet)
        
    def update(self) -> Optional[str]:
        """
        Update all physics objects.
        Returns 'left' or 'right' if ball scored, None otherwise.
        """
        goal_scored = None
        
        # Update ball
        if self.ball:
            self.ball.update()
            goal_scored = self.ball.check_boundaries()
            
        # Update bullets
        for bullet in self.bullets:
            bullet.update()
            
            # Remove out-of-bounds bullets
            if bullet.is_out_of_bounds():
                bullet.kill()
                continue
                
            # Check bullet-ball collision
            if self.ball and bullet.check_ball_collision(self.ball):
                bullet.apply_force_to_ball(self.ball)
                bullet.kill()
                
        return goal_scored
        
    def get_ball_position(self) -> Tuple[int, int]:
        """Get current ball position."""
        if self.ball:
            return (int(self.ball.pos.x), int(self.ball.pos.y))
        return (0, 0)
        
    def get_ball_velocity(self) -> Tuple[float, float]:
        """Get current ball velocity."""
        if self.ball:
            return (self.ball.vel.x, self.ball.vel.y)
        return (0.0, 0.0)
        
    def is_ball_moving(self) -> bool:
        """Check if ball is still moving."""
        return self.ball.is_moving() if self.ball else False
        
    def reset_ball(self, position: Tuple[int, int]):
        """Reset ball to given position."""
        if self.ball:
            self.ball.reset(position)
            
    def clear_bullets(self):
        """Remove all bullets."""
        self.bullets.empty()
        
    def calculate_angle_to_target(self, from_pos: Tuple[int, int], 
                                  to_pos: Tuple[int, int]) -> float:
        """Calculate angle in degrees from one position to another."""
        dx = to_pos[0] - from_pos[0]
        dy = from_pos[1] - to_pos[1]  # Inverted because y increases downward
        return math.degrees(math.atan2(dy, dx))
        
    def predict_ball_position(self, time_steps: int) -> Tuple[int, int]:
        """
        Predict where the ball will be after given time steps.
        Simple prediction based on current velocity and friction.
        """
        if not self.ball:
            return (0, 0)
            
        pos = pygame.Vector2(self.ball.pos)
        vel = pygame.Vector2(self.ball.vel)
        
        for _ in range(time_steps):
            pos += vel
            vel *= config.BALL_FRICTION
            
            # Check boundaries
            if pos.y - config.BALL_RADIUS <= 0 or pos.y + config.BALL_RADIUS >= config.SCREEN_HEIGHT:
                vel.y = -vel.y
                
        return (int(pos.x), int(pos.y))
        
    def check_round_end_condition(self) -> bool:
        """
        Check if round should end due to physics conditions.
        Returns True if ball is stationary and all bullets are gone.
        """
        ball_stopped = not self.is_ball_moving()
        no_bullets = len(self.bullets) == 0
        
        if ball_stopped and no_bullets:
            # Check if all cannons are out of ammo
            all_out_of_ammo = all(
                cannon.power_bullets == 0 and cannon.precision_bullets == 0
                for cannon in self.cannons
            )
            return all_out_of_ammo
            
        return False
        
    def determine_closest_cannon(self) -> Optional[int]:
        """
        Determine which cannon the ball is closer to.
        Returns player number (1 or 2) or None.
        """
        if not self.ball or not self.cannons or len(self.cannons) < 2:
            return None
            
        ball_x = self.ball.pos.x
        dist_to_cannon1 = abs(ball_x - self.cannons[0].pos.x)
        dist_to_cannon2 = abs(ball_x - self.cannons[1].pos.x)
        
        if dist_to_cannon1 < dist_to_cannon2:
            return 1
        else:
            return 2
