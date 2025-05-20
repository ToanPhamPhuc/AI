import random

# --- Window and grid settings ---
WIDTH, HEIGHT = 1024, 768
BOX_SIZE = 20

# --- Movement speeds (frames per move) ---
MOVE_FRAMES = 5
PLAYER_MOVE_FRAMES = 5
AI_MOVE_FRAMES = 1

# --- Colors ---
PLAYER_COLOR = (255, 255, 0)  # Yellow
FOOD_COLOR = (255, 100, 0)
BACKGROUND_COLOR = (30, 30, 30)
SNAKE_BODY_COLOR = (0, 200, 255)
TEXT_COLOR = (255, 255, 255)
NAME_COLOR = (255, 255, 0)

# --- Utility functions ---

def random_color():
    """Generate a random bright color for snakes."""
    return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

def random_food(snake_positions):
    """Generate food coordinates not overlapping with any snake."""
    while True:
        fx = random.randrange(0, WIDTH, BOX_SIZE)
        fy = random.randrange(0, HEIGHT, BOX_SIZE)
        if (fx, fy) not in snake_positions:
            return (fx, fy)

def distance(a, b):
    """Manhattan distance between points a and b."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
