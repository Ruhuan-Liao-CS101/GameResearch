import pygame
import os
import sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temporary folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class GamePurposeScene:
    def __init__(self, game_state):
        self.game_state = game_state
        self.screen_width, self.screen_height = 900, 700

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (100, 200, 255)
        self.HOVER_BLUE = (150, 220, 255)

        # Load background image to match act1_storyline
        try:
            self.background_image = pygame.image.load(
                resource_path('scenes/backgrounds/background2.webp'))
            self.background_image = pygame.transform.scale(
                self.background_image, (self.screen_width, self.screen_height))
        except pygame.error as e:
            print(f"Error loading background image: {e}")
            self.background_image = None

        # Fonts - match act1_storyline
        self.font = pygame.font.Font(None, 28)
        self.button_font = pygame.font.Font(None, 36)

        # Title and content - with each objective on a new line
        self.title = "Purpose of This Game"
        self.content_text = (
            "This project simulates the software engineering process through a disaster recovery scenario.\n"
            "\n"
            "Key Learning Objectives:\n"
            "\n"
            "1. Requirements Gathering: The interview phase demonstrates effective stakeholder\n"
            "   interviews and information collection techniques used in software requirements\n"
            "   gathering.\n"
            "\n"
            "2. Stakeholder Analysis: By talking to different community representatives, you\n"
            "   practice identifying diverse stakeholder needs and priorities, similar to\n"
            "   software project planning.\n"
            "\n"
            "3. Trade-off Decision Making: The multiple-choice phase simulates the engineering\n"
            "   decisions software teams make when balancing competing priorities with\n"
            "   limited resources.\n"
            "\n"
            "4. Outcome Evaluation: The difficulty of the Tetris game represents how each\n"
            "   software engineering decision impacts project implementation complexity and\n"
            "   long-term success.\n"
            "\n"
            "Thank you for experiencing this software engineering simulation!"
        )

        # Exit button setup - similar to continue button in storyline
        self.button_rect = pygame.Rect(self.screen_width // 2 - 75,
                                       self.screen_height - 100, 150, 50)
        self.button_color = (100, 200, 255)
        self.button_hover_color = (150, 220, 255)

    def handle_events(self, event):
        """Handle user input events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                if self.button_rect.collidepoint(mouse_pos):
                    # Exit the game
                    pygame.quit()
                    sys.exit()

    def render(self, screen):
        """Render the purpose scene with same style as act1_storyline"""
        # Check if background image is loaded
        if self.background_image:
            screen.blit(self.background_image, (0, 0))
        else:
            screen.fill(self.WHITE)

        # Render title
        title_surface = self.font.render(self.title, True, self.BLACK)
        title_rect = title_surface.get_rect(
            center=(self.screen_width // 2, 50))
        screen.blit(title_surface, title_rect)

        text_container_height = 450  # Increased height for the multi-line content
        text_container = pygame.Surface(
            (self.screen_width - 40, text_container_height))
        text_container.set_alpha(200)
        text_container.fill(self.WHITE)

        # Render wrapped text
        self._render_text_wrapped(text_container, self.content_text, 10, 10,
                                  self.font, self.BLACK, self.screen_width - 60)
        screen.blit(text_container, (20, 100))

        # Render exit button
        mouse_pos = pygame.mouse.get_pos()
        if self.button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.button_hover_color, self.button_rect)
        else:
            pygame.draw.rect(screen, self.button_color, self.button_rect)

        # Button text
        button_text = self.button_font.render("Exit", True, self.WHITE)
        button_text_rect = button_text.get_rect(center=self.button_rect.center)
        screen.blit(button_text, button_text_rect)

    def _render_text_wrapped(self, surface, text, x, y, font, color, max_width):
        """Modified text wrapping method that handles newlines"""
        # Split text by newlines first
        paragraphs = text.split('\n')
        line_height = font.get_height()

        current_y = y

        for paragraph in paragraphs:
            if not paragraph:  # Empty line/paragraph
                current_y += line_height
                continue

            words = paragraph.split(' ')
            space_width, _ = font.size(' ')
            current_line = []
            current_width = 0

            for word in words:
                word_surface = font.render(word, True, color)
                word_width, word_height = word_surface.get_size()

                if current_width + word_width <= max_width:
                    current_line.append(word)
                    current_width += word_width + space_width
                else:
                    # Render the current line
                    line_surface = font.render(
                        ' '.join(current_line), True, color)
                    surface.blit(line_surface, (x, current_y))
                    current_y += line_height
                    current_line = [word]
                    current_width = word_width + space_width

            # Render the last line of the paragraph
            if current_line:
                line_surface = font.render(' '.join(current_line), True, color)
                surface.blit(line_surface, (x, current_y))
                current_y += line_height
