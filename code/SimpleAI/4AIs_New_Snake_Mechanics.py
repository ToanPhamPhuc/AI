import pygame
import random
import sys

# --- Constants ---
GRID_WIDTH, GRID_HEIGHT = 680, 380
BOX_SIZE = 20
MOVE_FRAMES = 1  # Increased for smoother visualization
NUM_GAMES = 4
WINDOW_WIDTH, WINDOW_HEIGHT = 2 * GRID_WIDTH, 2 * GRID_HEIGHT
BORDER_THICKNESS = 4
FONT_SIZE = 16

# --- AI Agent ---
class SimpleAIAgent:
    def __init__(self):
        self.direction = 'right'

    def move(self, snake, food):
        head_x, head_y = snake[0]
        directions = {
            'left': (-1, 0),
            'right': (1, 0),
            'up': (0, -1),
            'down': (0, 1)
        }

        best_move = None
        min_dist = float('inf')

        for dir, (dx, dy) in directions.items():
            if (self.direction == 'left' and dir == 'right') or \
               (self.direction == 'right' and dir == 'left') or \
               (self.direction == 'up' and dir == 'down') or \
               (self.direction == 'down' and dir == 'up'):
                continue

            new_x = head_x + dx * BOX_SIZE
            new_y = head_y + dy * BOX_SIZE
            if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
                if (new_x, new_y) not in snake:
                    dist = abs(new_x - food[0]) + abs(new_y - food[1])
                    if dist < min_dist:
                        min_dist = dist
                        best_move = (dir, (new_x, new_y))

        if best_move:
            self.direction = best_move[0]
            return best_move
        else:
            valid_moves = []
            for dir, (dx, dy) in directions.items():
                new_x = head_x + dx * BOX_SIZE
                new_y = head_y + dy * BOX_SIZE
                if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
                    if (new_x, new_y) not in snake:
                        valid_moves.append((dir, (new_x, new_y)))
            if valid_moves:
                choice = random.choice(valid_moves)
                self.direction = choice[0]
                return choice
            else:
                return self.direction, (head_x, head_y)

    def learn(self, reward):
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
    def __init__(self):
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
        self.agent = SimpleAIAgent()

        # Initialize high_score only once (outside reset)
        if not hasattr(self, 'high_score'):
            self.high_score = 0

    def reset(self):
        # Save high_score before reset
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
            if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
                self.agent.learn(-10)
                self.reset()
                return

            if new_head in self.snake:
                hit_index = self.snake.index(new_head)
                if hit_index > 0:  # Ensure it's not hitting the head itself immediately
                    self.snake = self.snake[:hit_index]
                    self.agent.learn(-5) # Penalize self-collision
                else:
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
        for i, segment in enumerate(self.snake):
            color = (0, 200, 255) if i > 0 else (0, 255, 0) # Different color for the head
            pygame.draw.rect(surface, color, (*segment, BOX_SIZE, BOX_SIZE))
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

# Create 4 game instances
games = [GameInstance() for _ in range(NUM_GAMES)]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((10, 10, 10))
    for idx, game in enumerate(games):
        game.update()

        col = idx % 2
        row = idx // 2
        subsurface = screen.subsurface((col * GRID_WIDTH, row * GRID_HEIGHT, GRID_WIDTH, GRID_HEIGHT))
        game.draw(subsurface, font)

    # Draw borders after all game draws:
    pygame.draw.line(screen, (0, 0, 139), (GRID_WIDTH, 0), (GRID_WIDTH, WINDOW_HEIGHT), BORDER_THICKNESS)
    pygame.draw.line(screen, (0, 0, 139), (0, GRID_HEIGHT), (WINDOW_WIDTH, GRID_HEIGHT), BORDER_THICKNESS)

    pygame.display.flip()
    clock.tick(60)