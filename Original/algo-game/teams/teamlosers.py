import math
import random

# Screen dimensions
WIDTH, HEIGHT = 800, 600

# Radius of the ball
BALL_RADIUS = 20

# Maximum power that can be used to shoot
MAX_POWER = 30

# Friction factor applied to the ball's movement to simulate deceleration
FRICTION = 0.995

# Speed of the bullet when fired
BULLET_SPEED = 15

def player_script(cannon_pos, ball_pos, power_bullet_count, precision_bullet_count, ball_vel):
    """
    Determines the angle, power, and bullet type for shooting the ball.
    
    Parameters:
    cannon_pos: tuple
        Coordinates (x, y) of the cannon.
    ball_pos: tuple
        Coordinates (x, y) of the ball (target position).
    power_bullet_count: int
        Number of power bullets remaining.
    precision_bullet_count: int
        Number of precision bullets remaining.
    ball_vel: tuple
        Current velocity of the ball as (vx, vy).
        
    Returns:
    tuple or None
        (angle, power, bullet_type) for the shot, or None if no shot is made.
        - angle: The angle in degrees to aim the cannon.
        - power: The power level for the shot (1 to MAX_POWER).
        - bullet_type: The type of bullet ("power" or "precision").
    """
    # Unpack cannon position
    cannon_x, cannon_y = cannon_pos

    # Define the target position
    target_x, target_y = ball_pos

    # Calculate the angle to aim the cannon at the ball's position
    delta_x = target_x - cannon_x
    delta_y = target_y - cannon_y
    angle =- math.degrees(math.atan2(delta_y, delta_x))  # Angle in degrees
    
    # Calculate the distance to the ball
    distance = math.sqrt(delta_x ** 2 + delta_y ** 2)

    # Calculate the required power based on the distance
    # The further the ball, the higher the power needed
    power = min(MAX_POWER, int(distance / 20))  # Scale power based on distance

    # Choose the bullet type
    # If power bullets are available and the distance is large, use a power bullet
    if power_bullet_count > 0 and distance > 150:
        bullet_type = "power"
    # If precision bullets are available and the distance is smaller, use a precision bullet
    elif precision_bullet_count > 0 and distance < 150:
        bullet_type = "precision"
    # Otherwise, use whichever bullet is available (random choice between power and precision)
    else:
        bullet_type = random.choice(["power", "precision"])

    # Return the calculated parameters for shooting
    return (angle, power, bullet_type)
