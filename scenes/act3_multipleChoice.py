import pygame
import subprocess
import os
import sys


class DecisionDescriptionScene:
    def __init__(self, game_state):
        self.game_state = game_state
        self.screen_width, self.screen_height = 900, 700

        # Colors and Fonts
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)
        self.LIGHT_BLUE = (100, 200, 255)
        self.HOVER_BLUE = (150, 220, 255)
        self.text_font = pygame.font.Font(None, 28)
        self.option_font = pygame.font.Font(None, 24)

        # Back button
        self.back_button = pygame.Rect(50, self.screen_height - 80, 100, 35)
        self.back_button_hover = False

        # Continue button
        self.continue_button = pygame.Rect(
            self.screen_width - 150, self.screen_height - 80, 100, 35)
        self.continue_button_hover = False

        # Button hover states
        self.continue_button_color = {
            'active': (100, 200, 255),
            'hover': (150, 220, 255)
        }
        self.button_font = pygame.font.Font(None, 28)

        # Layout dimensions
        self.description_box = pygame.Rect(
            50, 10, self.screen_width - 100, 150)
        self.questions_start_y = 170

        # Question box dimensions (adjusted for new screen width)
        box_width = 250  # Increased from 220
        spacing = 40     # Space between boxes
        start_x = (self.screen_width - (3 * box_width + 2 * spacing)) // 2

        self.question_boxes = [
            pygame.Rect(start_x, self.questions_start_y, box_width, 350),
            pygame.Rect(start_x + box_width + spacing,
                        self.questions_start_y, box_width, 350),
            pygame.Rect(start_x + 2 * (box_width + spacing),
                        self.questions_start_y, box_width, 350)
        ]

       # Description text will be chosen based on question count in render method
        self.complete_description = [
            "Now that the interviews are complete, it's time to make critical decisions",
            "about the town's recovery. Your choices will determine how effectively",
            "Bridgewater is rebuilt and how satisfied the community members will be",
            "with the outcome. Keep in mind that some priorities may conflict, and",
            "addressing one need might delay another. Every decision impacts the",
            "town's recovery percentage.",
            "",
            "Your choices matter—choose wisely!"
        ]

        self.incomplete_description = [
            "You haven't interviewed all community members yet! To make informed",
            "decisions about Bridgewater's recovery, you need to gather more",
            "information. Please go back to the previous screen and select all",
            "16 interview questions to understand everyone's needs and priorities,",
            "in order to answer the following three decision making questions.",
            "",
            "Remember: Every perspective is crucial for the town's recovery."
        ]

        self.description_text = self.incomplete_description  # Default to incomplete

        # Questions
        self.questions = [
            {
                'text': 'Given the limited resources, which of the following should be prioritized for immediate recovery?',
                'options': [
                    'Repainting public buildings',
                    'Setting up a town festival',
                    'Clearing main roads'
                ],
                'correct': 2
            },
            {
                'text': 'What infrastructure improvement would most enhance the town\'s resilience against future storms?',
                'options': [
                    'Strengthening school playground equipment',
                    'Installing a storm-resistant storage facility',
                    'Purchasing decorative lights for public areas'
                ],
                'correct': 1
            },
            {
                'text': 'What communication method would be most effective for keeping residents informed during the recovery?',
                'options': [
                    'Setting up information booths and radio updates',
                    'Organizing social media posts celebrating achievements',
                    'Hosting weekly in-person meetings with all residents'
                ],
                'correct': 0
            }
        ]

        self.selected_answers = [None] * len(self.questions)
        self.hovered_option = None
        self.option_rects = [[], [], []]
        self.is_complete = False

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Add at the start of the handle_events method:
            if self.back_button.collidepoint(event.pos):
                self.game_state.current_scene = 'act2_characters'
                return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.continue_button.collidepoint(event.pos) and None not in self.selected_answers:
                self.calculate_score()
                self.game_state.current_scene = 'tetris'
                return

            for i, question_options in enumerate(self.option_rects):
                for j, option_rect in enumerate(question_options):
                    if option_rect.collidepoint(event.pos):
                        self.selected_answers[i] = j

        elif event.type == pygame.MOUSEMOTION:
            # Update both button hover states
            self.back_button_hover = self.back_button.collidepoint(event.pos)
            self.continue_hover = (self.continue_button.collidepoint(event.pos) and
                                   None not in self.selected_answers)

            # Update option hover state
            self.hovered_option = None
            for question_options in self.option_rects:
                for option_rect in question_options:
                    if option_rect.collidepoint(event.pos):
                        self.hovered_option = option_rect

    def wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current_line = []
        current_width = 0

        for word in words:
            word_surface = font.render(word + ' ', True, self.BLACK)
            word_width = word_surface.get_width()

            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width

        if current_line:
            lines.append(' '.join(current_line))
        return lines

    def render(self, screen):
        screen.fill(self.WHITE)

        # Update description based on question count
        self.description_text = self.complete_description if self.game_state.get_selected_count(
        ) >= 16 else self.incomplete_description

        # Define background colors based on completion status
        if self.game_state.get_selected_count() >= 16:
            description_bg_color = (220, 255, 220)  # Light green for complete
            description_border_color = (100, 200, 100)  # Darker green border
        else:
            description_bg_color = (255, 220, 220)  # Light red for incomplete
            description_border_color = (200, 100, 100)  # Darker red border

        # Draw description box with the appropriate color
        pygame.draw.rect(screen, description_bg_color,
                         self.description_box, border_radius=10)
        pygame.draw.rect(screen, description_border_color,
                         self.description_box, 2, border_radius=10)

        # Draw description text
        y_offset = self.description_box.y + 10
        for line in self.description_text:
            if line:
                text_surface = self.text_font.render(line, True, self.BLACK)
                text_rect = text_surface.get_rect(
                    centerx=self.screen_width//2, y=y_offset)
                screen.blit(text_surface, text_rect)
            y_offset += 15  # Reduced line spacing

        # Draw question boxes
        self.option_rects = [[], [], []]
        for i, (box, question) in enumerate(zip(self.question_boxes, self.questions)):
            pygame.draw.rect(screen, (240, 240, 250), box, border_radius=10)
            pygame.draw.rect(screen, self.LIGHT_BLUE, box, 2, border_radius=10)

            # Question text
            question_lines = self.wrap_text(
                question['text'], self.text_font, box.width - 20)
            text_y = box.y + 15
            for line in question_lines:
                text_surface = self.text_font.render(line, True, self.BLACK)
                text_rect = text_surface.get_rect(x=box.x + 10, y=text_y)
                screen.blit(text_surface, text_rect)
                text_y += 20

            # Draw options with text wrapping
            text_y += 10  # Space after question
            for j, option in enumerate(question['options']):
                option_lines = self.wrap_text(
                    option, self.option_font, box.width - 40)
                # Height based on number of lines
                option_height = len(option_lines) * 20 + 10

                option_rect = pygame.Rect(
                    box.x + 10,
                    text_y,
                    box.width - 20,
                    option_height
                )
                self.option_rects[i].append(option_rect)

                # Option background
                color = self.HOVER_BLUE if option_rect == self.hovered_option else \
                    self.LIGHT_BLUE if self.selected_answers[i] == j else \
                    self.GRAY
                pygame.draw.rect(screen, color, option_rect, border_radius=5)

                # Option text
                line_y = text_y + 5
                for line in option_lines:
                    line_surface = self.option_font.render(
                        line, True, self.BLACK)
                    line_rect = line_surface.get_rect(
                        x=option_rect.x + 10, y=line_y)
                    screen.blit(line_surface, line_rect)
                    line_y += 20

                text_y += option_height + 10

        # Draw back button
        button_color = self.continue_button_color[
            'hover'] if self.back_button_hover else self.continue_button_color['active']
        pygame.draw.rect(screen, button_color,
                         self.back_button, border_radius=5)
        back_text = self.button_font.render("Back", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=self.back_button.center)
        screen.blit(back_text, back_rect)

       # Draw continue button
        button_color = self.HOVER_BLUE if self.continue_button_hover else \
            self.LIGHT_BLUE if None not in self.selected_answers else \
            self.GRAY
        pygame.draw.rect(screen, button_color,
                         self.continue_button, border_radius=5)
        continue_text = self.button_font.render("Continue", True, self.WHITE)
        text_rect = continue_text.get_rect(center=self.continue_button.center)
        screen.blit(continue_text, text_rect)

        # Add hint if not all questions answered
        if None in self.selected_answers:
            hint_font = pygame.font.Font(None, 22)
            hint_text = hint_font.render(
                "Answer all three decision making questions to continue", True, (100, 100, 100))
            hint_rect = hint_text.get_rect(
                centerx=self.screen_width // 2,
                bottom=self.continue_button.top - 5
            )
            screen.blit(hint_text, hint_rect)

    def calculate_score(self):
        correct_count = sum(1 for i, answer in enumerate(self.selected_answers)
                            if answer == self.questions[i]['correct'])

        # Set difficulty based on correct answers
        if correct_count == 3:
            self.game_state.set_tetris_difficulty('easy')
        elif correct_count == 2:
            self.game_state.set_tetris_difficulty('medium')
        else:
            self.game_state.set_tetris_difficulty('hard')

        # Switch to tetris scene - it will be created with the appropriate difficulty
        self.game_state.current_scene = 'tetris'
