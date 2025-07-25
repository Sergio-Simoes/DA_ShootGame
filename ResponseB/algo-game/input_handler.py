"""
Input handler module for the Football Game.
Manages all user input and AI script execution.
"""

import pygame
from typing import Optional, Tuple, Callable, List
import config


class InputHandler:
    """Handles all input for the game."""
    
    def __init__(self):
        self.player1_script: Optional[Callable] = None
        self.player2_script: Optional[Callable] = None
        self.player1_ready = True
        self.player2_ready = True
        self.last_shot_time1 = 0
        self.last_shot_time2 = 0
        
    def set_player_scripts(self, script1: Callable, script2: Callable):
        """Set the AI scripts for both players."""
        self.player1_script = script1
        self.player2_script = script2
        
    def update_player_readiness(self, current_time: int):
        """Update whether players are ready to shoot based on turn delay."""
        self.player1_ready = current_time - self.last_shot_time1 >= config.TURN_DELAY * 1000
        self.player2_ready = current_time - self.last_shot_time2 >= config.TURN_DELAY * 1000
        
    def get_player1_command(self, cannon_pos: Tuple[int, int], ball_pos: Tuple[int, int],
                          power_bullets: int, precision_bullets: int, 
                          ball_vel: Tuple[float, float]) -> Optional[Tuple[float, float, str]]:
        """Get command from player 1 AI script."""
        if self.player1_ready and self.player1_script:
            try:
                command = self.player1_script(cannon_pos, ball_pos, power_bullets, 
                                            precision_bullets, ball_vel)
                if command:
                    self.last_shot_time1 = pygame.time.get_ticks()
                    self.player1_ready = False
                return command
            except Exception as e:
                print(f"Error in player 1 script: {e}")
        return None
        
    def get_player2_command(self, cannon_pos: Tuple[int, int], ball_pos: Tuple[int, int],
                          power_bullets: int, precision_bullets: int,
                          ball_vel: Tuple[float, float]) -> Optional[Tuple[float, float, str]]:
        """Get command from player 2 AI script."""
        if self.player2_ready and self.player2_script:
            try:
                command = self.player2_script(cannon_pos, ball_pos, power_bullets,
                                            precision_bullets, ball_vel)
                if command:
                    self.last_shot_time2 = pygame.time.get_ticks()
                    self.player2_ready = False
                return command
            except Exception as e:
                print(f"Error in player 2 script: {e}")
        return None
        
    def reset_timers(self):
        """Reset shot timers."""
        self.last_shot_time1 = 0
        self.last_shot_time2 = 0
        self.player1_ready = True
        self.player2_ready = True


class TeamSelectionInput:
    """Handles input for team selection screen."""
    
    def __init__(self):
        self.selected_index: Optional[int] = None
        
    def handle_mouse_click(self, pos: Tuple[int, int], button_rects: List[pygame.Rect]) -> Optional[int]:
        """
        Handle mouse click on team selection.
        Returns index of clicked button or None.
        """
        for i, rect in enumerate(button_rects):
            if rect.collidepoint(pos):
                return i
        return None
        
    def handle_scroll(self, direction: int, max_teams: int, current_offset: int) -> int:
        """
        Handle scroll wheel input.
        Returns new scroll offset.
        """
        if direction < 0:  # Scroll up
            return max(0, current_offset - 1)
        elif direction > 0:  # Scroll down
            return min(max_teams - config.MAX_VISIBLE_TEAMS, current_offset + 1)
        return current_offset


class GameOverInput:
    """Handles input for game over screen."""
    
    def handle_restart_click(self, pos: Tuple[int, int], restart_button: pygame.Rect) -> bool:
        """
        Check if restart button was clicked.
        Returns True if restart clicked.
        """
        return restart_button.collidepoint(pos)
