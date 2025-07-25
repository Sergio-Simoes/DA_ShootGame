"""Input handling module for player and user interaction."""

import pygame
import random
import time
from config import MAX_POWER, POWER_BULLET_ANGLE_ERROR

class InputHandler:
    def __init__(self):
        self.quit_game = False
        self.restart_game = False
        self.scroll_offset = 0
    
    def handle_events(self, game_state):
        """Handle pygame events for the main game."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game = True
            
            if event.type == pygame.USEREVENT:
                game_state.counter -= 1
                if game_state.counter <= 0:
                    game_state.game_over = True

    def handle_game_over_events(self, restart_button):
        """Handle events for game over screen."""
        self.restart_game = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game = True
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    self.restart_game = True
        
        return self.restart_game
    
    def handle_team_selection_events(self, team_selector):
        """Handle events for team selection screen."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, None, None
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check team button clicks
                    button_y = 150
                    visible_range = range(
                        max(0, team_selector.scroll_offset),
                        min(len(team_selector.teams), team_selector.scroll_offset + team_selector.max_visible_teams)
                    )
                    
                    for i in visible_range:
                        button_rect = team_selector.get_button_rect(i)
                        
                        if button_rect.collidepoint(event.pos):
                            selected_team = team_selector.teams[i]
                            if team_selector.current_selecting == 1:
                                team_selector.team1_selected = selected_team
                                team_selector.current_selecting = 2
                            else:
                                if selected_team != team_selector.team1_selected:  # Prevent selecting same team
                                    team_selector.team2_selected = selected_team
                                    # Both teams selected, load and return
                                    return team_selector.load_team_scripts()
                
                elif event.button == 4:  # Mouse wheel up
                    team_selector.scroll_offset = max(0, team_selector.scroll_offset - 1)
                elif event.button == 5:  # Mouse wheel down
                    team_selector.scroll_offset = min(
                        len(team_selector.teams) - team_selector.max_visible_teams,
                        team_selector.scroll_offset + 1
                    )
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if team_selector.current_selecting == 2 and team_selector.team1_selected:
                        team_selector.team1_selected = None
                        team_selector.current_selecting = 1
                    elif team_selector.current_selecting == 2 and team_selector.team2_selected:
                        team_selector.team2_selected = None
        
        return True, None, None

    def process_player_command(self, player_script, cannon_pos, ball_pos, power_bullets, precision_bullets, ball_vel):
        """Execute player script to get command (angle, power, bullet_type)."""
        command = player_script(cannon_pos, ball_pos, power_bullets, precision_bullets, ball_vel)
        if command is None:
            return None
        
        angle, power, bullet_type = command
        # Validate inputs
        angle = float(angle) % 360.0
        power = max(1, min(MAX_POWER, int(power)))
        bullet_type = "power" if bullet_type == "power" else "precision"
        
        return angle, power, bullet_type

    def execute_player_shot(self, game_state, bullet_sprite_group, player_num, bullet_class):
        """Execute player's shooting command."""
        if player_num == 1:
            if game_state.player1_executing is None:
                return
                
            if game_state.cannon1_power < game_state.player1_executing[1] and game_state.cannon1_power < MAX_POWER:
                game_state.cannon1_power += 1
            else:
                angle = game_state.player1_executing[0]
                bullet_type = game_state.player1_executing[2]
                
                if bullet_type == "power":
                    angle += random.uniform(-POWER_BULLET_ANGLE_ERROR, POWER_BULLET_ANGLE_ERROR)
                
                bullet = bullet_class(
                    game_state.cannon1_pos[0], game_state.cannon1_pos[1], 
                    angle, game_state.cannon1_power, bullet_type
                )
                bullet_sprite_group.add(bullet)
                
                game_state.last_shot_time1 = pygame.time.get_ticks()
                game_state.cannon1_power = 0
                game_state.player1_executing = None
        
        elif player_num == 2:
            if game_state.player2_executing is None:
                return
                
            if game_state.cannon2_power < game_state.player2_executing[1] and game_state.cannon2_power < MAX_POWER:
                game_state.cannon2_power += 1
            else:
                angle = game_state.player2_executing[0]
                bullet_type = game_state.player2_executing[2]
                
                if bullet_type == "power":
                    angle += random.uniform(-POWER_BULLET_ANGLE_ERROR, POWER_BULLET_ANGLE_ERROR)
                
                bullet = bullet_class(
                    game_state.cannon2_pos[0], game_state.cannon2_pos[1], 
                    angle, game_state.cannon2_power, bullet_type
                )
                bullet_sprite_group.add(bullet)
                
                game_state.last_shot_time2 = pygame.time.get_ticks()
                game_state.cannon2_power = 0
                game_state.player2_executing = None

    def handle_player_turns(self, game_state, bullet_sprite_group, bullet_class):
        """Handle turns for both players based on their script outputs."""
        current_time = pygame.time.get_ticks()
        
        # Update player readiness
        game_state.player1_ready = current_time - game_state.last_shot_time1 >= game_state.turn_delay * 1000
        game_state.player2_ready = current_time - game_state.last_shot_time2 >= game_state.turn_delay * 1000
        
        # Handle player 1 execution
        if game_state.player1_executing is not None:
            self.execute_player_shot(game_state, bullet_sprite_group, 1, bullet_class)
        elif game_state.player1_ready:
            # Get player 1 command
            command = self.process_player_command(
                game_state.player_script_left,
                game_state.cannon1_pos,
                [game_state.ball.rect.centerx, game_state.ball.rect.centery],
                game_state.powerbullets1,
                game_state.precisionbullets1,
                game_state.ball.vel
            )
            if command is not None:
                angle, power, bullet_type = command
                game_state.angle1 = angle
                if self._process_player_shot_command(game_state, 1, angle, power, bullet_type):
                    game_state.player1_ready = False
        
        # Handle player 2 execution
        if game_state.player2_executing is not None:
            self.execute_player_shot(game_state, bullet_sprite_group, 2, bullet_class)
        elif game_state.player2_ready:
            # Get player 2 command
            command = self.process_player_command(
                game_state.player_script_right,
                game_state.cannon2_pos,
                [game_state.ball.rect.centerx, game_state.ball.rect.centery],
                game_state.powerbullets2,
                game_state.precisionbullets2,
                game_state.ball.vel
            )
            if command is not None:
                angle, power, bullet_type = command
                game_state.angle2 = angle
                if self._process_player_shot_command(game_state, 2, angle, power, bullet_type):
                    game_state.player2_ready = False

    def _process_player_shot_command(self, game_state, player, angle, power, bullet_type):
        """Process player shot command and update game state accordingly."""
        if player == 1:
            if bullet_type == "power" and game_state.powerbullets1 > 0:
                game_state.player1_executing = (angle, power, bullet_type)
                game_state.powerbullets1 -= 1
                game_state.bullets_used1 += 1
                return True
            elif bullet_type == "precision" and game_state.precisionbullets1 > 0:
                game_state.player1_executing = (angle, power, bullet_type)
                game_state.precisionbullets1 -= 1
                game_state.bullets_used1 += 1
                return True
        else:
            if bullet_type == "power" and game_state.powerbullets2 > 0:
                game_state.player2_executing = (angle, power, bullet_type)
                game_state.powerbullets2 -= 1
                game_state.bullets_used2 += 1
                return True
            elif bullet_type == "precision" and game_state.precisionbullets2 > 0:
                game_state.player2_executing = (angle, power, bullet_type)
                game_state.precisionbullets2 -= 1
                game_state.bullets_used2 += 1
                return True
        return False

# Global input handler instance
input_handler = InputHandler()
