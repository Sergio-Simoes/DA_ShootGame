"""Main game module with Game class orchestration."""

import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_TIME_SEC, WINNING_SCORE,
    TURN_DELAY, POWER_BULLET_COUNT, PRECISION_BULLET_COUNT,
    CANNON1_POS, CANNON2_POS
)
from sprites import Ball, Cannon, Bullet
from asset_manager import asset_manager
from physics import physics_engine
from renderer import Renderer
from input_handler import input_handler
from team_selector import TeamSelector

class Game:
    def __init__(self):
        """Initialize the game and its components."""
        pygame.init()
        
        # Create screen
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Turn-Based Football Game")
        self.clock = pygame.time.Clock()
        
        # Load assets
        asset_manager.preload_assets()
        
        # Create renderer
        self.renderer = Renderer(self.screen)
        
        # Select teams using the team selector
        self.team_selector = TeamSelector()
        player_script_left, player_script_right = self.team_selector.run()
        
        if player_script_left is None or player_script_right is None:
            raise SystemExit("Team selection cancelled")
            
        # Initialize game state
        self.init_game(player_script_left, player_script_right)
    
    def init_game(self, player_script_left, player_script_right):
        """Initialize or reset game state."""
        # Game state
        self.running = True
        self.game_over = False
        self.counter = GAME_TIME_SEC
        pygame.time.set_timer(pygame.USEREVENT, 1000)
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        
        # Create ball
        self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.all_sprites.add(self.ball)
        
        # Create cannons
        self.cannon1 = Cannon(CANNON1_POS[0], CANNON1_POS[1], 1)
        self.cannon2 = Cannon(CANNON2_POS[0], CANNON2_POS[1], 2)
        self.all_sprites.add(self.cannon1, self.cannon2)
        
        # Cannon positions (used by player scripts)
        self.cannon1_pos = CANNON1_POS
        self.cannon2_pos = CANNON2_POS
        
        # Cannon angles and powers
        self.angle1 = 45
        self.angle2 = 135
        self.cannon1_power = 0
        self.cannon2_power = 0
        
        # Bullet counts
        self.powerbullets1 = POWER_BULLET_COUNT
        self.powerbullets2 = POWER_BULLET_COUNT
        self.precisionbullets1 = PRECISION_BULLET_COUNT
        self.precisionbullets2 = PRECISION_BULLET_COUNT
        self.bullets_used1 = 0
        self.bullets_used2 = 0
        
        # Turn management
        self.turn_delay = TURN_DELAY
        self.player1_ready = False
        self.player2_ready = False
        self.last_shot_time1 = 0
        self.last_shot_time2 = 0
        self.player1_executing = None
        self.player2_executing = None
        
        # Player scripts
        self.player_script_left = player_script_left
        self.player_script_right = player_script_right 
        
        # Score and winning conditions
        self.player1_score = 0
        self.player2_score = 0
        self.winning_score = WINNING_SCORE
        self.round_counter = 0
    
    def run(self):
        """Main game loop."""
        while self.running:
            if self.game_over:
                restart_button = self.renderer.draw_game_over_screen(self)
                if input_handler.handle_game_over_events(restart_button):
                    self.game_over = False
                    self.restart_game()
                
                pygame.display.flip()
                self.clock.tick(FPS)
                continue
            
            # Handle events
            input_handler.handle_events(self)
            if input_handler.quit_game:
                self.running = False
            
            # Handle player turns and script execution
            input_handler.handle_player_turns(self, self.bullet_sprites, Bullet)
            
            # Update game state
            self.update()
            
            # Render frame
            self.render()
            
            # Cap frame rate
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
    
    def update(self):
        """Update game state and physics."""
        # Update ball physics
        physics_engine.update_ball_position(self.ball)
        
        # Update cannon angles
        self.cannon1.angle = self.angle1
        self.cannon2.angle = self.angle2
        
        # Update bullets and check collisions
        self.handle_bullets()
        
        # Check win conditions
        self.check_win_conditions()
    
    def render(self):
        """Render the current game state."""
        self.renderer.draw_field()
        self.renderer.draw_cannon(self.cannon1)
        self.renderer.draw_cannon(self.cannon2)
        self.renderer.draw_ball(self.ball)
        
        for bullet in self.bullet_sprites:
            self.renderer.draw_bullet(bullet)
        
        self.renderer.draw_power_bar(self.cannon1_pos[0], self.cannon1_pos[1], self.cannon1_power, (255, 0, 0))
        self.renderer.draw_power_bar(self.cannon2_pos[0], self.cannon2_pos[1], self.cannon2_power, (0, 0, 255))
        
        self.renderer.draw_ui(self)
    
    def handle_bullets(self):
        """Update bullet positions and check for collisions."""
        for bullet in list(self.bullet_sprites):
            # Update bullet position
            if physics_engine.update_bullet_position(bullet):
                bullet.kill()  # Remove bullets that are off-screen
                continue
            
            # Check for collision with the ball
            if physics_engine.check_bullet_ball_collision(bullet, self.ball):
                bullet.kill()
    
    def check_win_conditions(self):
        """Check for various winning conditions."""
        # Check if ball went out of bounds horizontally
        if self.ball.rect.left <= 0:
            self.player2_score += 1
            self.reset_ball()
        elif self.ball.rect.right >= SCREEN_WIDTH:
            self.player1_score += 1
            self.reset_ball()
        
        # Check for game-ending conditions
        if self.player1_score >= self.winning_score or self.player2_score >= self.winning_score:
            self.game_over = True
        
        # Check if ball is not moving and both players are out of bullets
        if (not self.ball.is_moving and 
            self.powerbullets1 == 0 and self.powerbullets2 == 0 and 
            self.precisionbullets1 == 0 and self.precisionbullets2 == 0):
            if abs(self.ball.rect.centerx - self.cannon1_pos[0]) > abs(self.ball.rect.centerx - self.cannon2_pos[0]):
                self.player1_score += 1
            else:
                self.player2_score += 1
            self.reset_ball()
    
    def reset_ball(self):
        """Reset ball position and game state for the next round."""
        self.round_counter += 1
        physics_engine.reset_ball(self.ball, self.round_counter)
        
        # Reset bullet counts
        self.powerbullets1 = POWER_BULLET_COUNT
        self.powerbullets2 = POWER_BULLET_COUNT
        self.precisionbullets1 = PRECISION_BULLET_COUNT
        self.precisionbullets2 = PRECISION_BULLET_COUNT
        
        # Clear bullets and execution state
        for bullet in self.bullet_sprites:
            bullet.kill()
        
        self.player1_executing = None
        self.player2_executing = None
        self.cannon1_power = 0
        self.cannon2_power = 0
    
    def restart_game(self):
        """Restart the game entirely."""
        self.round_counter = 0
        self.bullets_used1 = 0
        self.bullets_used2 = 0
        self.counter = GAME_TIME_SEC
        self.player1_score = 0
        self.player2_score = 0
        self.reset_ball()

def main():
    """Entry point function."""
    try:
        game = Game()
        game.run()
    except SystemExit as e:
        print(e)
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
