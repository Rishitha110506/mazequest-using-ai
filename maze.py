import random

class Maze:
    def __init__(self, width, height, extra_walls_to_remove=20):
        self.width = width if width % 2 == 1 else width + 1
        self.height = height if height % 2 == 1 else height + 1
        self.agent_pos = (1, 1)
        self.extra_walls_to_remove = extra_walls_to_remove
        self.walls = set()
        self.generate_maze()

    def generate_maze(self):
        self.walls = {(x, y) for x in range(self.width) for y in range(self.height)}
        def backtrack(x, y):
            self.walls.discard((x, y))
            directions = [(2,0), (-2,0), (0,2), (0,-2)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 1 <= nx < self.width - 1 and 1 <= ny < self.height - 1 and (nx, ny) in self.walls:
                    self.walls.discard((x + dx//2, y + dy//2))
                    backtrack(nx, ny)
        backtrack(1, 1)
        for x in range(self.width):
            self.walls.add((x, 0))
            self.walls.add((x, self.height-1))
        for y in range(self.height):
            self.walls.add((0, y))
            self.walls.add((self.width-1, y))
        self.remove_random_walls(self.extra_walls_to_remove)

    def remove_random_walls(self, count):
        potential_walls = [wall for wall in self.walls if self.is_removable(wall)]
        random.shuffle(potential_walls)
        removed = 0
        for wall in potential_walls:
            if removed >= count:
                break
            self.walls.remove(wall)
            removed += 1

    def is_removable(self, pos):
        # Only remove walls that are between two paths, i.e., walls that can open multiple routes
        x, y = pos
        if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
            return False  # Do not remove border walls
        adjacent_paths = 0
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) not in self.walls:
                adjacent_paths += 1
        return adjacent_paths == 2  # Must be a wall between two path cells

    def get_neighbors(self, pos):
        neighbors = []
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            nx, ny = pos[0]+dx, pos[1]+dy
            if 0 <= nx < self.width and 0 <= ny < self.height and (nx, ny) not in self.walls:
                neighbors.append((nx, ny))
        random.shuffle(neighbors)
        return neighbors

    def is_wall(self, pos):
        return pos in self.walls
