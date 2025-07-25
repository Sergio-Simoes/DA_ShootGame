"""Team selection module for choosing player scripts."""

import os
import importlib
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BG_COLOR, PRIMARY, HOVER, WHITE,
    TITLE_FONT_SIZE, TEAM_FONT_SIZE, MAX_VISIBLE_TEAMS, BUTTON_HEIGHT, BUTTON_SPACING
)
from asset_manager import asset_manager
from input_handler import input_handler

class TeamSelector:
    def __init__(self):
        self.WIDTH = SCREEN_WIDTH
        self.HEIGHT = SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()
        self.FPS = FPS
        
        # Colors
        self.WHITE = WHITE
        self.BLACK = (0, 0, 0)
        self.PRIMARY = PRIMARY
        self.HOVER = HOVER
        self.BG_COLOR = BG_COLOR
        
        # Fonts
        self.title_font = asset_manager.get_font('title', TITLE_FONT_SIZE)
        self.team_font = asset_manager.get_font('game', TEAM_FONT_SIZE)
        
        # Selection state
        self.team1_selected = None
        self.team2_selected = None
        self.current_selecting = 1  # 1 for player 1, 2 for player 2
        
        # Load teams
        self.teams = self.get_team_scripts()
        self.scroll_offset = 0
        self.max_visible_teams = MAX_VISIBLE_TEAMS
        self.button_height = BUTTON_HEIGHT
        self.button_spacing = BUTTON_SPACING

    def get_team_scripts(self):
        """Find available team scripts."""
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

    def draw_selection_screen(self):
        """Draw the team selection interface."""
        # Draw gradient background
        for y in range(self.HEIGHT):
            alpha = y / self.HEIGHT
            color = [int(self.BG_COLOR[i] + (self.PRIMARY[i] - self.BG_COLOR[i]) * alpha * 0.15) for i in range(3)]
            pygame.draw.line(self.screen, tuple(color), (0, y), (self.WIDTH, y))

        # Draw title
        title_text = self.title_font.render("Select Teams", True, self.WHITE)
        title_rect = title_text.get_rect(center=(self.WIDTH // 2, 50))
        self.screen.blit(title_text, title_rect)

        # Draw player selection status
        status_text = f"Selecting Player {self.current_selecting}"
        status_surface = self.team_font.render(status_text, True, self.WHITE)
        status_rect = status_surface.get_rect(center=(self.WIDTH // 2, 100))
        self.screen.blit(status_surface, status_rect)

        # Draw team buttons
        visible_range = range(
            max(0, self.scroll_offset),
            min(len(self.teams), self.scroll_offset + self.max_visible_teams)
        )

        for i in visible_range:
            team_name = self.teams[i]
            button_rect = self.get_button_rect(i)
            
            # Check if mouse is hovering over button
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = button_rect.collidepoint(mouse_pos)
            is_selected = (team_name == self.team1_selected or team_name == self.team2_selected)
            
            # Draw button with appropriate color
            button_color = self.HOVER if is_hovered else self.PRIMARY
            if is_selected:
                button_color = (0, 255, 0)  # Green for selected
                
            pygame.draw.rect(self.screen, button_color, button_rect, border_radius=10)
            
            # Draw team name
            team_text = self.team_font.render(team_name, True, self.WHITE)
            text_rect = team_text.get_rect(center=button_rect.center)
            self.screen.blit(team_text, text_rect)

        # Draw scroll indicators if needed
        if len(self.teams) > self.max_visible_teams:
            if self.scroll_offset > 0:
                pygame.draw.polygon(self.screen, self.WHITE, [
                    (self.WIDTH // 2, 140),
                    (self.WIDTH // 2 - 10, 130),
                    (self.WIDTH // 2 + 10, 130)
                ])
            if self.scroll_offset + self.max_visible_teams < len(self.teams):
                bottom_y = 150 + (self.max_visible_teams * (self.button_height + self.button_spacing))
                pygame.draw.polygon(self.screen, self.WHITE, [
                    (self.WIDTH // 2, bottom_y + 20),
                    (self.WIDTH // 2 - 10, bottom_y + 10),
                    (self.WIDTH // 2 + 10, bottom_y + 10)
                ])

        # Draw selected teams
        if self.team1_selected:
            text = f"Player 1: {self.team1_selected}"
            surface = self.team_font.render(text, True, self.WHITE)
            self.screen.blit(surface, (20, self.HEIGHT - 60))
        
        if self.team2_selected:
            text = f"Player 2: {self.team2_selected}"
            surface = self.team_font.render(text, True, self.WHITE)
            self.screen.blit(surface, (20, self.HEIGHT - 30))

    def get_button_rect(self, index):
        """Get the rectangle for a team button by index."""
        button_y = 150
        return pygame.Rect(
            self.WIDTH // 4,
            button_y + (index - self.scroll_offset) * (self.button_height + self.button_spacing),
            self.WIDTH // 2,
            self.button_height
        )

    def load_team_scripts(self):
        """Load the selected team scripts."""
        try:
            # Import the selected team scripts
            team1_module = importlib.import_module(f"teams.{self.team1_selected}")
            team2_module = importlib.import_module(f"teams.{self.team2_selected}")
            
            return False, team1_module.player_script, team2_module.player_script
        except Exception as e:
            print(f"Error loading team scripts: {e}")
            return True, None, None

    def run(self):
        """Run the team selection process."""
        running = True
        while running:
            self.screen.fill(self.BG_COLOR)
            self.draw_selection_screen()
            running, script1, script2 = input_handler.handle_team_selection_events(self)
            
            if script1 and script2:
                return script1, script2
            
            pygame.display.flip()
            self.clock.tick(self.FPS)
        
        return None, None
