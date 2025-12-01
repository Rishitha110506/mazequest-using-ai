import pygame
import sys
from maze import Maze
from agent import Agent
import random

pygame.init()
pygame.font.init()

CELLSIZE = 32
MAZEWIDTH, MAZEHEIGHT = 21, 21
SIDEBARWIDTH = 700  # The sidebar is now very wide!
SCREENWIDTH = CELLSIZE * MAZEWIDTH + SIDEBARWIDTH
SCREENHEIGHT = CELLSIZE * MAZEHEIGHT
screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption("Maze Quest AI")

clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 22)
fontsmall = pygame.font.SysFont("Arial", 18)
bigfont = pygame.font.SysFont("Arial", 34, True)

wallimg = pygame.Surface((CELLSIZE, CELLSIZE))
wallimg.fill((50, 120, 200))
agentimg = pygame.Surface((CELLSIZE, CELLSIZE))
agentimg.fill((50, 200, 50))
exitimg = pygame.Surface((CELLSIZE, CELLSIZE))
exitimg.fill((255, 140, 0))

ALGORITHMS = ['bfs', 'dfs', 'ucs', 'astar', 'gbfs']
algonames = {
    'bfs': "BFS",
    'dfs': "DFS",
    'ucs': "UCS",
    'astar': "A*",
    'gbfs': "GBFS"
}
COMPLEXITIES = {
    'bfs': ("O(V + E)", "O(V)"),
    'dfs': ("O(V + E)", "O(V)"),
    'ucs': ("O(E + V log V)", "O(V)"),
    'astar': ("O(E), worst O(b^d)", "O(V)"),
    'gbfs': ("O(E), worst O(b^d)", "O(V)")
}
results = {}

currentalgoindex = 0
stopsimulation = False
alldone = False

def findrandomexit(maze):
    border = []
    w, h = maze.width, maze.height
    for x in range(w):
        if (x, 0) not in maze.walls and (x, 0) != maze.agent_pos:
            border.append((x, 0))
        if (x, h - 1) not in maze.walls and (x, h - 1) != maze.agent_pos:
            border.append((x, h - 1))
    for y in range(1, h - 1):
        if (0, y) not in maze.walls and (0, y) != maze.agent_pos:
            border.append((0, y))
        if (w - 1, y) not in maze.walls and (w - 1, y) != maze.agent_pos:
            border.append((w - 1, y))
    return random.choice(border) if border else (w - 2, h - 2)

def drawmaze(maze, agent):
    for y in range(maze.height):
        for x in range(maze.width):
            pos = (x, y)
            rect = pygame.Rect(x * CELLSIZE, y * CELLSIZE, CELLSIZE, CELLSIZE)
            if pos in maze.walls:
                screen.blit(wallimg, rect)
            else:
                pygame.draw.rect(screen, (22, 30, 22), rect)
            if hasattr(maze, 'exitpos') and pos == maze.exitpos:
                screen.blit(exitimg, rect)
    pos = agent.get_draw_position()
    rect = pygame.Rect(int(pos[0]) * CELLSIZE, int(pos[1]) * CELLSIZE, CELLSIZE, CELLSIZE)
    screen.blit(agentimg, rect)

def drawcomparisontable(resultdict, starty, sidebarx):
    y = starty
    rowh = 34
    headers = ["Algorithm", "Steps", "Time Complexity", "Space Complexity"]
    x_offsets = [
        sidebarx + 15,
        sidebarx + 120,
        sidebarx + 255,
        sidebarx + 450
    ]
    for i, header in enumerate(headers):
        head = font.render(header, True, (255, 255, 255))
        screen.blit(head, (x_offsets[i], y))
    y += rowh
    pygame.draw.line(screen, (220, 220, 220), (sidebarx + 8, y), (sidebarx + SIDEBARWIDTH - 30, y), 2)
    y += 6
    for alg in ALGORITHMS:
        algdisplay = fontsmall.render(algonames.get(alg, alg), True, (255, 255, 180))
        res = resultdict.get(alg, {})
        steps = str(res.get('steps', '-')) if res else '-'
        stepdisplay = fontsmall.render(steps, True, (255, 255, 255))
        timecomp, spacecomp = COMPLEXITIES.get(alg, ("-", "-"))
        timecompdisplay = fontsmall.render(timecomp, True, (255, 255, 255))
        spacecompdisplay = fontsmall.render(spacecomp, True, (255, 255, 255))
        screen.blit(algdisplay, (x_offsets[0], y))
        screen.blit(stepdisplay, (x_offsets[1], y))
        screen.blit(timecompdisplay, (x_offsets[2], y))
        screen.blit(spacecompdisplay, (x_offsets[3], y))
        y += rowh
    return y

