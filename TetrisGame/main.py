import pygame
from copy import deepcopy
from random import choice, randrange
import sys

# Check if difficulty is passed as command line argument
difficulty = 'easy'  # Default difficulty
if len(sys.argv) > 1:
    arg_difficulty = sys.argv[1].lower()
    if arg_difficulty in ['easy', 'medium', 'difficult']:
        difficulty = arg_difficulty

W, H = 10, 15
TILE = 45
GAME_RES = W * TILE, H * TILE
RES = 900, 700  # Updated resolution
FPS = 60

# Set difficulty-specific parameters
if difficulty == 'easy':
    anim_speed, anim_limit = 60, 2000
    speed_increase = 3
elif difficulty == 'medium':
    anim_speed, anim_limit = 80, 1500
    speed_increase = 4
else:  # difficult
    anim_speed, anim_limit = 1000, 1000
    speed_increase = 100

pygame.init()
sc = pygame.display.set_mode(RES)
pygame.display.set_caption(f"TETRIS - {difficulty.upper()} MODE")
game_sc = pygame.Surface(GAME_RES)
clock = pygame.time.Clock()

grid = [pygame.Rect(x * TILE, y * TILE, TILE, TILE)
        for x in range(W) for y in range(H)]

figures_pos = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
               [(0, -1), (-1, -1), (-1, 0), (0, 0)],
               [(-1, 0), (-1, 1), (0, 0), (0, -1)],
               [(0, 0), (-1, 0), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, 0)]]

figures = [[pygame.Rect(x + W // 2, y + 1, 1, 1)
            for x, y in fig_pos] for fig_pos in figures_pos]
figure_rect = pygame.Rect(0, 0, TILE - 2, TILE - 2)
field = [[0 for i in range(W)] for j in range(H)]

anim_count = 0

bg = pygame.image.load('img/img1.webp').convert()
game_bg = pygame.image.load('img/bg2.jpg').convert()

main_font = pygame.font.Font('font/font.ttf', 65)
font = pygame.font.Font('font/font.ttf', 45)

title_tetris = main_font.render('TETRIS', True, pygame.Color('darkorange'))
title_score = font.render('score:', True, pygame.Color('green'))
title_record = font.render('record:', True, pygame.Color('purple'))

# Create difficulty text with appropriate color
difficulty_color = pygame.Color('green')
if difficulty == 'medium':
    difficulty_color = pygame.Color('yellow')
elif difficulty == 'difficult':
    difficulty_color = pygame.Color('red')
title_difficulty = font.render(
    f"{difficulty.upper()} MODE", True, difficulty_color)

# Calculate positions based on new resolution
game_sc_x = 20
game_sc_y = (RES[1] - GAME_RES[1]) // 2  # Center the game vertically
sidebar_x = game_sc_x + GAME_RES[0] + 40  # Right side position


def get_color(): return (randrange(30, 256), randrange(30, 256), randrange(30, 256))


figure, next_figure = deepcopy(choice(figures)), deepcopy(choice(figures))
color, next_color = get_color(), get_color()

score, lines = 0, 0
scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}


def check_borders():
    if figure[i].x < 0 or figure[i].x > W - 1:
        return False
    elif figure[i].y > H - 1 or field[figure[i].y][figure[i].x]:
        return False
    return True


def get_record():
    record_file = f'record_{difficulty}'
    try:
        with open(record_file) as f:
            return f.readline()
    except FileNotFoundError:
        with open(record_file, 'w') as f:
            f.write('0')
        return '0'


def set_record(record, score):
    record_file = f'record_{difficulty}'
    rec = max(int(record), score)
    with open(record_file, 'w') as f:
        f.write(str(rec))


