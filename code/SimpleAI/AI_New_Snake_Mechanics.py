import pygame
import tkinter as tk
from tkinter import simpledialog
import sys
from SimpleAI import *
from config import *

# --- Player Name Popup ---
root = tk.Tk()
root.withdraw()
player_name = simpledialog.askstring("Player Name", "Enter your name:")
if not player_name:
    player_name = "Player"

# --- Pygame Setup ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Snake Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# Starting positions aligned to grid
START_X = WIDTH // 2 // BOX_SIZE * BOX_SIZE
START_Y = HEIGHT // 2 // BOX_SIZE * BOX_SIZE

player_mode = False
player_direction = 'right'
pending_direction = 'right'

snake_colors = [PLAYER_COLOR]
snake_names = [player_name]

generation = 1

while True:
    agents = [SimpleAIAgent(x=START_X, y=START_Y)]
    snakes = [[(START_X, START_Y)]]
    scores = [0]

    foods = []
    snake_positions = [pos for sn in snakes for pos in sn]
    # Ensure only one food per snake color
    existing_colors = {f[2] for f in foods}
    for color in snake_colors:
        if color not in existing_colors:
            snake_positions = [pos for sn in snakes for pos in sn]
            foods.append(random_food(snake_positions, color))


    running = True
    frames_left = 0

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

        screen.fill(BACKGROUND_COLOR)

        snake_positions = [pos for sn in snakes for pos in sn]

        for i in range(len(agents)):
            food_color = snake_colors[i]
            # foods.append(random_food(snake_positions, food_color))
            agent = agents[i]
            snake = snakes[i]

            if frames_left == 0:
                if player_mode and i == 0:
                    player_direction = pending_direction
                    dx, dy = {
                        'left':  (-1,  0),
                        'right': ( 1,  0),
                        'up':    ( 0, -1),
                        'down':  ( 0,  1)
                    }[player_direction]
                    new_head = (snake[0][0] + dx * BOX_SIZE, snake[0][1] + dy * BOX_SIZE)
                else:
                    # Get food that matches this snake's color
                    target_foods = [f for f in foods if f[2] == snake_colors[i]]
                    target_food = target_foods[0] if target_foods else None
                    action, new_head = agent.move(snake, target_food)

                # Check collision with walls
                if (
                    new_head[0] < 0 or new_head[0] >= WIDTH or
                    new_head[1] < 0 or new_head[1] >= HEIGHT
                ):
                    if i == 0:
                        print("Player hit the wall and died.")
                        player_mode = False
                    snakes[i] = []
                    continue


                # Check self collision -> split snake
                if new_head in snake:
                    print(f"Collision detected for {snake_names[i]} at {new_head}") 
                    index = snake.index(new_head)
                    
                    if i == 0:  # Player splits
                        tail_part = snake[index:]
                        snakes[i] = snake[:index]

                        if len(tail_part) > 1:
                            new_agent = SimpleAIAgent(x=tail_part[0][0], y=tail_part[0][1])
                            new_agent.direction = agent.direction or 'right'
                            agents.append(new_agent)
                            snakes.append(tail_part)
                            scores.append(0)

                            new_color = random_color()
                            snake_colors.append(new_color)
                            snake_names.append(f"Snake{len(snake_names)}")

                            # Ensure the new snake has food to pursue
                            snake_positions = [pos for sn in snakes for pos in sn]
                            foods.append(random_food(snake_positions, new_color))
                        else:
                            print("Player died.")
                            player_mode = False
                            snakes[i] = []
                    else:
                        # AI splits like the player
                        tail_part = snake[index:]
                        snakes[i] = snake[:index]

                        if len(tail_part) > 1:
                            new_agent = SimpleAIAgent(x=tail_part[0][0], y=tail_part[0][1])
                            new_agent.direction = agent.direction or 'right'
                            agents.append(new_agent)
                            snakes.append(tail_part)
                            scores.append(0)

                            new_color = random_color()
                            snake_colors.append(new_color)
                            snake_names.append(f"Snake{len(snake_names)}")

                            # Ensure the new snake has food to pursue
                            snake_positions = [pos for sn in snakes for pos in sn]
                            foods.append(random_food(snake_positions, new_color))
                        else:
                            print(f"{snake_names[i]} died from self-collision.")
                            snakes[i] = []

                    continue

                snake.insert(0, new_head)
                eaten = False
                for j, (fx, fy, fcolor) in enumerate(foods):
                    if (fx, fy) == new_head:
                        if fcolor == snake_colors[i]:
                            # Legal food
                            scores[i] += 1
                            eaten = True
                            del foods[j]
                            foods.append(random_food(
                                [pos for sn in snakes for pos in sn], snake_colors[i]
                            ))
                        else:
                            # This is another snake's food → treat it as fatal
                            if i == 0:
                                print("Player tried to eat someone else's food and died.")
                                player_mode = False
                            snakes[i] = []
                        break

                if not eaten:
                    snake.pop()


                agent.x, agent.y = new_head

        # Draw snakes
        for j, snake in enumerate(snakes):
            if not snake:
                continue  # Skip empty snakes to avoid IndexError
            
            # Draw body
            for segment in snake[1:]:
                pygame.draw.rect(screen, (0, 200, 255), (*segment, BOX_SIZE, BOX_SIZE))

            # Draw head
            head_color = (255, 255, 0) if j == 0 else snake_colors[j]
            pygame.draw.rect(screen, head_color, (*snake[0], BOX_SIZE, BOX_SIZE))

            # Draw name above head
            name_surf = font.render(snake_names[j], True, NAME_COLOR)
            screen.blit(name_surf, (snake[0][0], snake[0][1] - 20))

            # Draw score below head
            score_surf = font.render(f"{scores[j]}", True, (255, 255, 255))
            screen.blit(score_surf, (snake[0][0], snake[0][1] + BOX_SIZE))


        # Draw food
        for fx, fy, color in foods:
            pygame.draw.rect(screen, color, (fx, fy, BOX_SIZE, BOX_SIZE))


        pygame.display.flip()
        clock.tick(30)

        # --- Remove empty snakes and related data ---
        for i in reversed(range(len(snakes))):
            if not snakes[i]:
                del snakes[i]
                del agents[i]
                del snake_colors[i]
                del snake_names[i]
                del scores[i]

        if frames_left > 0:
            frames_left -= 1
        else:
            frames_left = PLAYER_MOVE_FRAMES if player_mode else AI_MOVE_FRAMES
    
    generation += 1
    print(f"Generation {generation} finished. Score: {scores[0]}")
