"""Physics module for game object movement and collision detection."""

import math
import random
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BALL_RADIUS, FRICTION, INITIAL_BALL_POSITIONS
from config import BULLET_RADIUS, BULLET_SPEED, POWER_BULLET_MULTIPLIER, POWER_INCREMENT

class PhysicsEngine:
    def __init__(self):
        self.gravity = 0  # No gravity in this game
    
    def update_ball_position(self, ball):
        """Update ball position based on velocity and apply friction."""
        ball.rect.x += ball.vel[0]
        ball.rect.y += ball.vel[1]
        
        # Apply friction to slow down the ball
        ball.vel[0] *= FRICTION
        ball.vel[1] *= FRICTION
        
        # Stop the ball if it's moving very slowly
        if abs(ball.vel[0]) < 0.1:
            ball.vel[0] = 0
        if abs(ball.vel[1]) < 0.1:
            ball.vel[1] = 0
        
        # Handle collisions with screen boundaries
        if ball.rect.top <= 0 or ball.rect.bottom >= SCREEN_HEIGHT:
            ball.vel[1] = -ball.vel[1]
            # Keep the ball within bounds
            ball.rect.y = max(BALL_RADIUS, min(SCREEN_HEIGHT - BALL_RADIUS, ball.rect.y))

    def update_bullet_position(self, bullet):
        """Update bullet position based on its angle and speed."""
        bullet.rect.x += math.cos(math.radians(bullet.angle)) * BULLET_SPEED
        bullet.rect.y -= math.sin(math.radians(bullet.angle)) * BULLET_SPEED
        
        # Return True if the bullet is out of bounds and should be removed
        if (bullet.rect.left < 0 or bullet.rect.right > SCREEN_WIDTH or
                bullet.rect.top < 0 or bullet.rect.bottom > SCREEN_HEIGHT):
            return True
        return False

    def check_bullet_ball_collision(self, bullet, ball):
        """Check if bullet has collided with the ball and apply physics if so."""
        dist = math.hypot(ball.rect.centerx - bullet.rect.centerx,
                         ball.rect.centery - bullet.rect.centery)
        
        if dist <= BALL_RADIUS + BULLET_RADIUS:
            # Calculate angle for impulse
            angle = math.atan2(ball.rect.centery - bullet.rect.centery,
                             ball.rect.centerx - bullet.rect.centerx)
            
            # Apply impulse based on bullet type
            multiplier = POWER_BULLET_MULTIPLIER if bullet.bullet_type == "power" else 1
            ball.vel[0] += math.cos(angle) * bullet.power * POWER_INCREMENT * multiplier
            ball.vel[1] += math.sin(angle) * bullet.power * POWER_INCREMENT * multiplier
            
            return True  # Collision detected
        
        return False  # No collision
    
    def reset_ball(self, ball, round_counter):
        """Reset ball position and velocity."""
        pos_index = round_counter % len(INITIAL_BALL_POSITIONS)
        new_pos = INITIAL_BALL_POSITIONS[pos_index]
        
        # Add slight randomness to starting position
        ball.rect.centerx = new_pos[0] + random.randint(-5, 5)
        ball.rect.centery = new_pos[1] + random.randint(-5, 5)
        ball.vel = [0, 0]

# Global physics engine instance
physics_engine = PhysicsEngine()
