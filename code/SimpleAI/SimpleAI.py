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

        # Handle case when there's no food
        if food is None:
            dx, dy = {
                'up': (0, -1),
                'down': (0, 1),
                'left': (-1, 0),
                'right': (1, 0),
            }[self.direction]
            new_x = head_x + dx * BOX_SIZE
            new_y = head_y + dy * BOX_SIZE
            
            # If current direction leads to collision, try to find a safe direction
            if not (0 <= new_x < WIDTH and 0 <= new_y < HEIGHT) or (new_x, new_y) in snake:
                for new_dir in ['up', 'right', 'down', 'left']:
                    if new_dir == self.direction or new_dir == {
                        'up': 'down', 'down': 'up',
                        'left': 'right', 'right': 'left'
                    }[self.direction]:
                        continue
                    dx, dy = {
                        'up': (0, -1),
                        'down': (0, 1),
                        'left': (-1, 0),
                        'right': (1, 0),
                    }[new_dir]
                    new_x = head_x + dx * BOX_SIZE
                    new_y = head_y + dy * BOX_SIZE
                    if 0 <= new_x < WIDTH and 0 <= new_y < HEIGHT and (new_x, new_y) not in snake:
                        self.direction = new_dir
                        return self.direction, (new_x, new_y)
            return self.direction, (new_x, new_y)

        # Correct direction mapping
        directions = {
            'up': (0, -1),
            'down': (0, 1),
            'left': (-1, 0),
            'right': (1, 0)
        }

        best_move = None
        min_dist = float('inf')
        backup_move = None

        # First, try to continue in current direction if it's safe and gets closer to food
        dx, dy = directions[self.direction]
        new_x = head_x + dx * BOX_SIZE
        new_y = head_y + dy * BOX_SIZE
        if (0 <= new_x < WIDTH and 0 <= new_y < HEIGHT and (new_x, new_y) not in snake):
            curr_dist = distance((new_x, new_y), food)
            if curr_dist < distance((head_x, head_y), food):
                return self.direction, (new_x, new_y)

        # If current direction isn't optimal, look for alternatives
        for dir, (dx, dy) in directions.items():
            # Prevent reversing
            if (self.direction == 'left' and dir == 'right') or \
               (self.direction == 'right' and dir == 'left') or \
               (self.direction == 'up' and dir == 'down') or \
               (self.direction == 'down' and dir == 'up'):
                continue

            new_x = head_x + dx * BOX_SIZE
            new_y = head_y + dy * BOX_SIZE
            
            # Check if move is valid
            if (0 <= new_x < WIDTH) and (0 <= new_y < HEIGHT) and ((new_x, new_y) not in snake):
                # Store as backup move if we haven't found one yet
                if backup_move is None:
                    backup_move = (dir, (new_x, new_y))
                
                # Calculate distance to food
                dist = distance((new_x, new_y), food)
                
                # Check if this position would be too close to snake body
                too_close = False
                for segment in snake[1:]:
                    if distance((new_x, new_y), segment) < BOX_SIZE * 2:
                        too_close = True
                        break
                
                if not too_close and dist < min_dist:
                    min_dist = dist
                    best_move = (dir, (new_x, new_y))

        if best_move:
            self.direction = best_move[0]
            return best_move
        elif backup_move:
            self.direction = backup_move[0]
            return backup_move
        else:
            # If no valid moves, try to find any safe move
            for dir, (dx, dy) in directions.items():
                new_x = head_x + dx * BOX_SIZE
                new_y = head_y + dy * BOX_SIZE
                if (0 <= new_x < WIDTH) and (0 <= new_y < HEIGHT) and ((new_x, new_y) not in snake):
                    self.direction = dir
                    return dir, (new_x, new_y)
            
            # If still no valid moves, stay in place (will likely lead to death)
            return self.direction, (head_x, head_y)

    def learn(self, reward):
        # Placeholder for learning logic
        pass #TODO: Implement learning logic
