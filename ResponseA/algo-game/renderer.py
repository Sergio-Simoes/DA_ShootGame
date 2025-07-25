"""Renderer module for drawing game elements."""

import pygame
import math
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, RED, BLUE, GREEN, GRAY, BG_COLOR, PRIMARY, FIELD_COLOR,
    MAX_POWER, BALL_RADIUS, BULLET_RADIUS, GAME_FONT_SIZE, BULLET_COUNT_FONT_SIZE, WINNER_FONT_SIZE
)
from asset_manager import asset_manager

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.game_font = asset_manager.get_font('game', GAME_FONT_SIZE)
        self.bullet_font = asset_manager.get_font('bullet_count', BULLET_COUNT_FONT_SIZE)
        self.winner_font = asset_manager.get_font('winner', WINNER_FONT_SIZE)
    
    def draw_field(self):
        """Draw the game field."""
        self.screen.fill(FIELD_COLOR)
        pygame.draw.rect(self.screen, WHITE, (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100), 5)
        pygame.draw.line(self.screen, WHITE, (SCREEN_WIDTH // 2, 50), (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50), 5)
        pygame.draw.circle(self.screen, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 70, 5)
        pygame.draw.rect(self.screen, WHITE, (50, SCREEN_HEIGHT // 2 - 75, 50, 150), 5)
        pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2 - 75, 50, 150), 5)
    
    def draw_cannon(self, cannon):
        """Draw a cannon."""
        img = asset_manager.get_image(cannon.sprite_name)
        rotated_img = pygame.transform.rotate(img, cannon.angle)
        img_rect = rotated_img.get_rect(center=(cannon.rect.centerx, cannon.rect.centery))
        self.screen.blit(rotated_img, img_rect.topleft)
        
    def draw_power_bar(self, x, y, power, color):
        """Draw power bar for cannon."""
        pygame.draw.rect(self.screen, GRAY, (x - 25, y + 40, 50, 10))
        pygame.draw.rect(self.screen, color, (x - 25, y + 40, int(50 * (power / MAX_POWER)), 10))
    
    def draw_ball(self, ball):
        """Draw the ball."""
        pygame.draw.circle(self.screen, GREEN, (ball.rect.centerx, ball.rect.centery), BALL_RADIUS)
    
    def draw_bullet(self, bullet):
        """Draw a bullet."""
        color = RED if bullet.bullet_type == "power" else BLACK
        pygame.draw.circle(self.screen, color, (bullet.rect.centerx, bullet.rect.centery), BULLET_RADIUS)
    
    def draw_ui(self, game_state):
        """Draw UI elements like scores, timer, and bullet counts."""
        # Draw scores
        score_text = self.game_font.render(
            f"Player 1: {game_state.player1_score}  Player 2: {game_state.player2_score}", 
            True, BLACK
        )
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 10))
        
        # Draw timer
        timer_text = self.game_font.render(f"Time: {game_state.counter}", True, BLACK)
        self.screen.blit(timer_text, (SCREEN_WIDTH // 2 - 50, 100))
        
        # Draw bullet counts for Player 1
        power_text1 = self.bullet_font.render(f"Power Bullets: {game_state.powerbullets1}", True, BLACK)
        precision_text1 = self.bullet_font.render(f"Precision Bullets: {game_state.precisionbullets1}", True, BLACK)
        
        self.screen.blit(power_text1, (10, SCREEN_HEIGHT - power_text1.get_height() - 10))
        self.screen.blit(precision_text1, (10, SCREEN_HEIGHT - power_text1.get_height() - 
                                         precision_text1.get_height() - 20))
        
        # Draw bullet counts for Player 2
        power_text2 = self.bullet_font.render(f"Power Bullets: {game_state.powerbullets2}", True, BLACK)
        precision_text2 = self.bullet_font.render(f"Precision Bullets: {game_state.precisionbullets2}", True, BLACK)
        
        self.screen.blit(power_text2, (SCREEN_WIDTH - power_text2.get_width() - 10, 
                                     SCREEN_HEIGHT - power_text2.get_height() - 10))
        self.screen.blit(precision_text2, (SCREEN_WIDTH - precision_text2.get_width() - 10,
                                         SCREEN_HEIGHT - power_text2.get_height() - 
                                         precision_text2.get_height() - 20))
        
        # Draw FPS counter
        fps_text = self.game_font.render(f"FPS: {int(game_state.clock.get_fps())}", True, WHITE)
        self.screen.blit(fps_text, (10, 10))
    
    def draw_game_over_screen(self, game_state):
        """Draw game over screen with winner announcement."""
        # Create background with subtle gradient
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            alpha = y / SCREEN_HEIGHT
            color = [int(BG_COLOR[i] + (PRIMARY[i] - BG_COLOR[i]) * alpha * 0.15) for i in range(3)]
            pygame.draw.line(background, tuple(color), (0, y), (SCREEN_WIDTH, y))
        self.screen.blit(background, (0, 0))
        
        # Determine winner
        if game_state.player1_score > game_state.player2_score:
            winner = 1
        elif game_state.player2_score > game_state.player1_score:
            winner = 2
        else:
            winner = 1 if game_state.bullets_used1 < game_state.bullets_used2 else 2
            
        # Draw score cards
        self.draw_score_card(1, game_state.player1_score, game_state.bullets_used1, SCREEN_WIDTH//4 - 140, SCREEN_HEIGHT//3)
        self.draw_score_card(2, game_state.player2_score, game_state.bullets_used2, SCREEN_WIDTH*3//4 - 140, SCREEN_HEIGHT//3)
        
        # Draw winner announcement
        winner_text = f"PLAYER {winner} WINS!"
        winner_surface = self.winner_font.render(winner_text, True, WHITE)
        winner_rect = winner_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
        self.screen.blit(winner_surface, winner_rect)
        
        # Create restart button
        button_width = 240
        button_height = 60
        button_x = SCREEN_WIDTH//2 - button_width//2
        button_y = SCREEN_HEIGHT*3//4 - button_height//2
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Draw button
        pygame.draw.rect(self.screen, PRIMARY, button_rect, border_radius=15)
        button_text = self.game_font.render("PLAY AGAIN", True, WHITE)
        text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, text_rect)
        
        return button_rect
    
    def draw_score_card(self, player_num, score, bullets, x, y):
        """Draw a player score card for game over screen."""
        card_width = 280
        card_height = 150
        card_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        
        # Card background
        pygame.draw.rect(card_surface, (*PRIMARY, 40), (0, 0, card_width, card_height), border_radius=15)
        
        # Player text
        player_font = pygame.font.Font(None, 36)
        player_text = player_font.render(f"PLAYER {player_num}", True, WHITE)
        card_surface.blit(player_text, (20, 20))
        
        # Score
        score_font = pygame.font.Font(None, 72)
        score_text = score_font.render(str(score), True, WHITE)
        card_surface.blit(score_text, (20, 50))
        
        # Bullets used
        bullets_font = pygame.font.Font(None, 28)
        bullets_text = bullets_font.render(f"Bullets: {bullets}", True, GRAY)
        card_surface.blit(bullets_text, (20, 110))
        
        # Apply floating animation
        current_time = pygame.time.get_ticks()
        y_offset = math.sin(current_time / 1000 * 2 + (player_num * math.pi)) * 5
        self.screen.blit(card_surface, (x, y + y_offset))
    
    def draw_gradient_background(self, start_color, end_color):
        """Draw a gradient background."""
        for y in range(SCREEN_HEIGHT):
            alpha = y / SCREEN_HEIGHT
            color = [int(start_color[i] + (end_color[i] - start_color[i]) * alpha * 0.15) for i in range(3)]
            pygame.draw.line(self.screen, tuple(color), (0, y), (SCREEN_WIDTH, y))
