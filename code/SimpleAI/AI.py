import pygame
import random
import sys
from SimpleAI import SimpleAIAgent
from config import WIDTH, HEIGHT, BOX_SIZE

# --- Constants ---
START_X = WIDTH // 2 // BOX_SIZE * BOX_SIZE
START_Y = HEIGHT // 2 // BOX_SIZE * BOX_SIZE
MOVE_FRAMES = 5
PLAYER_MOVE_FRAMES = 5
AI_MOVE_FRAMES = 1

# --- Player control variables ---
player_mode = False
player_direction = 'right'
pending_direction = 'right'

def random_food(snake):
    while True:
        fx = random.randrange(0, WIDTH, BOX_SIZE)
        fy = random.randrange(0, HEIGHT, BOX_SIZE)
        if (fx, fy) not in snake:
            return (fx, fy)

def distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# --- Pygame Setup ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Snake Game")
clock = pygame.time.Clock()

generation = 1

while True:
    agent = SimpleAIAgent(x=START_X, y=START_Y)
    snake = [(START_X, START_Y)]
    food = random_food(snake)
    score = 0

    running = True
    move_queue = []
    frames_left = 0
    current_head = snake[0]
    next_head = snake[0]
    prev_dist = distance(snake[0], food)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    player_mode = not player_mode
                    print("Switched to", "PLAYER mode" if player_mode else "AI mode")
                elif player_mode:
                    if (event.key == pygame.K_UP or event.key == pygame.K_w) and player_direction != 'down':
                        pending_direction = 'up'
                    elif (event.key == pygame.K_DOWN or event.key == pygame.K_s) and player_direction != 'up':
                        pending_direction = 'down'
                    elif (event.key == pygame.K_LEFT or event.key == pygame.K_a) and player_direction != 'right':
                        pending_direction = 'left'
                    elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and player_direction != 'left':
                        pending_direction = 'right'

        if frames_left == 0:
            if player_mode:
                player_direction = pending_direction
                dx, dy = {
                    'left':  (-1,  0),
                    'right': ( 1,  0),
                    'up':    ( 0, -1),
                    'down':  ( 0,  1)
                }[player_direction]
                new_head = (snake[0][0] + dx * BOX_SIZE, snake[0][1] + dy * BOX_SIZE)
                action = player_direction
            else:
                action, new_head = agent.move(snake, food)

            # Check collisions
            if (
                new_head[0] < 0 or new_head[0] >= WIDTH or
                new_head[1] < 0 or new_head[1] >= HEIGHT or
                new_head in snake
            ):
                reward = -10
                agent.learn(reward)
                break

            snake.insert(0, new_head)
            if new_head == food:
                reward = 10
                score += 1
                food = random_food(snake)
            else:
                reward = -0.1
                snake.pop()

            agent.x, agent.y = new_head
            agent.learn(reward)

            if len(snake) > 1:
                current_head = snake[1]
            else:
                current_head = snake[0]
            next_head = snake[0]
            frames_left = AI_MOVE_FRAMES if not player_mode else PLAYER_MOVE_FRAMES


        # Interpolate head position
        t = (MOVE_FRAMES - frames_left) / MOVE_FRAMES
        interp_x = int(current_head[0] + (next_head[0] - current_head[0]) * t)
        interp_y = int(current_head[1] + (next_head[1] - current_head[1]) * t)

        # Drawing
        screen.fill((30, 30, 30))
        for segment in snake[1:]:
            pygame.draw.rect(screen, (0, 200, 255), (*segment, BOX_SIZE, BOX_SIZE))
        pygame.draw.rect(screen, (0, 200, 255), (interp_x, interp_y, BOX_SIZE, BOX_SIZE))
        pygame.draw.rect(screen, (255, 100, 0), (*food, BOX_SIZE, BOX_SIZE))
        pygame.display.flip()
        clock.tick(30)

        if frames_left > 0:
            frames_left -= 1

    print(f"Generation {generation} finished. Score: {score}")
    generation += 1