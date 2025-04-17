import os
import sys
import pygame


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temporary folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class StorylineScene:
    def __init__(self, game_state):
        self.game_state = game_state

        # Screen dimensions
        self.screen_width = 900
        self.screen_height = 700

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)

        # Load background image
        try:
            self.background_image = pygame.image.load(
                resource_path('scenes/backgrounds/background1.webp'))
            self.background_image = pygame.transform.scale(
                self.background_image, (self.screen_width, self.screen_height))
        except pygame.error as e:
            print(f"Error loading background image: {e}")
            self.background_image = None

        # Fonts
        self.font = pygame.font.Font(None, 28)
        self.button_font = pygame.font.Font(None, 28)

        # Story content
        self.title = "Chapter 1: The Aftermath"
        self.story_text = (
            "The town of Bridgewater has been struck by a devastating hurricane, causing widespread destruction. "
            "Roads are flooded, buildings are damaged, and critical services like electricity, water, and communication "
            "are severely disrupted. You're taking on the role of a Reconstruction Specialist tasked with coordinating "
            "the town's recovery efforts. With limited resources, you must interview key community representatives to "
            "understand their priorities and gather crucial insights. They will then need to make decisions on how to allocate "
            "resources and which parts of the town should be rebuilt first. Balancing immediate needs with long-term recovery "
            "goals will be essential as you weigh each representative's input."
        )

        # Button setup
        self.button_rect = pygame.Rect(self.screen_width // 2 - 75,
                                       self.screen_height - 100, 150, 50)
        self.button_color = (100, 200, 255)
        self.button_hover_color = (150, 250, 255)

        # Scene completion flag
        self.is_complete = False

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                if self.button_rect.collidepoint(mouse_pos):
                    self.is_complete = True
                    self.game_state.current_scene = 'act2_characters'

    def update(self):
        # Any scene-specific updates can go here
        pass

    def render(self, screen):
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

        # Create text container
        text_container_height = 400
        text_container = pygame.Surface(
            (self.screen_width - 40, text_container_height))
        text_container.set_alpha(200)
        text_container.fill(self.WHITE)

        # Render wrapped text
        self._render_text_wrapped(text_container, self.story_text, 10, 10,
                                  self.font, self.BLACK, self.screen_width - 60)
        screen.blit(text_container, (20, 100))

        # Render button
        mouse_pos = pygame.mouse.get_pos()
        if self.button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.button_hover_color, self.button_rect)
        else:
            pygame.draw.rect(screen, self.button_color, self.button_rect)

        # Button text
        button_text = self.button_font.render("Continue", True, self.WHITE)
        button_text_rect = button_text.get_rect(center=self.button_rect.center)
        screen.blit(button_text, button_text_rect)

    def _render_text_wrapped(self, surface, text, x, y, font, color, max_width):
        words = text.split(' ')
        space_width, _ = font.size(' ')
        current_line = []
        current_width = 0
        line_height = font.get_height()

        for word in words:
            word_surface = font.render(word, True, color)
            word_width, word_height = word_surface.get_size()

            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width + space_width
            else:
                # Render the current line
                line_surface = font.render(' '.join(current_line), True, color)
                surface.blit(line_surface, (x, y))
                y += line_height
                current_line = [word]
                current_width = word_width + space_width

        # Render the last line
        if current_line:
            line_surface = font.render(' '.join(current_line), True, color)
            surface.blit(line_surface, (x, y))