def drawsidebar(agent, currentalgokey, alldone):
    sidebarx = CELLSIZE * MAZEWIDTH + 12
    sidebarrect = pygame.Rect(sidebarx - 8, 0, SIDEBARWIDTH, SCREENHEIGHT)
    pygame.draw.rect(screen, (50, 50, 50), sidebarrect)

    y = 26
    screen.blit(bigfont.render("Maze Quest AI", True, (255, 255, 255)), (sidebarx, y))
    y += 44
    screen.blit(font.render("About Game", True, (200, 255, 180)), (sidebarx, y))
    y += 27
    about_lines = [
        "Five pathfinding algorithms,",
        "race to solve the maze!",
        "Results compared below."
    ]
    for line in about_lines:
        screen.blit(fontsmall.render(line, True, (222, 255, 220)), (sidebarx, y))
        y += 22
    y += 6
    screen.blit(font.render("Instructions", True, (220, 220, 255)), (sidebarx, y))
    y += 27
    instructions_lines = [
        "S - Pause/Resume",
        "R - New Maze / Restart",
        "Close window - Exit"
    ]
    for line in instructions_lines:
        screen.blit(fontsmall.render(line, True, (210, 210, 255)), (sidebarx, y))
        y += 21
    y += 17

    if alldone:
        currentstr = "All Results Below!"
    else:
        currentstr = f"Running {algonames.get(currentalgokey, currentalgokey)} - Steps: {agent.steps}"
    screen.blit(font.render(currentstr, True, (255, 255, 180)), (sidebarx, y))
    y += 33
    drawcomparisontable(results, y, sidebarx)

def resetgame():
    global maze, agent, currentalgoindex, stopsimulation, results, alldone

    while True:
        maze = Maze(MAZEWIDTH, MAZEHEIGHT)
        maze.exitpos = findrandomexit(maze)
        maze.walls.discard(maze.exitpos)
        agent = Agent(maze, None)
        agent.goal = maze.exitpos
        agent.reset()
        agent.set_algorithm(ALGORITHMS[0])
        if agent.path:
            break

    currentalgoindex = 0
    stopsimulation = False
    alldone = False
    results.clear()

def main():
    global stopsimulation, results, currentalgoindex, agent, alldone
    resetgame()
    running = True
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    stopsimulation = not stopsimulation
                elif event.key == pygame.K_r:
                    resetgame()

        if currentalgoindex < len(ALGORITHMS) and not stopsimulation and not alldone:
            currentalgokey = ALGORITHMS[currentalgoindex]
            if agent.position == agent.goal or not agent.path:
                results[currentalgokey] = {'steps': agent.steps}
                currentalgoindex += 1
                if currentalgoindex < len(ALGORITHMS):
                    agent = Agent(maze, None)
                    agent.goal = maze.exitpos
                    agent.reset()
                    agent.set_algorithm(ALGORITHMS[currentalgoindex])
                else:
                    alldone = True
            else:
                agent.move()
        else:
            if currentalgoindex >= len(ALGORITHMS):
                alldone = True

        drawmaze(maze, agent)
        currentalgokey = ALGORITHMS[currentalgoindex] if currentalgoindex < len(ALGORITHMS) else ALGORITHMS[-1]
        drawsidebar(agent, currentalgokey, alldone)

        pygame.display.flip()
        clock.tick(30)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
