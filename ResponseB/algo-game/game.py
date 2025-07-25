"""
Main game module for the Football Game.
Contains the Game class that orchestrates all game systems.
"""

import pygame
import os
import importlib
import random
from typing import Optional, Tuple, Callable
import config
from assets import asset_manager
from sprites import Ball, Cannon, Bullet, PowerBar
from physics import PhysicsEngine
from renderer import Renderer
from input_handler import InputHandler, TeamSelectionInput, GameOverInput


class GameState:
    """Enum-like class for game states."""
    TEAM_SELECTION = "team_selection"
    PLAYING = "playing"
    GAME_OVER = "game_over"
    QUIT = "quit"


class Game:
    """Main game class that orchestrates all game systems."""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("Turn-Based Football Game")
        
        # Core systems
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen)
        self.physics = PhysicsEngine()
        self.input_handler = InputHandler()
        
        # Load assets
        asset_manager.load_all_assets()
        
        # Game state
        self.state = GameState.TEAM_SELECTION
        self.running = True
        
        # Team selection
        self.teams = self._get_team_scripts()
        self.team_selector = TeamSelector(self.teams)
        
        # Game objects (initialized after team selection)
        self.sprites = pygame.sprite.Group()
        self.ball: Optional[Ball] = None
        self.cannons = []
        self.bullets = pygame.sprite.Group()
        self.power_bars = []
        
        # Game statistics
        self.player1_score = 0
        self.player2_score = 0
        self.bullets_used1 = 0
        self.bullets_used2 = 0
        self.round_counter = 0
        self.time_remaining = config.GAME_TIME
        
        # Execution state for charging shots
        self.player1_executing: Optional[Tuple[float, float, str]] = None
        self.player2_executing: Optional[Tuple[float, float, str]] = None
        
        # Set up timer event
        pygame.time.set_timer(config.TIMER_EVENT, 1000)
        
    def _get_team_scripts(self):
        """Load available team scripts."""
        teams = []
        teams_dir = "teams"
        
        if not os.path.exists(teams_dir):
            print(f"Warning: {teams_dir} directory not found")
            return teams
            
        for file in os.listdir(teams_dir):
            if file.endswith(".py") and not file.startswith("__"):
                team_name = file[:-3]  # Remove .py extension
                teams.append(team_name)
                
        return sorted(teams)
        
    def init_game_objects(self, player1_script: Callable, player2_script: Callable):
        """Initialize game objects after team selection."""
        # Set player scripts
        self.input_handler.set_player_scripts(player1_script, player2_script)
        
        # Create ball
        initial_pos = config.BALL_SPAWN_POSITIONS[0]
        self.ball = Ball(initial_pos)
        self.sprites.add(self.ball)
        self.physics.set_ball(self.ball)
        
        # Create cannons
        cannon1 = Cannon(config.CANNON1_POS, 1)
        cannon2 = Cannon(config.CANNON2_POS, 2)
        self.cannons = [cannon1, cannon2]
        self.sprites.add(cannon1, cannon2)
        self.physics.set_cannons(self.cannons)
        
        # Create power bars
        self.power_bars = [PowerBar(cannon1), PowerBar(cannon2)]
        
        # Reset scores
        self.player1_score = 0
        self.player2_score = 0
        self.bullets_used1 = 0
        self.bullets_used2 = 0
        self.round_counter = 0
        self.time_remaining = config.GAME_TIME
        
    def run(self):
        """Main game loop."""
        while self.running:
            if self.state == GameState.TEAM_SELECTION:
                self._handle_team_selection()
            elif self.state == GameState.PLAYING:
                self._handle_gameplay()
            elif self.state == GameState.GAME_OVER:
                self._handle_game_over()
                
            pygame.display.flip()
            self.clock.tick(config.FPS)
            
        pygame.quit()
        
    def _handle_team_selection(self):
        """Handle team selection state."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.state = GameState.QUIT
                
            result = self.team_selector.handle_event(event)
            if result:
                script1, script2 = result
                self.init_game_objects(script1, script2)
                self.state = GameState.PLAYING
                
        # Render team selection
        button_rects = self.renderer.draw_team_selection(
            self.team_selector.teams,
            self.team_selector.scroll_offset,
            self.team_selector.team1_selected,
            self.team_selector.team2_selected,
            self.team_selector.current_selecting
        )
        self.team_selector.button_rects = button_rects
        
    def _handle_gameplay(self):
        """Handle main gameplay state."""
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.state = GameState.QUIT
            elif event.type == config.TIMER_EVENT:
                self.time_remaining -= 1
                if self.time_remaining <= 0:
                    self.state = GameState.GAME_OVER
                    
        # Update player readiness
        current_time = pygame.time.get_ticks()
        self.input_handler.update_player_readiness(current_time)
        
        # Handle player actions
        self._handle_player_actions()
        
        # Update physics
        goal_scored = self.physics.update()
        if goal_scored == 'left':
            self.player2_score += 1
            self._reset_round()
        elif goal_scored == 'right':
            self.player1_score += 1
            self._reset_round()
            
        # Check for round end conditions
        if self.physics.check_round_end_condition():
            # Award point to player whose goal the ball is farther from
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
        
    def _handle_player_actions(self):
        """Handle player AI script execution and shot charging."""
        # Handle player 1
        if self.player1_executing:
            self._execute_player1_shot()
        elif self.input_handler.player1_ready:
            command = self.input_handler.get_player1_command(
                (self.cannons[0].pos.x, self.cannons[0].pos.y),
                self.physics.get_ball_position(),
                self.cannons[0].power_bullets,
                self.cannons[0].precision_bullets,
                self.physics.get_ball_velocity()
            )
            if command:
                angle, power, bullet_type = command
                if self.cannons[0].use_bullet(bullet_type):
                    self.player1_executing = (angle, power, bullet_type)
                    self.bullets_used1 += 1
                    self.cannons[0].rotate_to_angle(angle)
                    
        # Handle player 2
        if self.player2_executing:
            self._execute_player2_shot()
        elif self.input_handler.player2_ready:
            command = self.input_handler.get_player2_command(
                (self.cannons[1].pos.x, self.cannons[1].pos.y),
                self.physics.get_ball_position(),
                self.cannons[1].power_bullets,
                self.cannons[1].precision_bullets,
                self.physics.get_ball_velocity()
            )
            if command:
                angle, power, bullet_type = command
                if self.cannons[1].use_bullet(bullet_type):
                    self.player2_executing = (angle, power, bullet_type)
                    self.bullets_used2 += 1
                    self.cannons[1].rotate_to_angle(angle)
                    
    def _execute_player1_shot(self):
        """Execute player 1's shot with power charging."""
        angle, target_power, bullet_type = self.player1_executing
        
        if self.cannons[0].power < target_power and self.cannons[0].power < config.MAX_POWER:
            self.cannons[0].charge_power(1)
        else:
            # Fire bullet
            bullet = Bullet(
                (self.cannons[0].pos.x, self.cannons[0].pos.y),
                angle, self.cannons[0].power, bullet_type, 1
            )
            self.sprites.add(bullet)
            self.physics.add_bullet(bullet)
            
            # Reset
            self.cannons[0].reset_power()
            self.player1_executing = None
            
    def _execute_player2_shot(self):
        """Execute player 2's shot with power charging."""
        angle, target_power, bullet_type = self.player2_executing
        
        if self.cannons[1].power < target_power and self.cannons[1].power < config.MAX_POWER:
            self.cannons[1].charge_power(1)
        else:
            # Fire bullet
            bullet = Bullet(
                (self.cannons[1].pos.x, self.cannons[1].pos.y),
                angle, self.cannons[1].power, bullet_type, 2
            )
            self.sprites.add(bullet)
            self.physics.add_bullet(bullet)
            
            # Reset
            self.cannons[1].reset_power()
            self.player2_executing = None
            
    def _reset_round(self):
        """Reset for next round."""
        self.round_counter += 1
        
        # Reset ball position
        pos_index = self.round_counter % len(config.BALL_SPAWN_POSITIONS)
        base_pos = config.BALL_SPAWN_POSITIONS[pos_index]
        randomized_pos = (
            base_pos[0] + random.randint(-5, 5),
            base_pos[1] + random.randint(-5, 5)
        )
        self.physics.reset_ball(randomized_pos)
        
        # Clear bullets
        self.physics.clear_bullets()
        for bullet in self.bullets:
            bullet.kill()
            
        # Reset cannon ammo and power
        for cannon in self.cannons:
            cannon.reset_ammo()
            cannon.reset_power()
            
        # Reset execution state
        self.player1_executing = None
        self.player2_executing = None
        self.input_handler.reset_timers()
        
    def _render_game(self):
        """Render the game scene."""
        self.renderer.draw_field()
        self.renderer.draw_sprites(self.sprites)
        self.renderer.draw_power_bars(self.power_bars)
        self.renderer.draw_scores(self.player1_score, self.player2_score)
        self.renderer.draw_timer(self.time_remaining)
        self.renderer.draw_bullet_counts(self.cannons)
        self.renderer.draw_fps(int(self.clock.get_fps()))
        
    def _handle_game_over(self):
        """Handle game over state."""
        restart_button = self.renderer.draw_game_over_screen(
            self.player1_score, self.player2_score,
            self.bullets_used1, self.bullets_used2
        )
        
        game_over_input = GameOverInput()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.state = GameState.QUIT
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_over_input.handle_restart_click(event.pos, restart_button):
                    # Reset game and go back to team selection
                    self.state = GameState.TEAM_SELECTION
                    self.team_selector.reset()
                    

