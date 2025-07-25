"""
Example of extending the refactored game for manual control.
Demonstrates how the modular architecture makes it easy to add new features.
"""

import pygame
import math
from game import Game, GameState
from sprites import Bullet
import config


class ManualGame(Game):
    """Extended Game class that allows manual control for testing."""
    
    def __init__(self, player1_manual=True, player2_manual=False):
        super().__init__()
        self.player1_manual = player1_manual
        self.player2_manual = player2_manual
        self.charging = {1: False, 2: False}
        self.current_turn = 1
        
    def _handle_gameplay(self):
        """Override gameplay to add manual control."""
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.state = GameState.QUIT
            elif event.type == config.TIMER_EVENT:
                self.time_remaining -= 1
                if self.time_remaining <= 0:
                    self.state = GameState.GAME_OVER
                    
            # Manual control events
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_manual_shot_start(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                self._handle_manual_shot_release(event)
                
        # Update manual charging
        if self.charging[1] and self.player1_manual:
            self.cannons[0].charge_power(config.POWER_INCREMENT * 3)
        if self.charging[2] and self.player2_manual:
            self.cannons[1].charge_power(config.POWER_INCREMENT * 3)
            
        # Update player readiness
        current_time = pygame.time.get_ticks()
        self.input_handler.update_player_readiness(current_time)
        
        # Handle AI/manual actions
        if self.player1_manual:
            self._handle_manual_cannon_rotation(1)
        else:
            self._handle_ai_player(1)
            
        if self.player2_manual:
            self._handle_manual_cannon_rotation(2)
        else:
            self._handle_ai_player(2)
            
        # Continue with normal game update
        goal_scored = self.physics.update()
        if goal_scored == 'left':
            self.player2_score += 1
            self._reset_round()
        elif goal_scored == 'right':
            self.player1_score += 1
            self._reset_round()
            
        # Check for round end conditions
        if self.physics.check_round_end_condition():
            closest = self.physics.determine_closest_cannon()
            if closest == 1:
                self.player2_score += 1
            else:
                self.player1_score += 1
            self._reset_round()
            
        # Check for game over
        if self.player1_score >= config.WINNING_SCORE or self.player2_score >= config.WINNING_SCORE:
            self.state = GameState.GAME_OVER
            
        # Render game
        self._render_game()
        
    def _handle_manual_shot_start(self, event):
        """Handle start of manual shot charging."""
        if self.current_turn == 1 and self.player1_manual and self.input_handler.player1_ready:
            if event.button == 1 and self.cannons[0].power_bullets > 0:
                self.charging[1] = True
            elif event.button == 3 and self.cannons[0].precision_bullets > 0:
                self.charging[1] = True
        elif self.current_turn == 2 and self.player2_manual and self.input_handler.player2_ready:
            if event.button == 1 and self.cannons[1].power_bullets > 0:
                self.charging[2] = True
            elif event.button == 3 and self.cannons[1].precision_bullets > 0:
                self.charging[2] = True
                
    def _handle_manual_shot_release(self, event):
        """Handle release of manual shot."""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        if self.charging[1] and self.player1_manual:
            # Calculate angle
            angle = math.degrees(math.atan2(self.cannons[0].pos.y - mouse_y, 
                                           mouse_x - self.cannons[0].pos.x))
            
            # Determine bullet type
            bullet_type = "power" if event.button == 1 else "precision"
            
            # Fire bullet
            if self.cannons[0].use_bullet(bullet_type):
                bullet = Bullet(
                    (self.cannons[0].pos.x, self.cannons[0].pos.y),
                    angle, self.cannons[0].power, bullet_type, 1
                )
                self.sprites.add(bullet)
                self.physics.add_bullet(bullet)
                self.bullets_used1 += 1
                self.input_handler.last_shot_time1 = pygame.time.get_ticks()
                self.input_handler.player1_ready = False
                
            self.cannons[0].reset_power()
            self.charging[1] = False
            self.current_turn = 2
            
        elif self.charging[2] and self.player2_manual:
            # Calculate angle
            angle = math.degrees(math.atan2(self.cannons[1].pos.y - mouse_y, 
                                           mouse_x - self.cannons[1].pos.x))
            
            # Determine bullet type
            bullet_type = "power" if event.button == 1 else "precision"
            
            # Fire bullet
            if self.cannons[1].use_bullet(bullet_type):
                bullet = Bullet(
                    (self.cannons[1].pos.x, self.cannons[1].pos.y),
                    angle, self.cannons[1].power, bullet_type, 2
                )
                self.sprites.add(bullet)
                self.physics.add_bullet(bullet)
                self.bullets_used2 += 1
                self.input_handler.last_shot_time2 = pygame.time.get_ticks()
                self.input_handler.player2_ready = False
                
            self.cannons[1].reset_power()
            self.charging[2] = False
            self.current_turn = 1
            
    def _handle_manual_cannon_rotation(self, player_num):
        """Rotate cannon to follow mouse."""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        cannon = self.cannons[player_num - 1]
        
        # Calculate angle to mouse
        angle = math.degrees(math.atan2(cannon.pos.y - mouse_y, mouse_x - cannon.pos.x))
        cannon.rotate_to_angle(angle)
        
    def _handle_ai_player(self, player_num):
        """Handle AI-controlled player."""
        if player_num == 1:
            if self.player1_executing:
                self._execute_player1_shot()
            elif self.input_handler.player1_ready:
                self._handle_player_actions()
        else:
            if self.player2_executing:
                self._execute_player2_shot()
            elif self.input_handler.player2_ready:
                self._handle_player_actions()
                
    def _render_game(self):
        """Override to add manual control indicators."""
        super()._render_game()
        
        # Draw turn indicator for manual players
        if (self.current_turn == 1 and self.player1_manual) or \
           (self.current_turn == 2 and self.player2_manual):
            font = asset_manager.get_font('default', 36)
            turn_text = font.render(f"Player {self.current_turn}'s Turn", True, config.BLACK)
            turn_rect = turn_text.get_rect(centerx=config.SCREEN_WIDTH // 2, y=50)
            self.screen.blit(turn_text, turn_rect)
            
        # Draw control instructions
        if self.player1_manual or self.player2_manual:
            font = asset_manager.get_font('bullet_count', 24)
            instructions = [
                "Left Click: Power Bullet",
                "Right Click: Precision Bullet",
                "Hold to Charge Power"
            ]
            y = 140
            for instruction in instructions:
                text = font.render(instruction, True, config.WHITE)
                text_rect = text.get_rect(centerx=config.SCREEN_WIDTH // 2, y=y)
                self.screen.blit(text, text_rect)
                y += 25


def main():
    """Run the game with manual control for player 1."""
    try:
        # Create game with player 1 as manual, player 2 as AI
        game = ManualGame(player1_manual=True, player2_manual=False)
        game.run()
    except Exception as e:
        print(f"Game error: {e}")
        pygame.quit()
        raise


if __name__ == "__main__":
    main()
