"""
Renderer module for the Football Game.
Handles all drawing operations.
"""

import pygame
import math
from typing import List, Optional, Tuple
import config
from assets import asset_manager
from sprites import Ball, Cannon, Bullet, PowerBar


class Renderer:
    """Handles all rendering for the game."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.fonts = {}
        self._load_fonts()
        
    def _load_fonts(self):
        """Load fonts for rendering."""
        self.fonts['title'] = asset_manager.get_font('title', config.TITLE_FONT_SIZE)
        self.fonts['team'] = asset_manager.get_font('team', config.TEAM_FONT_SIZE)
        self.fonts['default'] = asset_manager.get_font('default', 36)
        self.fonts['bullet_count'] = asset_manager.get_font('bullet_count', config.BULLET_FONT_SIZE)
        
    def draw_field(self):
        """Draw the football field."""
        # Green background
        self.screen.fill(config.FIELD_GREEN)
        
        # Field border
        pygame.draw.rect(self.screen, config.WHITE, config.FIELD_RECT, 5)
        
        # Halfway line
        pygame.draw.line(self.screen, config.WHITE, 
                        (config.SCREEN_WIDTH // 2, config.FIELD_BORDER),
                        (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT - config.FIELD_BORDER), 5)
        
        # Center circle
        pygame.draw.circle(self.screen, config.WHITE, 
                         (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2), 70, 5)
        
        # Goal areas
        pygame.draw.rect(self.screen, config.WHITE, config.LEFT_GOAL_RECT, 5)
        pygame.draw.rect(self.screen, config.WHITE, config.RIGHT_GOAL_RECT, 5)
        
    def draw_sprites(self, sprites: pygame.sprite.Group):
        """Draw all sprites in the group."""
        sprites.draw(self.screen)
        
    def draw_power_bars(self, power_bars: List[PowerBar]):
        """Draw power bars for cannons."""
        for power_bar in power_bars:
            power_bar.update()
            self.screen.blit(power_bar.image, power_bar.rect)
            
    def draw_scores(self, player1_score: int, player2_score: int):
        """Draw player scores."""
        score_text = self.fonts['default'].render(
            f"Player 1: {player1_score}  Player 2: {player2_score}", 
            True, config.BLACK
        )
        score_rect = score_text.get_rect(centerx=config.SCREEN_WIDTH // 2, y=10)
        self.screen.blit(score_text, score_rect)
        
    def draw_timer(self, time_remaining: int):
        """Draw game timer."""
        timer_text = self.fonts['default'].render(
            f"Time: {time_remaining}", 
            True, config.BLACK
        )
        timer_rect = timer_text.get_rect(centerx=config.SCREEN_WIDTH // 2, y=100)
        self.screen.blit(timer_text, timer_rect)
        
    def draw_bullet_counts(self, cannons: List[Cannon]):
        """Draw bullet counts for both players."""
        if len(cannons) >= 2:
            # Player 1 bullet counts
            power_text1 = self.fonts['bullet_count'].render(
                f"Power Bullets: {cannons[0].power_bullets}", True, config.BLACK
            )
            precision_text1 = self.fonts['bullet_count'].render(
                f"Precision Bullets: {cannons[0].precision_bullets}", True, config.BLACK
            )
            
            self.screen.blit(power_text1, (10, config.SCREEN_HEIGHT - 60))
            self.screen.blit(precision_text1, (10, config.SCREEN_HEIGHT - 35))
            
            # Player 2 bullet counts
            power_text2 = self.fonts['bullet_count'].render(
                f"Power Bullets: {cannons[1].power_bullets}", True, config.BLACK
            )
            precision_text2 = self.fonts['bullet_count'].render(
                f"Precision Bullets: {cannons[1].precision_bullets}", True, config.BLACK
            )
            
            power_rect2 = power_text2.get_rect(right=config.SCREEN_WIDTH - 10, y=config.SCREEN_HEIGHT - 60)
            precision_rect2 = precision_text2.get_rect(right=config.SCREEN_WIDTH - 10, y=config.SCREEN_HEIGHT - 35)
            
            self.screen.blit(power_text2, power_rect2)
            self.screen.blit(precision_text2, precision_rect2)
            
    def draw_fps(self, fps: int):
        """Draw FPS counter."""
        fps_text = self.fonts['default'].render(f"FPS: {fps}", True, config.WHITE)
        self.screen.blit(fps_text, (10, 10))
        
    def draw_team_selection(self, teams: List[str], scroll_offset: int,
                          team1_selected: Optional[str], team2_selected: Optional[str],
                          current_selecting: int) -> List[pygame.Rect]:
        """
        Draw team selection screen.
        Returns list of button rectangles.
        """
        # Draw gradient background
        self._draw_gradient_background()
        
        # Draw title
        title_text = self.fonts['title'].render("Select Teams", True, config.WHITE)
        title_rect = title_text.get_rect(center=(config.SCREEN_WIDTH // 2, 50))
        self.screen.blit(title_text, title_rect)
        
        # Draw player selection status
        status_text = f"Selecting Player {current_selecting}"
        status_surface = self.fonts['team'].render(status_text, True, config.WHITE)
        status_rect = status_surface.get_rect(center=(config.SCREEN_WIDTH // 2, 100))
        self.screen.blit(status_surface, status_rect)
        
        # Draw team buttons
        button_rects = []
        button_y = 150
        visible_range = range(
            max(0, scroll_offset),
            min(len(teams), scroll_offset + config.MAX_VISIBLE_TEAMS)
        )
        
        for i in visible_range:
            team_name = teams[i]
            button_rect = pygame.Rect(
                config.SCREEN_WIDTH // 4,
                button_y + (i - scroll_offset) * (config.BUTTON_HEIGHT + config.BUTTON_SPACING),
                config.SCREEN_WIDTH // 2,
                config.BUTTON_HEIGHT
            )
            button_rects.append(button_rect)
            
            # Check if mouse is hovering over button
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = button_rect.collidepoint(mouse_pos)
            is_selected = (team_name == team1_selected or team_name == team2_selected)
            
            # Draw button with appropriate color
            button_color = config.HOVER if is_hovered else config.PRIMARY
            if is_selected:
                button_color = config.GREEN
                
            pygame.draw.rect(self.screen, button_color, button_rect, border_radius=10)
            
            # Draw team name
            team_text = self.fonts['team'].render(team_name, True, config.WHITE)
            text_rect = team_text.get_rect(center=button_rect.center)
            self.screen.blit(team_text, text_rect)
            
        # Draw scroll indicators
        self._draw_scroll_indicators(len(teams), scroll_offset)
        
        # Draw selected teams
        self._draw_selected_teams(team1_selected, team2_selected)
        
        return button_rects
        
    def draw_game_over_screen(self, player1_score: int, player2_score: int,
                            bullets_used1: int, bullets_used2: int) -> pygame.Rect:
        """
        Draw game over screen.
        Returns restart button rectangle.
        """
        # Draw gradient background
        self._draw_gradient_background()
        
        # Determine winner
        if player1_score > player2_score:
            winner = 1
        elif player2_score > player1_score:
            winner = 2
        else:
            winner = 1 if bullets_used1 < bullets_used2 else 2
            
        # Draw winner announcement
        winner_font = pygame.font.Font(None, 84)
        winner_text = f"PLAYER {winner} WINS!"
        winner_surface = winner_font.render(winner_text, True, config.WHITE)
        winner_rect = winner_surface.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 4))
        self.screen.blit(winner_surface, winner_rect)
        
        # Draw score cards
        self._draw_score_card(1, player1_score, bullets_used1, 
                            config.SCREEN_WIDTH // 4 - 140, config.SCREEN_HEIGHT // 3)
        self._draw_score_card(2, player2_score, bullets_used2, 
                            config.SCREEN_WIDTH * 3 // 4 - 140, config.SCREEN_HEIGHT // 3)
        
        # Create restart button
        button_width = 240
        button_height = 60
        button_x = config.SCREEN_WIDTH // 2 - button_width // 2
        button_y = config.SCREEN_HEIGHT * 3 // 4 - button_height // 2
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Draw button
        pygame.draw.rect(self.screen, config.PRIMARY, button_rect, border_radius=15)
        button_text = self.fonts['default'].render("PLAY AGAIN", True, config.WHITE)
        text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, text_rect)
        
        return button_rect
        
    def _draw_gradient_background(self):
        """Draw a gradient background."""
        for y in range(config.SCREEN_HEIGHT):
            alpha = y / config.SCREEN_HEIGHT
            color = [int(config.BG_COLOR[i] + (config.PRIMARY[i] - config.BG_COLOR[i]) * alpha * 0.15) 
                    for i in range(3)]
            pygame.draw.line(self.screen, tuple(color), (0, y), (config.SCREEN_WIDTH, y))
            
    def _draw_scroll_indicators(self, total_teams: int, scroll_offset: int):
        """Draw scroll indicators for team selection."""
        if total_teams > config.MAX_VISIBLE_TEAMS:
            if scroll_offset > 0:
                pygame.draw.polygon(self.screen, config.WHITE, [
                    (config.SCREEN_WIDTH // 2, 140),
                    (config.SCREEN_WIDTH // 2 - 10, 130),
                    (config.SCREEN_WIDTH // 2 + 10, 130)
                ])
            if scroll_offset + config.MAX_VISIBLE_TEAMS < total_teams:
                bottom_y = 150 + (config.MAX_VISIBLE_TEAMS * (config.BUTTON_HEIGHT + config.BUTTON_SPACING))
                pygame.draw.polygon(self.screen, config.WHITE, [
                    (config.SCREEN_WIDTH // 2, bottom_y + 20),
                    (config.SCREEN_WIDTH // 2 - 10, bottom_y + 10),
                    (config.SCREEN_WIDTH // 2 + 10, bottom_y + 10)
                ])
                
    def _draw_selected_teams(self, team1: Optional[str], team2: Optional[str]):
        """Draw selected team names at bottom of screen."""
        if team1:
            text = f"Player 1: {team1}"
            surface = self.fonts['team'].render(text, True, config.WHITE)
            self.screen.blit(surface, (20, config.SCREEN_HEIGHT - 60))
            
        if team2:
            text = f"Player 2: {team2}"
            surface = self.fonts['team'].render(text, True, config.WHITE)
            self.screen.blit(surface, (20, config.SCREEN_HEIGHT - 30))
            
    def _draw_score_card(self, player_num: int, score: int, bullets: int, x: int, y: int):
        """Draw individual score card for game over screen."""
        card_width = 280
        card_height = 150
        card_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        
        # Card background
        pygame.draw.rect(card_surface, (*config.PRIMARY, 40), 
                        (0, 0, card_width, card_height), border_radius=15)
        
        # Player text
        player_font = self.fonts['team']
        player_text = player_font.render(f"PLAYER {player_num}", True, config.WHITE)
        card_surface.blit(player_text, (20, 20))
        
        # Score
        score_font = pygame.font.Font(None, 72)
        score_text = score_font.render(str(score), True, config.WHITE)
        card_surface.blit(score_text, (20, 50))
        
        # Bullets used
        bullets_font = pygame.font.Font(None, 28)
        bullets_text = bullets_font.render(f"Bullets: {bullets}", True, config.GRAY)
        card_surface.blit(bullets_text, (20, 110))
        
        # Apply floating animation
        current_time = pygame.time.get_ticks()
        y_offset = math.sin(current_time / 1000 * 2 + (player_num * math.pi)) * 5
        self.screen.blit(card_surface, (x, y + y_offset))
