"""
Configuration module for the Football Game.
Contains all game constants and settings for easy tweaking.
"""

import pygame

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
PRIMARY = (86, 63, 251)
HOVER = (106, 83, 255)
BG_COLOR = (18, 18, 18)
FIELD_GREEN = (34, 139, 34)

# Game time settings
GAME_TIME = 60  # seconds
TURN_DELAY = 0.6  # seconds between turns

# Ball settings
BALL_RADIUS = 20
BALL_FRICTION = 0.995
BALL_STOP_VELOCITY = 0.1

# Initial ball spawn positions (will cycle through these)
BALL_SPAWN_POSITIONS = [
    (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
    (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50),
    (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50),
    (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100),
    (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 100)
]

# Cannon settings
CANNON_RADIUS = 30
CANNON_SIZE = (60, 20)  # width, height for sprite scaling

# Cannon positions
CANNON1_POS = (50, SCREEN_HEIGHT // 2)
CANNON2_POS = (SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2)

# Bullet settings
BULLET_RADIUS = 5
BULLET_SPEED = 15
MAX_POWER = 30
POWER_INCREMENT = 0.13

# Bullet counts per round
POWER_BULLETS_COUNT = 5
PRECISION_BULLETS_COUNT = 10

# Power bullet settings
POWER_BULLET_ANGLE_ERROR = 5  # degrees
POWER_BULLET_MULTIPLIER = 1.5

# Scoring
WINNING_SCORE = 1

# Field drawing settings
FIELD_BORDER = 50
FIELD_RECT = pygame.Rect(FIELD_BORDER, FIELD_BORDER, 
                         SCREEN_WIDTH - 2 * FIELD_BORDER, 
                         SCREEN_HEIGHT - 2 * FIELD_BORDER)

# Goal areas
GOAL_WIDTH = 50
GOAL_HEIGHT = 150
LEFT_GOAL_RECT = pygame.Rect(FIELD_BORDER, SCREEN_HEIGHT // 2 - GOAL_HEIGHT // 2, 
                             GOAL_WIDTH, GOAL_HEIGHT)
RIGHT_GOAL_RECT = pygame.Rect(SCREEN_WIDTH - FIELD_BORDER - GOAL_WIDTH, 
                              SCREEN_HEIGHT // 2 - GOAL_HEIGHT // 2, 
                              GOAL_WIDTH, GOAL_HEIGHT)

# Team selection UI
MAX_VISIBLE_TEAMS = 8
BUTTON_HEIGHT = 50
BUTTON_SPACING = 10
TITLE_FONT_SIZE = 64
TEAM_FONT_SIZE = 36
BULLET_FONT_SIZE = 24

# Asset paths
CANNON_IMAGE_PATH = "cannon.png"
BALL_IMAGE_PATH = "ball.png"

# Events
TIMER_EVENT = pygame.USEREVENT
