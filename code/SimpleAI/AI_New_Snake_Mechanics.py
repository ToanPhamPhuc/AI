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

def reset_game():
    global player_mode, player_direction, pending_direction, snake_colors, snake_names, agents, snakes, scores, foods
    player_mode = True
    player_direction = 'right'
    pending_direction = 'right'
    snake_colors = [PLAYER_COLOR]
    snake_names = [player_name]
    agents = [SimpleAIAgent(x=START_X, y=START_Y)]
    snakes = [[(START_X, START_Y)]]
    scores = [0]
    foods = []
    # Initialize food for the player
    snake_positions = [pos for sn in snakes for pos in sn]
    foods.append(random_food(snake_positions, PLAYER_COLOR))
    return True  # Return True to indicate game should continue running

# Initialize game variables
player_mode = True
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
                    if player_mode:
                        # When switching to player mode, inherit the AI's direction
                        player_direction = agents[0].direction
                        pending_direction = agents[0].direction
                    print("Switched to", "PLAYER mode" if player_mode else "AI mode")
                elif event.key == pygame.K_g and player_mode:  # Cheat code for growth
                    if len(snakes) > 0:  # Make sure there's a snake to grow
                        # Add a new segment at the tail's position
                        tail = snakes[0][-1]
                        snakes[0].append(tail)
                        scores[0] += 1  # Increase score as well
                        print("Cheat activated: Snake grew longer!")
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
            if i >= len(snake_colors):  # Safety check
                continue
                
            food_color = snake_colors[i]
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
                    if i == 0:  # Player hits wall
                        print("Player hit the wall and died.")
                        # Transfer player control to next available snake
                        if len(snakes) > 1 and len(agents) > 1:  # Make sure we have both next snake and agent
                            # Store the next snake's direction before deletion
                            next_direction = agents[1].direction
                            # Remove current snake
                            del snakes[0]
                            del agents[0]
                            del snake_colors[0]
                            del snake_names[0]
                            del scores[0]
                            # Make next snake the player snake
                            snake_colors[0] = PLAYER_COLOR  # Change color to yellow
                            player_direction = next_direction  # Use stored direction
                            pending_direction = next_direction
                            player_mode = True  # Keep player mode active
                            print(f"Control transferred to {snake_names[0]}")
                        else:
                            print("No more snakes to control, game restarted")
                            running = reset_game()  # Reset game state
                    snakes[i] = []
                    continue

                # Check self collision -> split snake
                if new_head in snake:
                    print(f"Collision detected for {snake_names[i]} at {new_head}") 
                    index = snake.index(new_head)
                    
                    if i == 0:  # Player splits or dies
                        tail_part = snake[index:]
                        snakes[i] = snake[:index]

                        if len(tail_part) > 1:  # Split possible
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
                        else:  # Player dies
                            print("Player died from self-collision.")
                            # Transfer player control to next available snake
                            if len(snakes) > 1 and len(agents) > 1:  # Make sure we have both next snake and agent
                                # Store the next snake's direction before deletion
                                next_direction = agents[1].direction
                                # Remove current snake
                                del snakes[0]
                                del agents[0]
                                del snake_colors[0]
                                del snake_names[0]
                                del scores[0]
                                # Make next snake the player snake
                                snake_colors[0] = PLAYER_COLOR  # Change color to yellow
                                player_direction = next_direction  # Use stored direction
                                pending_direction = next_direction
                                player_mode = True  # Keep player mode active
                                print(f"Control transferred to {snake_names[0]}")
                            else:
                                print("No more snakes to control, game restarted")
                                running = reset_game()  # Reset game state
                            snakes[i] = []
                    else:  # AI snake splits or dies
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
                        # Allow player-controlled snake to eat yellow food
                        if (i == 0 and fcolor == PLAYER_COLOR) or (i > 0 and fcolor == snake_colors[i]):
                            # Legal food
                            scores[i] += 1
                            eaten = True
                            del foods[j]
                            # Spawn new food with appropriate color
                            foods.append(random_food(
                                [pos for sn in snakes for pos in sn], 
                                PLAYER_COLOR if i == 0 else snake_colors[i]
                            ))
                        else:
                            # This is another snake's food → treat it as fatal
                            if i == 0:
                                print("Player tried to eat someone else's food and died.")
                                # Transfer player control to next available snake
                                if len(snakes) > 1 and len(agents) > 1:  # Make sure we have both next snake and agent
                                    # Store the next snake's direction before deletion
                                    next_direction = agents[1].direction
                                    # Remove current snake
                                    del snakes[0]
                                    del agents[0]
                                    del snake_colors[0]
                                    del snake_names[0]
                                    del scores[0]
                                    # Make next snake the player snake
                                    snake_colors[0] = PLAYER_COLOR  # Change color to yellow
                                    player_direction = next_direction  # Use stored direction
                                    pending_direction = next_direction
                                    player_mode = True  # Keep player mode active
                                    print(f"Control transferred to {snake_names[0]}")
                                else:
                                    print("No more snakes to control, game restarted")
                                    running = reset_game()  # Reset game state
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
