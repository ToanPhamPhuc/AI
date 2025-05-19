import pygame
import random
import sys
import numpy as np
from NN import NeuralNetwork
from evolution import EvolutionEngine

# --- Constants ---
GRID_WIDTH, GRID_HEIGHT = 600, 350
BOX_SIZE = 20
MOVE_FRAMES = 1
NUM_GAMES = 4
WINDOW_WIDTH, WINDOW_HEIGHT = 2 * GRID_WIDTH, 2 * GRID_HEIGHT
BORDER_THICKNESS = 4
FONT_SIZE = 16
NUM_GAMES = 4

# --- Game Settings and Fitnesses ---
best_fitnesses = []
average_fitnesses = []
generation = 1
GENERATION_LIMIT = 100

# --- AI Agent ---
class NeuralAIAgent:
    def __init__(self, nn=None):
        self.nn = nn if nn else NeuralNetwork()
        self.direction = 'right'
    
    def get_inputs(self, snake, food):
        head_x, head_y = snake[0]
        
        dx = food[0] - head_x
        dy = food[1] - head_y
        distance_to_food = abs(dx) + abs(dy)

        max_distance = (GRID_WIDTH//BOX_SIZE) + (GRID_HEIGHT //BOX_SIZE) 

        snake_length = len(snake)
        max_possible_length = (GRID_WIDTH // BOX_SIZE) * (GRID_HEIGHT // BOX_SIZE)

        food_dx = dx / GRID_WIDTH
        food_dy = dy / GRID_HEIGHT

        def is_blocked(x, y):
            return (x<0 or x>=GRID_WIDTH or y<0 or y>=GRID_HEIGHT or (x, y) in snake)
        
        left_blocked = is_blocked(head_x - BOX_SIZE, head_y)
        right_blocked = is_blocked(head_x + BOX_SIZE, head_y)
        up_blocked = is_blocked(head_x, head_y - BOX_SIZE)
        down_blocked = is_blocked(head_x, head_y + BOX_SIZE)

        return np.array([ #TODO: Normalize these values
            food_dx, food_dy,
            int(self.direction == 'left'),
            int(self.direction == 'right'),
            int(self.direction == 'up'),
            int(self.direction == 'down'),
            left_blocked,
            right_blocked,
            up_blocked,
            down_blocked,
            distance_to_food / max_distance,
            snake_length / max_possible_length,
        ]
        , dtype=np.float32)

    def move(self, snake, food):
        inputs = self.get_inputs(snake, food)
        outputs = self.nn.forward(inputs)

        action = np.argmax(outputs)
        directions = ['left', 'right', 'up', 'down']
        
        current_idx = directions.index(self.direction)

        if action == 0:  # left
            new_idx = (current_idx - 1) % 4
        elif action == 1:  # go straight
            new_idx = current_idx
        else:  # right
            new_idx = (current_idx + 1) % 4
        # chosen_idx = np.argmax(outputs)
        # chosen_dir = directions[chosen_idx]

        # if self.direction == 'left' and chosen_dir == 'right':
        #     chosen_dir = 'left'
        # elif self.direction == 'right' and chosen_dir == 'left':
        #     chosen_dir = 'right'
        # elif self.direction == 'up' and chosen_dir == 'down':
        #     chosen_dir = 'up'
        # elif self.direction == 'down' and chosen_dir == 'up':
        #     chosen_dir = 'down'    

        opposite = {
            'left': 'right',
            'right': 'left',
            'up': 'down',
            'down': 'up'
        }
        
        proposed_direction = directions[new_idx]
        if proposed_direction != opposite[self.direction]:
            self.direction = proposed_direction

        dx,dy = {
            'left': (-1, 0),
            'right': (1, 0),
            'up': (0, -1),
            'down': (0, 1)
        } [self.direction]
        
        head_x, head_y = snake[0]
        return self.direction, (head_x + dx * BOX_SIZE, head_y + dy * BOX_SIZE)

    def learn(self, reward):
        # TODO: Implement learning mechanism
        pass

# --- Helper ---
def random_food(snake):
    while True:
        fx = random.randrange(0, GRID_WIDTH, BOX_SIZE)
        fy = random.randrange(0, GRID_HEIGHT, BOX_SIZE)
        if (fx, fy) not in snake:
            return (fx, fy)

# --- Game Instance ---
class GameInstance:
    def __init__(self, agent=None):
        start_x = GRID_WIDTH // 2 // BOX_SIZE * BOX_SIZE
        start_y = GRID_HEIGHT // 2 // BOX_SIZE * BOX_SIZE
        self.snake = [(start_x, start_y)]
        self.food = random_food(self.snake)
        self.score = 0
        self.generation = 1
        self.frames_left = 0
        self.current_head = self.snake[0]
        self.next_head = self.snake[0]
        self.running = True
        self.agent = agent if agent else NeuralAIAgent()
        self.agent.direction = 'right' 
        self.prev_food_distance = self.get_food_distance()
        self.idle_steps = 0

        # Initialize high_score only once (outside reset)
        if not hasattr(self, 'high_score'):
            self.high_score = 0

    def get_food_distance(self):
        head_x, head_y = self.snake[0]
        food_x, food_y = self.food
        return abs(head_x - food_x) + abs(head_y - food_y)
    
    def reset(self):
        # Save high_score before reset (no-op, kept for clarity)
        if self.score > self.high_score:
            self.high_score = self.score
        
        self.score = 0
        self.generation += 1
        start_x = GRID_WIDTH // 2 // BOX_SIZE * BOX_SIZE
        start_y = GRID_HEIGHT // 2 // BOX_SIZE * BOX_SIZE
        self.snake = [(start_x, start_y)]
        self.food = random_food(self.snake)
        self.frames_left = 0
        self.current_head = self.snake[0]
        self.next_head = self.snake[0]
        self.running = True
        self.agent.direction = 'right'  # Reset AI direction if needed

    def update(self):
        if not self.running:
            return

        if self.frames_left == 0:
            action, new_head = self.agent.move(self.snake, self.food)

            # Check for wall collisions and self-collision
            if new_head in self.snake or not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
                self.agent.learn(-10)
                self.reset()
                return

            self.snake.insert(0, new_head)

            if new_head == self.food:
                self.score += 1
                if self.score > self.high_score:  # <-- Add this check
                    self.high_score = self.score
                self.agent.learn(10)
                self.food = random_food(self.snake)

            else:
                self.agent.learn(-0.1)
                new_distance = self.get_food_distance()

                if new_distance < self.prev_food_distance:
                    self.agent.learn(0.3)
                    self.idle_steps = 0
                elif new_distance > self.prev_food_distance:
                    self.agent.learn(-0.3)
                    self.idle_steps += 1
                else:
                    self.agent.learn(-0.2)
                    self.idle_steps += 1
                
                self.agent.learn(-0.05)
                if self.idle_steps > 30:
                    self.agent.learn(-10)
                    self.reset()
                    return
                                     
                self.prev_food_distance = new_distance
                self.snake.pop()

            self.current_head = self.next_head
            self.next_head = new_head
            self.frames_left = MOVE_FRAMES
        else:
            self.frames_left -= 1

    def draw(self, surface, font):
        t = (MOVE_FRAMES - self.frames_left) / MOVE_FRAMES
        interp_x = int(self.current_head[0] + (self.next_head[0] - self.current_head[0]) * t)
        interp_y = int(self.current_head[1] + (self.next_head[1] - self.current_head[1]) * t)

        surface.fill((20, 20, 20))
        for segment in self.snake[1:]:
            pygame.draw.rect(surface, (0, 200, 255), (*segment, BOX_SIZE, BOX_SIZE))
        pygame.draw.rect(surface, (0, 255, 0), (interp_x, interp_y, BOX_SIZE, BOX_SIZE))
        pygame.draw.rect(surface, (255, 100, 0), (*self.food, BOX_SIZE, BOX_SIZE))

        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        high_text = font.render(f"High Score: {self.high_score}", True, (255, 255, 255))
        gen_text = font.render(f"Gen: {self.generation}", True, (255, 255, 255))

        surface.blit(score_text, (5, 5))
        surface.blit(high_text, (5, 5 + FONT_SIZE + 2))  # Below Score
        surface.blit(gen_text, (GRID_WIDTH - gen_text.get_width() - 5, 5))

# --- Main Setup ---
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Multi-AI Snake Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", FONT_SIZE)

# --- Initialize population and games ---
POPULATION_SIZE = NUM_GAMES
population = [NeuralNetwork() for _ in range(POPULATION_SIZE)]
games = [GameInstance(NeuralAIAgent(nn)) for nn in population]

engine = EvolutionEngine(games)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((10, 10, 10))
    all_done = True

    for idx, game in enumerate(games):
        game.update()

        if game.running:
            all_done = False
            
        col = idx % 2
        row = idx // 2
        subsurface = screen.subsurface((col * GRID_WIDTH, row * GRID_HEIGHT, GRID_WIDTH, GRID_HEIGHT))
        game.draw(subsurface, font)

    # Draw borders after all game draws:
    pygame.draw.line(screen, (0, 0, 139), (GRID_WIDTH, 0), (GRID_WIDTH, WINDOW_HEIGHT), BORDER_THICKNESS)
    pygame.draw.line(screen, (0, 0, 139), (0, GRID_HEIGHT), (WINDOW_WIDTH, GRID_HEIGHT), BORDER_THICKNESS)
    pygame.display.flip()
    clock.tick(60)


    #Evolution
    if all_done:
        # evaluate fitness use score
        fitness_score = [ #TODO: use a better fitness function
            game.score * 1000
            + game.score**2 * 50  # extra reward for more food
            + game.snake.__len__() * 2  # survival / exploration
            - game.idle_steps * 1
            for game in games
        ]


        print(f"Generation {generation} - Scores: {fitness_score}")

        best_fit = max(fitness_score)
        average_fit = sum(fitness_score) / len(fitness_score)
        best_fitnesses.append(best_fit)
        average_fitnesses.append(average_fit)

        engine.next_generation(games)

        generation += 1
        if generation >= GENERATION_LIMIT:
            break

import matplotlib.pyplot as plt
plt.figure(figsize=(10, 5))
plt.plot(best_fitnesses, label='Best Fitness')
plt.plot(average_fitnesses, label='Average Fitness')
plt.xlabel('Generation')
plt.ylabel('Fitness')
plt.title('Fitness over Generations')
plt.legend()
plt.grid(True)
plt.show()

#
fitnesses = EvolutionEngine.evaluate_fitness()
best_idx = np.argmax(fitnesses)
best_nn = EvolutionEngine.population[best_idx].agent.nn

np.savez('best_nn.npz', w1=best_nn.w1, w2=best_nn.w2)
data = np.load('best_nn.npz')
nn = NeuralNetwork()
nn.w1 = data['w1']
nn.w2 = data['w2']