class TeamSelector:
    """Handles team selection logic."""
    
    def __init__(self, teams):
        self.teams = teams
        self.team1_selected: Optional[str] = None
        self.team2_selected: Optional[str] = None
        self.current_selecting = 1
        self.scroll_offset = 0
        self.button_rects = []
        self.input_handler = TeamSelectionInput()
        
    def handle_event(self, event) -> Optional[Tuple[Callable, Callable]]:
        """
        Handle events for team selection.
        Returns (script1, script2) when both teams are selected, None otherwise.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                visible_start = self.scroll_offset
                visible_end = min(len(self.teams), self.scroll_offset + config.MAX_VISIBLE_TEAMS)
                
                index = self.input_handler.handle_mouse_click(event.pos, self.button_rects)
                if index is not None:
                    actual_index = self.scroll_offset + index
                    if actual_index < len(self.teams):
                        selected_team = self.teams[actual_index]
                        
                        if self.current_selecting == 1:
                            self.team1_selected = selected_team
                            self.current_selecting = 2
                        else:
                            if selected_team != self.team1_selected:
                                self.team2_selected = selected_team
                                return self._load_team_scripts()
                                
            elif event.button == 4:  # Mouse wheel up
                self.scroll_offset = self.input_handler.handle_scroll(-1, len(self.teams), self.scroll_offset)
            elif event.button == 5:  # Mouse wheel down
                self.scroll_offset = self.input_handler.handle_scroll(1, len(self.teams), self.scroll_offset)
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.current_selecting == 2:
                    self.team1_selected = None
                    self.current_selecting = 1
                    
        return None
        
    def _load_team_scripts(self) -> Tuple[Callable, Callable]:
        """Load the selected team scripts."""
        try:
            team1_module = importlib.import_module(f"teams.{self.team1_selected}")
            team2_module = importlib.import_module(f"teams.{self.team2_selected}")
            return team1_module.player_script, team2_module.player_script
        except Exception as e:
            print(f"Error loading team scripts: {e}")
            raise
            
    def reset(self):
        """Reset team selection."""
        self.team1_selected = None
        self.team2_selected = None
        self.current_selecting = 1
        self.scroll_offset = 0


def main():
    """Entry point for the game."""
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Game error: {e}")
        pygame.quit()
        raise


if __name__ == "__main__":
    main()
