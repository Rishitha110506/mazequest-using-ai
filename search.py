from collections import deque
import heapq
import random

def reconstruct_path(came_from, start, goal):
    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from.get(current)
        if current is None:
            return []
    path.reverse()
    return path

def bfs(start, goal, maze):
    frontier = deque([start])
    came_from = {start: None}
    while frontier:
        current = frontier.popleft()
        if current == goal:
            break
        for nxt in maze.get_neighbors(current):
            if nxt not in came_from:
                frontier.append(nxt)
                came_from[nxt] = current
    return reconstruct_path(came_from, start, goal)

def dfs(start, goal, maze):
    stack = [start]
    came_from = {start: None}
    while stack:
        current = stack.pop()
        if current == goal:
            break
        neighbors = maze.get_neighbors(current)
        random.shuffle(neighbors)  # Random order for varied DFS paths
        for nxt in neighbors:
            if nxt not in came_from:
                stack.append(nxt)
                came_from[nxt] = current
    return reconstruct_path(came_from, start, goal)

def ucs(start, goal, maze):
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    while frontier:
        cost, current = heapq.heappop(frontier)
        if current == goal:
            break
        for nxt in maze.get_neighbors(current):
            new_cost = cost_so_far[current] + 1
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                heapq.heappush(frontier, (new_cost, nxt))
                came_from[nxt] = current
    return reconstruct_path(came_from, start, goal)

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(start, goal, maze):
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    while frontier:
        _, current = heapq.heappop(frontier)
        if current == goal:
            break
        for nxt in maze.get_neighbors(current):
            new_cost = cost_so_far[current] + 1
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                priority = new_cost + heuristic(goal, nxt)
                heapq.heappush(frontier, (priority, nxt))
                came_from[nxt] = current
    return reconstruct_path(came_from, start, goal)

def gbfs(start, goal, maze):
    frontier = []
    heapq.heappush(frontier, (heuristic(start, goal), start))
    came_from = {start: None}
    visited = set([start])
    while frontier:
        _, current = heapq.heappop(frontier)
        if current == goal:
            break
        for nxt in maze.get_neighbors(current):
            if nxt not in visited:
                heapq.heappush(frontier, (heuristic(goal, nxt), nxt))
                came_from[nxt] = current
                visited.add(nxt)
    return reconstruct_path(came_from, start, goal)
