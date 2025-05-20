# SimpleAI.py

import random
from config import WIDTH, HEIGHT, BOX_SIZE, distance

class SimpleAIAgent:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.direction = 'right'

    def move(self, snake, food):
        head_x, head_y = snake[0]
        directions = {
            'left':  (-1,  0),
            'right': ( 1,  0),
            'up':    ( 0, -1),
            'down':  ( 0,  1)
        }

        best_move = None
        min_dist = float('inf')

        for dir, (dx, dy) in directions.items():
            # Prevent reversing
            if (self.direction == 'left' and dir == 'right') or \
               (self.direction == 'right' and dir == 'left') or \
               (self.direction == 'up' and dir == 'down') or \
               (self.direction == 'down' and dir == 'up'):
                continue

            new_x = head_x + dx * BOX_SIZE
            new_y = head_y + dy * BOX_SIZE
            if (0 <= new_x < WIDTH) and (0 <= new_y < HEIGHT) and ((new_x, new_y) not in snake):
                dist = distance((new_x, new_y), food)
                if dist < min_dist:
                    min_dist = dist
                    best_move = (dir, (new_x, new_y))

        if best_move:
            self.direction = best_move[0]
            return best_move
        else:
            # Fallback to random move
            valid_moves = []
            for dir, (dx, dy) in directions.items():
                new_x = head_x + dx * BOX_SIZE
                new_y = head_y + dy * BOX_SIZE
                if (0 <= new_x < WIDTH) and (0 <= new_y < HEIGHT) and ((new_x, new_y) not in snake):
                    valid_moves.append((dir, (new_x, new_y)))
            if valid_moves:
                choice = random.choice(valid_moves)
                self.direction = choice[0]
                return choice
            else:
                return self.direction, (head_x, head_y)

    def learn(self, reward):
        # Placeholder for learning logic
        pass
