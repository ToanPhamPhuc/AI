import random
import pygame
from AI_New_Snake_Mechanics import player_name, screen, snakes

def random_color():
    return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

# Initial color setup
snake_colors = [(255, 255, 0)]  # Yellow for player

font = pygame.font.SysFont(None, 24)
snake_names = [player_name]  # Initial name

for j, snake in enumerate(snakes):
    name_surf = font.render(snake_names[j], True, (255, 255, 255))
    screen.blit(name_surf, (snake[0][0], snake[0][1] - 20))  # Draw name above head

