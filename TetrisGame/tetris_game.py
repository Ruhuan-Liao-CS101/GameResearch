import pygame
import os
from copy import deepcopy
from random import choice, randrange


class TetrisScene:
    def __init__(self, game_state, difficulty='easy'):
        self.game_state = game_state
        self.difficulty = difficulty.lower()

        # Set up paths
        self.base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        self.tetris_folder_path = os.path.join(self.base_dir, "TetrisGame")

        # Tetris constants
        self.W, self.H = 10, 15
        self.TILE = 45
        self.GAME_RES = self.W * self.TILE, self.H * self.TILE
        self.RES = 900, 700
        self.FPS = 60

        # Create game surface
        self.game_sc = pygame.Surface(self.GAME_RES)

        # Calculate positions based on resolution
        self.game_sc_x = 20
        # Center the game vertically
        self.game_sc_y = (self.RES[1] - self.GAME_RES[1]) // 2
        self.sidebar_x = self.game_sc_x + \
            self.GAME_RES[0] + 40  # Right side position

        # Create grid
        self.grid = [pygame.Rect(x * self.TILE, y * self.TILE, self.TILE, self.TILE)
                     for x in range(self.W) for y in range(self.H)]

        # Define figures positions
        self.figures_pos = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
                            [(0, -1), (-1, -1), (-1, 0), (0, 0)],
                            [(-1, 0), (-1, 1), (0, 0), (0, -1)],
                            [(0, 0), (-1, 0), (0, 1), (-1, -1)],
                            [(0, 0), (0, -1), (0, 1), (-1, -1)],
                            [(0, 0), (0, -1), (0, 1), (1, -1)],
                            [(0, 0), (0, -1), (0, 1), (-1, 0)]]

        self.figures = [[pygame.Rect(x + self.W // 2, y + 1, 1, 1)
                         for x, y in fig_pos] for fig_pos in self.figures_pos]

        self.figure_rect = pygame.Rect(0, 0, self.TILE - 2, self.TILE - 2)
        self.field = [[0 for i in range(self.W)] for j in range(self.H)]

        # Set difficulty parameters
        if self.difficulty == 'easy':
            self.anim_speed = 60
            self.anim_limit = 2000
            self.speed_increase = 2  # Smaller speed increase when clearing lines
        elif self.difficulty == 'medium':
            self.anim_speed = 80
            self.anim_limit = 1500
            self.speed_increase = 3
        else:  # difficult -> now hard
            self.difficulty = 'hard'  # Change 'difficult' to 'hard'
            self.anim_speed = 150     # Increased from 100 to 150
            self.anim_limit = 700     # Decreased from 1000 to 700
            self.speed_increase = 6   # Increased from 4 to 6

        self.anim_count = 0

        # Load assets
        try:
            self.bg = pygame.image.load(os.path.join(
                self.tetris_folder_path, 'img', 'img1.webp')).convert()
            self.game_bg = pygame.image.load(os.path.join(
                self.tetris_folder_path, 'img', 'photo1.jpeg')).convert()
        except pygame.error:
            # Fallback if specific images aren't available
            self.bg = pygame.Surface(self.RES)
            self.bg.fill((40, 40, 40))
            self.game_bg = pygame.Surface(self.GAME_RES)
            self.game_bg.fill((0, 0, 0))

        # Load fonts - BEFORE creating text
        try:
            self.main_font = pygame.font.Font(os.path.join(
                self.tetris_folder_path, 'font', 'font.ttf'), 65)
            self.font = pygame.font.Font(os.path.join(
                self.tetris_folder_path, 'font', 'font.ttf'), 45)
        except FileNotFoundError:
            # Fallback to default font
            self.main_font = pygame.font.Font(None, 65)
            self.font = pygame.font.Font(None, 45)

        # Create UI text elements
        self.title_tetris = self.main_font.render(
            'TETRIS', True, pygame.Color('darkorange'))

        # Create difficulty text with appropriate color
        difficulty_text = f"{self.difficulty.upper()} MODE"
        difficulty_color = pygame.Color('green')
        if self.difficulty == 'medium':
            difficulty_color = pygame.Color('yellow')
        elif self.difficulty == 'hard':  # Changed from 'difficult' to 'hard'
            difficulty_color = pygame.Color('red')
        self.title_difficulty = self.font.render(
            difficulty_text, True, difficulty_color)

        self.title_score = self.font.render(
            'SCORE:', True, pygame.Color('green'))

        # Initialize game variables
        self.figure, self.next_figure = deepcopy(
            choice(self.figures)), deepcopy(choice(self.figures))
        self.color, self.next_color = self.get_color(), self.get_color()

        self.score, self.lines = 0, 0
        self.scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}

        # Game state
        self.dx, self.rotate = 0, False
        self.game_over = False
        self.pause_lines = 0

    def set_difficulty(self, difficulty):
        """Set game parameters based on difficulty level"""
        self.difficulty = difficulty.lower()

        # Set initial game speed based on difficulty
        if self.difficulty == 'easy':
            self.anim_speed = 60
            self.anim_limit = 2000
            self.speed_increase = 2  # Smaller speed increase when clearing lines
        elif self.difficulty == 'medium':
            self.anim_speed = 80
            self.anim_limit = 1500
            self.speed_increase = 3
        else:  # Change difficult to hard
            self.difficulty = 'hard'  # Standardize 'difficult' to 'hard'
            self.anim_speed = 150     # Increased from 100 to 150
            self.anim_limit = 700     # Decreased from 1000 to 700
            self.speed_increase = 6   # Increased from 4 to 6

        # Update the difficulty text
        difficulty_text = f"{self.difficulty.upper()} MODE"
        difficulty_color = pygame.Color('green')
        if self.difficulty == 'medium':
            difficulty_color = pygame.Color('yellow')
        elif self.difficulty == 'hard':  # Changed from 'difficult' to 'hard'
            difficulty_color = pygame.Color('red')

        # Make sure font is initialized before rendering
        if hasattr(self, 'font'):
            self.title_difficulty = self.font.render(
                difficulty_text, True, difficulty_color)

    def get_color(self):
        return (randrange(30, 256), randrange(30, 256), randrange(30, 256))

    def check_borders(self):
        for i in range(4):
            if self.figure[i].x < 0 or self.figure[i].x > self.W - 1:
                return False
            elif self.figure[i].y > self.H - 1 or self.field[self.figure[i].y][self.figure[i].x]:
                return False
        return True

    def handle_events(self, event):
        """Handle Pygame events"""
        if event.type == pygame.QUIT:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.dx = -1
            elif event.key == pygame.K_RIGHT:
                self.dx = 1
            elif event.key == pygame.K_DOWN:
                self.anim_limit = 100
            elif event.key == pygame.K_UP:
                self.rotate = True

    def update(self):
        """Update game state"""
        # Process line deletion pause
        if self.pause_lines > 0:
            pygame.time.delay(200)
            self.pause_lines -= 1
            return

        # Move x
        figure_old = deepcopy(self.figure)
        for i in range(4):
            self.figure[i].x += self.dx
            if not self.check_borders():
                self.figure = deepcopy(figure_old)
                break

        # Rotate - BEFORE resetting flags
        center = self.figure[0]
        figure_old = deepcopy(self.figure)
        if self.rotate:
            for i in range(4):
                x = self.figure[i].y - center.y
                y = self.figure[i].x - center.x
                self.figure[i].x = center.x - x
                self.figure[i].y = center.y + y
                if not self.check_borders():
                    self.figure = deepcopy(figure_old)
                    break

        # Move y
        self.anim_count += self.anim_speed
        if self.anim_count > self.anim_limit:
            self.anim_count = 0
            figure_old = deepcopy(self.figure)
            for i in range(4):
                self.figure[i].y += 1
                if not self.check_borders():
                    for i in range(4):
                        self.field[figure_old[i].y][figure_old[i].x] = self.color
                    self.figure, self.color = self.next_figure, self.next_color
                    self.next_figure, self.next_color = deepcopy(
                        choice(self.figures)), self.get_color()

                    # Reset falling speed based on current difficulty
                    if self.difficulty == 'easy':
                        self.anim_limit = 2000
                    elif self.difficulty == 'medium':
                        self.anim_limit = 1500
                    else:  # difficult
                        self.anim_limit = 1000
                    break

        # Check lines
        line, lines = self.H - 1, 0
        for row in range(self.H - 1, -1, -1):
            count = 0
            for i in range(self.W):
                if self.field[row][i]:
                    count += 1
                self.field[line][i] = self.field[row][i]
            if count < self.W:
                line -= 1
            else:
                # Speed increase depends on difficulty
                self.anim_speed += self.speed_increase
                lines += 1

        # Set pause for line animation
        self.pause_lines = lines

        # Compute score
        self.score += self.scores[lines]

        # Check game over
        for i in range(self.W):
            if self.field[0][i]:
                self.field = [[0 for i in range(self.W)]
                              for i in range(self.H)]

                # Reset animation speed based on difficulty
                if self.difficulty == 'easy':
                    self.anim_speed = 60
                    self.anim_limit = 2000
                elif self.difficulty == 'medium':
                    self.anim_speed = 80
                    self.anim_limit = 1500
                else:  # hard mode (was difficult)
                    self.anim_speed = 150     # Increased from 100 to 150
                    self.anim_limit = 700     # Decreased from 1000 to 700

                self.anim_count = 0
                self.score = 0
                self.game_over = True
                break

        # Reset single-frame actions AFTER using them
        self.dx, self.rotate = 0, False

    def render(self, screen):
        """Render Tetris game on the main screen"""
        # Draw background
        screen.blit(self.bg, (0, 0))

        # Draw game background
        self.game_sc.blit(self.game_bg, (0, 0))

        # Draw grid
        [pygame.draw.rect(self.game_sc, (40, 40, 40), i_rect, 1)
         for i_rect in self.grid]

        # Draw figure
        for i in range(4):
            self.figure_rect.x = self.figure[i].x * self.TILE
            self.figure_rect.y = self.figure[i].y * self.TILE
            pygame.draw.rect(self.game_sc, self.color, self.figure_rect)

        # Draw field
        for y, raw in enumerate(self.field):
            for x, col in enumerate(raw):
                if col:
                    self.figure_rect.x, self.figure_rect.y = x * self.TILE, y * self.TILE
                    pygame.draw.rect(self.game_sc, col, self.figure_rect)

        # Blit game surface to main screen
        screen.blit(self.game_sc, (self.game_sc_x, self.game_sc_y))

        # Title position
        screen.blit(self.title_tetris, (self.sidebar_x, self.game_sc_y + 20))

        # Dfficulty text
        screen.blit(self.title_difficulty,
                    (self.sidebar_x, self.game_sc_y + 120))

        # Score text
        screen.blit(self.title_score, (self.sidebar_x,
                    self.game_sc_y + 200))
        # Space between score label and score value
        screen.blit(self.font.render(str(self.score), True, pygame.Color('white')),
                    (self.sidebar_x + 15, self.game_sc_y + 270))

        # Draw next figure with space
        next_figure_x = self.sidebar_x
        next_figure_y = self.game_sc_y + 450

        # Next Figure text
        next_text = self.font.render(
            "NEXT FIGURE", True, pygame.Color('white'))
        screen.blit(next_text, (next_figure_x, next_figure_y - 80))

        # Draw the next figure
        for i in range(4):
            self.figure_rect.x = self.next_figure[i].x * \
                self.TILE + next_figure_x
            self.figure_rect.y = self.next_figure[i].y * \
                self.TILE + next_figure_y
            pygame.draw.rect(screen, self.next_color, self.figure_rect)

        # Handle game over animation
        if self.game_over:
            for i_rect in self.grid:
                pygame.draw.rect(self.game_sc, self.get_color(), i_rect)
                screen.blit(self.game_sc, (self.game_sc_x, self.game_sc_y))
                pygame.display.flip()
                pygame.time.delay(1)  # Shorter delay for smoother integration
            self.game_over = False

            # Launch final scene
            self.game_state.tetris_difficulty = self.difficulty
            self.game_state.current_scene = 'final_scene'
