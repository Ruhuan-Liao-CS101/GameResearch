import pygame
import os
import sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class FinalScene:
    def __init__(self, game_state):
        self.game_state = game_state
        # Get difficulty from game state
        self.difficulty = game_state.tetris_difficulty
        self.screen_width, self.screen_height = 900, 700

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (100, 200, 255)
        self.HOVER_BLUE = (150, 220, 255)
        self.GREEN = (100, 200, 100)
        self.YELLOW = (250, 200, 100)
        self.RED = (200, 100, 100)

        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.text_font = pygame.font.Font(None, 16)
        self.button_font = pygame.font.Font(None, 16)

        # Try to load custom font if available
        try:
            font_path = resource_path("TetrisGame/font/font.ttf")
            if os.path.exists(font_path):
                self.title_font = pygame.font.Font(font_path, 48)
                self.text_font = pygame.font.Font(font_path, 30)
                self.button_font = pygame.font.Font(font_path, 30)
            else:
                print(f"Font not found at: {font_path}")
        except Exception as e:
            # If custom font fails, fallback fonts
            print(f"Error loading font: {e}")
            pass

        # Background - try to load the same as Tetris or fall back to solid color
        try:
            bg_path = resource_path("TetrisGame/img/background2.webp")
            self.bg = pygame.image.load(bg_path).convert()
            print(f"Successfully loaded background: {bg_path}")
        except Exception as e:
            print(f"Error loading background: {e}")
            self.bg = pygame.Surface((self.screen_width, self.screen_height))
            self.bg.fill((40, 40, 40))

        # Message box
        self.message_box = pygame.Rect(
            50, 150, self.screen_width - 100, 250)

        self.continue_button = pygame.Rect(
            self.screen_width // 2 - 125, self.screen_height - 100, 250, 50)
        self.continue_hover = False

        # Set message content based on difficulty
        self.set_message_content()

    def set_message_content(self):
        """Set message content based on difficulty level"""
        if self.difficulty == 'easy':
            self.title_text = "EXCELLENT WORK!"
            self.message_text = [
                "Congratulations, you have made all the correct choices",
                "to rebuild the town's infrastructure!",
                "",
                "Your decisions will ensure that Bridgewater recovers",
                "quickly and efficiently from the disaster."
            ]
            self.box_color = self.GREEN
        else:  # medium or difficult
            self.title_text = "GOOD EFFORT!"
            self.message_text = [
                "Nice try, you were very close to making the correct",
                "choices to rebuild the town's infrastructure!",
                "",
                "Next time, pay more attention to the interviews because they will help you make better decisions"
            ]
            self.box_color = self.YELLOW

    def handle_events(self, event):
        """Handle user input events"""
        if event.type == pygame.MOUSEMOTION:
            # Update button hover states
            self.continue_hover = self.continue_button.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.continue_button.collidepoint(event.pos):
                # Go back to character selection scene
                self.game_state.current_scene = 'game_purpose'
                return

    def render(self, screen):
        """Render the final scene"""
        # Clear screen with background
        screen.blit(self.bg, (0, 0))

        # Draw title
        title_surface = self.title_font.render(
            self.title_text, True, self.BLACK)
        title_rect = title_surface.get_rect(centerx=self.screen_width//2, y=80)
        screen.blit(title_surface, title_rect)

        # Draw message box
        pygame.draw.rect(screen, self.box_color,
                         self.message_box, border_radius=10)
        pygame.draw.rect(screen, self.BLACK, self.message_box,
                         2, border_radius=10)

        # Draw message text with proper word wrapping to stay inside the box
        max_width = self.message_box.width - 40  # Leave 20px padding on each side
        y_offset = self.message_box.y + 20  # Start a bit higher

        for line in self.message_text:
            if not line:  # Skip empty lines
                y_offset += 15
                continue

            # Break long lines into multiple shorter lines if needed
            words = line.split()
            current_line = []
            current_width = 0

            for word in words:
                word_surface = self.text_font.render(
                    word + ' ', True, self.BLACK)
                word_width = word_surface.get_width()

                if current_width + word_width <= max_width:
                    current_line.append(word)
                    current_width += word_width
                else:
                    # Render current line and move to next line
                    if current_line:
                        text = ' '.join(current_line)
                        text_surface = self.text_font.render(
                            text, True, self.BLACK)
                        text_rect = text_surface.get_rect(
                            centerx=self.screen_width//2, y=y_offset)
                        screen.blit(text_surface, text_rect)
                        y_offset += 25

                    # Start a new line with the current word
                    current_line = [word]
                    current_width = word_width

            # Render any remaining text in the last line
            if current_line:
                text = ' '.join(current_line)
                text_surface = self.text_font.render(text, True, self.BLACK)
                text_rect = text_surface.get_rect(
                    centerx=self.screen_width//2, y=y_offset)
                screen.blit(text_surface, text_rect)
                y_offset += 25

         # Draw continue button
        button_color = self.HOVER_BLUE if self.continue_hover else self.BLUE
        pygame.draw.rect(screen, button_color,
                         self.continue_button, border_radius=5)
        continue_text = self.button_font.render("Continue", True, self.WHITE)
        continue_rect = continue_text.get_rect(
            center=self.continue_button.center)
        screen.blit(continue_text, continue_rect)
