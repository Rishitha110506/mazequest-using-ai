class Agent:
    def __init__(self, maze, algorithm='astar'):
        self.maze = maze
        self.algorithm = algorithm
        self.goal = None
        self.reset()

    def reset(self):
        self.position = self.maze.agent_pos
        self.steps = 0
        self.path = []
        self.move_progress = 0
        self.move_speed = 5
        self.from_pos = self.position
        self.to_pos = self.position

    def set_algorithm(self, algorithm):
        self.algorithm = algorithm
        self.reset()
        self.compute_path()

    def set_goal(self, goal):
        self.goal = goal
        self.compute_path()

    def compute_path(self):
        from search import bfs, dfs, ucs, astar, gbfs
        if not self.goal:
            self.path = []
            return
        if self.algorithm == 'bfs':
            self.path = bfs(self.position, self.goal, self.maze)
        elif self.algorithm == 'dfs':
            self.path = dfs(self.position, self.goal, self.maze)
        elif self.algorithm == 'ucs':
            self.path = ucs(self.position, self.goal, self.maze)
        elif self.algorithm == 'astar':
            self.path = astar(self.position, self.goal, self.maze)
        elif self.algorithm == 'gbfs':
            self.path = gbfs(self.position, self.goal, self.maze)

    def move(self):
        if self.move_progress > 0:
            self.move_progress -= 1
            if self.move_progress == 0:
                self.position = self.to_pos
            return True
        if not self.path or self.position == self.goal:
            return False
        self.steps += 1
        self.from_pos = self.position
        self.to_pos = self.path.pop(0)
        self.move_progress = self.move_speed
        return True

    def get_draw_position(self):
        if self.move_progress == 0:
            return self.position
        ax, ay = self.from_pos
        bx, by = self.to_pos
        t = self.move_speed - self.move_progress
        return (ax + (bx - ax) * t / self.move_speed, ay + (by - ay) * t / self.move_speed)