while True:
    record = get_record()
    dx, rotate = 0, False
    sc.blit(bg, (0, 0))
    sc.blit(game_sc, (game_sc_x, game_sc_y))  # Updated position
    game_sc.blit(game_bg, (0, 0))

    # delay for full lines
    for i in range(lines):
        pygame.time.wait(200)

    # control
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1
            elif event.key == pygame.K_DOWN:
                anim_limit = 100
            elif event.key == pygame.K_UP:
                rotate = True

    # move x
    figure_old = deepcopy(figure)
    for i in range(4):
        figure[i].x += dx
        if not check_borders():
            figure = deepcopy(figure_old)
            break

    # move y
    anim_count += anim_speed
    if anim_count > anim_limit:
        anim_count = 0
        figure_old = deepcopy(figure)
        for i in range(4):
            figure[i].y += 1
            if not check_borders():
                for i in range(4):
                    field[figure_old[i].y][figure_old[i].x] = color
                figure, color = next_figure, next_color
                next_figure, next_color = deepcopy(
                    choice(figures)), get_color()
                # Reset falling speed based on difficulty
                if difficulty == 'easy':
                    anim_limit = 2000
                elif difficulty == 'medium':
                    anim_limit = 1500
                else:  # difficult
                    anim_limit = 1000
                break

    # rotate
    center = figure[0]
    figure_old = deepcopy(figure)
    if rotate:
        for i in range(4):
            x = figure[i].y - center.y
            y = figure[i].x - center.x
            figure[i].x = center.x - x
            figure[i].y = center.y + y
            if not check_borders():
                figure = deepcopy(figure_old)
                break

    # check lines
    line, lines = H - 1, 0
    for row in range(H - 1, -1, -1):
        count = 0
        for i in range(W):
            if field[row][i]:
                count += 1
            field[line][i] = field[row][i]
        if count < W:
            line -= 1
        else:
            anim_speed += speed_increase  # Use difficulty-specific speed increase
            lines += 1

    # compute score
    score += scores[lines]

    # draw grid
    [pygame.draw.rect(game_sc, (40, 40, 40), i_rect, 1) for i_rect in grid]

    # draw figure
    for i in range(4):
        figure_rect.x = figure[i].x * TILE
        figure_rect.y = figure[i].y * TILE
        pygame.draw.rect(game_sc, color, figure_rect)

    # draw field
    for y, raw in enumerate(field):
        for x, col in enumerate(raw):
            if col:
                figure_rect.x, figure_rect.y = x * TILE, y * TILE
                pygame.draw.rect(game_sc, col, figure_rect)

    # draw next figure
    next_figure_x = sidebar_x
    next_figure_y = game_sc_y + 100
    for i in range(4):
        figure_rect.x = next_figure[i].x * TILE + next_figure_x
        figure_rect.y = next_figure[i].y * TILE + next_figure_y
        pygame.draw.rect(sc, next_color, figure_rect)

    # draw titles with adjusted positions
    sc.blit(title_tetris, (sidebar_x, game_sc_y + 20))
    # Display difficulty
    sc.blit(title_difficulty, (sidebar_x, game_sc_y + 80))
    sc.blit(title_score, (sidebar_x, game_sc_y + 200))
    sc.blit(font.render(str(score), True, pygame.Color('white')),
            (sidebar_x + 15, game_sc_y + 250))
    sc.blit(title_record, (sidebar_x, game_sc_y + 300))
    sc.blit(font.render(record, True, pygame.Color('gold')),
            (sidebar_x + 15, game_sc_y + 350))

    # game over
    for i in range(W):
        if field[0][i]:
            set_record(record, score)
            field = [[0 for i in range(W)] for i in range(H)]
            # Reset animation parameters based on difficulty
            if difficulty == 'easy':
                anim_speed, anim_limit = 60, 2000
            elif difficulty == 'medium':
                anim_speed, anim_limit = 80, 1500
            else:  # difficult
                anim_speed, anim_limit = 100, 1000
            anim_count = 0
            score = 0
            for i_rect in grid:
                pygame.draw.rect(game_sc, get_color(), i_rect)
                sc.blit(game_sc, (game_sc_x, game_sc_y))
                pygame.display.flip()
                clock.tick(200)

    pygame.display.flip()
    clock.tick(FPS)
