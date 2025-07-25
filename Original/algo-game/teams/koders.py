import math

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
    # Unpack cannon and target positions
    cannon_x, cannon_y = cannon_pos
    target_x, target_y = ball_pos
    ball_vx, ball_vy = ball_vel

    # Predict the future position of the ball
    time_to_hit = 1  # Assume 1 second for simplicity; can be adjusted for accuracy
    predicted_x = target_x + ball_vx * time_to_hit
    predicted_y = target_y + ball_vy * time_to_hit

    # Calculate angle to the predicted position of the ball
    dx = predicted_x - cannon_x
    dy = predicted_y - cannon_y
    angle = -math.degrees(math.atan2(dy, dx))

    # Calculate distance to the predicted position of the ball
    distance = math.sqrt(dx**2 + dy**2)

    # Determine power proportional to distance, clamped to MAX_POWER
    power = min(MAX_POWER, max(5, int(distance / 10)))

    # Determine bullet type based on cannon position
    if cannon_x < WIDTH / 3 and power_bullet_count > 0:
        bullet_type = "power"
    elif precision_bullet_count > 0:
        bullet_type = "precision"
    else:
        return None  # Do not shoot if no bullets are available

    # Return the shooting parameters
    return (angle, power, bullet_type)