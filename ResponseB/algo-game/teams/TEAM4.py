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
    # Unpack cannon position
    cannon_x, cannon_y = cannon_pos

    # Define the target position (end of the arena)
    # target_x = WIDTH if cannon_x < WIDTH / 2 else 0
    # target_y = HEIGHT / 2  # Aim for the middle height to maximize clearance
    # Define the target position
    target_x, target_y = ball_pos

    # Calculate the angle to the target
    dx = target_x - cannon_x
    dy = target_y - cannon_y
    angle =- math.degrees(math.atan2(dy, dx-BALL_RADIUS))

    # Calculate the distance to the target
    distance = math.hypot(dx, dy)

    # Calculate the power needed to reach the target (use max power for maximum distance)
    power = MAX_POWER

    # Choose bullet type based on remaining counts
    if power_bullet_count > 0:
        bullet_type = "power"
    else:
        bullet_type = "precision"

    # Return the shooting parameters
    return (angle, power, bullet_type)

def rotate_cannon(current_angle, target_angle, rotation_speed):
    """
    Rotates the cannon to the target angle.
    
    Parameters:
    current_angle: float
        The current angle of the cannon.
    target_angle: float
        The target angle to rotate to.
    rotation_speed: float
        The speed at which the cannon rotates.
        
    Returns:
    float
        The new angle of the cannon.
    """
    if current_angle < target_angle:
        current_angle += rotation_speed
        if current_angle > target_angle:
            current_angle = target_angle
    elif current_angle > target_angle:
        current_angle -= rotation_speed
        if current_angle < target_angle:
            current_angle = target_angle
    return current_angle

# Example usage
cannon_angle = 0  # Initial angle of the cannon
target_angle, power, bullet_type = player_script((100, 300), (700, 300), 5, 5, (0, 0))
rotation_speed = 1  # Speed of rotation

# Rotate the cannon to the target angle
while cannon_angle != target_angle:
    cannon_angle = rotate_cannon(cannon_angle, target_angle, rotation_speed)
    print(f"Cannon angle: {cannon_angle}")
