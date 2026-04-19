import pygame
import sys
import random

pygame.init()

# cell and screen size
CELL   = 20
COLS   = 30
ROWS   = 30
WIDTH  = CELL * COLS
HEIGHT = CELL * ROWS
INFO_H = 40   # height of score panel on top

# colors
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
GREEN      = (0,   200, 0)
DARK_GREEN = (0,   140, 0)
RED        = (220, 0,   0)
GRAY       = (40,  40,  40)
WALL_COLOR = (80,  80,  80)
GOLD       = (255, 215, 0)

# directions
UP    = (0,  -1)
DOWN  = (0,   1)
LEFT  = (-1,  0)
RIGHT = (1,   0)

# level settings - new level every 3 foods eaten
FOOD_PER_LEVEL = 3
BASE_SPEED     = 8   # starting speed (frames per second)
SPEED_STEP     = 2   # speed increase per level

# window setup
screen = pygame.display.set_mode((WIDTH, HEIGHT + INFO_H))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

font       = pygame.font.SysFont("Verdana", 18)
font_big   = pygame.font.SysFont("Verdana", 36)
font_small = pygame.font.SysFont("Verdana", 22)


# returns a rect for a given cell position
def cell_rect(col, row):
    return pygame.Rect(col * CELL, INFO_H + row * CELL, CELL, CELL)


# builds a set of wall coordinates around the border
def build_walls():
    walls = set()
    for c in range(COLS):
        walls.add((c, 0))           # top wall
        walls.add((c, ROWS - 1))    # bottom wall
    for r in range(ROWS):
        walls.add((0, r))           # left wall
        walls.add((COLS - 1, r))    # right wall
    return walls


# generates food position - not on a wall or snake body
def spawn_food(walls, snake):
    occupied = walls | set(snake)
    free = [
        (c, r)
        for c in range(1, COLS - 1)
        for r in range(1, ROWS - 1)
        if (c, r) not in occupied
    ]
    return random.choice(free) if free else None


# draws score and level panel at the top
def draw_info(score, level):
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, INFO_H))
    score_surf = font.render(f"score: {score}", True, WHITE)
    level_surf = font.render(f"level: {level}", True, GOLD)
    screen.blit(score_surf, (10, 10))
    screen.blit(level_surf, (WIDTH - level_surf.get_width() - 10, 10))


# draws the field: background, walls, food and snake
def draw_field(walls, snake, food):
    # background
    pygame.draw.rect(screen, GRAY, (0, INFO_H, WIDTH, HEIGHT))

    # walls around the border
    for (c, r) in walls:
        pygame.draw.rect(screen, WALL_COLOR, cell_rect(c, r))

    # food as a red circle
    if food:
        pygame.draw.ellipse(screen, RED, cell_rect(*food))

    # snake body - head is darker
    for i, (c, r) in enumerate(snake):
        color = DARK_GREEN if i == 0 else GREEN
        pygame.draw.rect(screen, color, cell_rect(c, r))
        pygame.draw.rect(screen, BLACK, cell_rect(c, r), 1)  # grid border


# shows game over screen and waits for keypress
def show_game_over(score):
    screen.fill(BLACK)
    over  = font_big.render("game over", True, RED)
    sc    = font_small.render(f"score: {score}", True, WHITE)
    again = font.render("press r to restart or q to quit", True, GRAY)
    screen.blit(over,  (WIDTH // 2 - over.get_width()  // 2, 200))
    screen.blit(sc,    (WIDTH // 2 - sc.get_width()    // 2, 270))
    screen.blit(again, (WIDTH // 2 - again.get_width() // 2, 330))
    pygame.display.update()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return True   # restart
                if e.key == pygame.K_q:               # quit
                    pygame.quit(); sys.exit()


# resets all game variables to starting state
def reset_game(walls):
    snake     = [(5, 5), (4, 5), (3, 5)]  # starting snake position
    direction = RIGHT
    food      = spawn_food(walls, snake)
    score     = 0
    level     = 1
    eaten     = 0   # how many foods eaten on this level
    speed     = BASE_SPEED
    return snake, direction, food, score, level, eaten, speed


# main game loop
walls = build_walls()
snake, direction, food, score, level, eaten, speed = reset_game(walls)
next_dir = direction   # buffer for next direction to avoid instant reverse

while True:

    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            # change direction - can't go directly opposite
            if event.key == pygame.K_UP    and direction != DOWN:  next_dir = UP
            if event.key == pygame.K_DOWN  and direction != UP:    next_dir = DOWN
            if event.key == pygame.K_LEFT  and direction != RIGHT: next_dir = LEFT
            if event.key == pygame.K_RIGHT and direction != LEFT:  next_dir = RIGHT

    direction = next_dir

    # calculate new head position
    head     = snake[0]
    new_head = (head[0] + direction[0], head[1] + direction[1])

    # check wall collision
    if new_head in walls:
        if show_game_over(score):
            snake, direction, food, score, level, eaten, speed = reset_game(walls)
            next_dir = direction
        continue

    # check self collision
    if new_head in snake:
        if show_game_over(score):
            snake, direction, food, score, level, eaten, speed = reset_game(walls)
            next_dir = direction
        continue

    # move snake - add new head
    snake.insert(0, new_head)

    # check if snake ate the food
    if new_head == food:
        score += 10
        eaten += 1

        # check if we reached next level
        if eaten >= FOOD_PER_LEVEL:
            level += 1
            eaten  = 0
            speed += SPEED_STEP   # increase speed on level up

        food = spawn_food(walls, snake)   # spawn new food
    else:
        snake.pop()   # remove tail if no food eaten

    # draw everything
    draw_field(walls, snake, food)
    draw_info(score, level)
    pygame.display.update()
    clock.tick(speed)