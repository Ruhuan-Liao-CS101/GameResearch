import os
import sys
import pygame
import json


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temporary folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class ScrollBox:
    def __init__(self, rect, text, font, background_color=(255, 255, 255), text_color=(0, 0, 0)):
        self.rect = rect
        self.text = text
        self.font = font
        self.background_color = background_color
        self.text_color = text_color
        self.scroll_y = 0
        self.scroll_speed = 20
        self.padding = 10

        # Create lines of text that fit within the box width
        self.lines = self.wrap_text(text, font, rect.width - 2 * self.padding)

        # Calculate the total height of the text
        self.total_height = len(self.lines) * font.get_linesize()

        # Create the surface for drawing
        self.surface = pygame.Surface((rect.width, rect.height))

    def wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current_line = []
        current_width = 0

        for word in words:
            word_surface = font.render(word + ' ', True, self.text_color)
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

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if event.button == 4:  # Mouse wheel up
                self.scroll_y = min(0, self.scroll_y + self.scroll_speed)
            elif event.button == 5:  # Mouse wheel down
                max_scroll = min(0, self.rect.height -
                                 self.total_height - 2 * self.padding)
                self.scroll_y = max(
                    max_scroll, self.scroll_y - self.scroll_speed)

    def draw(self, screen):
        # Draw background
        self.surface.fill(self.background_color)

        # Draw text with scroll offset
        y = self.padding + self.scroll_y
        for line in self.lines:
            text_surface = self.font.render(line, True, self.text_color)
            self.surface.blit(text_surface, (self.padding, y))
            y += self.font.get_linesize()

        # Draw the surface to the screen
        screen.blit(self.surface, self.rect)

        # Draw border
        pygame.draw.rect(screen, (200, 200, 200),
                         self.rect, 1, border_radius=5)


class AvatarProfile:
    def __init__(self, game_state):
        self.game_state = game_state
        self.screen_width = 800
        self.screen_height = 600
        self.background_color = (240, 240, 240)

        # Load avatar questions data with error handling
        self.avatars_data = self.load_avatars_data()

        # Layout settings
        self.avatar_area = {
            "x": 50,
            "y": 50,
            "width": 250,
            "height": 400
        }

        self.questions_area = {
            "x": 320,
            "y": 50,
            "width": 430,
            "height": 500
        }

        # Fixed heights for boxes
        self.question_height = 80
        self.answer_height = 120
        self.button_padding = 30

        # UI Elements
        self.back_button = pygame.Rect(50, 500, 150, 50)
        self.back_button_color = (100, 200, 255)
        self.back_button_hover = False

        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.text_font = pygame.font.Font(None, 32)
        self.question_font = pygame.font.Font(None, 24)

        # Store scroll boxes
        self.answer_boxes = {}

        # Scroll position for questions area
        self.questions_scroll_y = 0
        self.questions_max_scroll = 0

        # Fallback avatar data based on your shared JSON
        self.fallback_avatar_data = [
            {
                "id": "Jenna",
                "name": "Mayor Jenna",
                "role": "Mayor",
                "description": "Focused on revitalizing the local economy and government services.",
                "questions": [
                    {
                        "question": "Given our limited budget, what would you prioritize for immediate repair?",
                        "answer": "Our top priority should be to clear the main roads as soon as possible. These routes are essential for getting emergency supplies and aid workers into the town and for allowing residents to access essential services. Additionally, restoring power to emergency centers is critical for medical and communication needs."
                    },
                    {
                        "question": "With the risk of future storms, what's a top resilience investment?",
                        "answer": "Investing in flood barriers around key infrastructure and strengthening the town's power grid by reinforcing poles, upgrading transformers, and installing backup generators."
                    },
                    {
                        "question": "Have you attended any recent conferences?",
                        "answer": "Yes, I attended an urban planning conference last month, focusing on disaster response, resilience strategies, and eco-friendly infrastructure."
                    }
                ]
            },
            {
                "id": "George",
                "name": "George",
                "role": "School Principal",
                "description": "Committed to reopening schools and ensuring safe access to education for children.",
                "questions": [
                    {
                        "question": "What should we prioritize to get students back in school quickly?",
                        "answer": "Repairing water damage in classrooms and clearing main roads to enable bus routes to resume safely."
                    },
                    {
                        "question": "What long-term improvements should we consider for school safety?",
                        "answer": "Reinforcing school buildings with stronger materials and creating an emergency supply room stocked with essentials."
                    },
                    {
                        "question": "What's your favorite book genre?",
                        "answer": "Historical fiction, as it inspires resilience and provides perspective through stories from the past."
                    }
                ]
            },
            {
                "id": "Jamal",
                "name": "Jamal",
                "role": "Factory Owner",
                "description": "Advocates for restoring power and transportation to revive the industrial sector.",
                "questions": [
                    {
                        "question": "What's the first thing we should fix to get the factory back up and running?",
                        "answer": "Restoring power to the factory is the most urgent need, followed by clearing debris and ensuring supply chain routes are accessible."
                    },
                    {
                        "question": "How can we prevent future disruptions to the factory from future storms?",
                        "answer": "Reinforcing the building's structure, investing in backup generators, and creating a flood barrier around the factory."
                    },
                    {
                        "question": "Are there plans for expanding the factory soon?",
                        "answer": "Not currently; the focus is on rebuilding and restoring what we already have before considering expansion."
                    }
                ]
            },
            {
                "id": "Maria",
                "name": "Maria",
                "role": "Community Leader",
                "description": "Prioritizes healthcare and shelter for the elderly and vulnerable populations.",
                "questions": [
                    {
                        "question": "How can we support elderly and vulnerable community members in need?",
                        "answer": "Restoring power to senior housing, ensuring functional heating and cooling systems, and providing backup generators for critical care facilities."
                    },
                    {
                        "question": "How can we address the needs of other vulnerable populations, such as the disabled or low-income families?",
                        "answer": "Prioritizing accessible shelters for people with disabilities and providing financial aid or food assistance to low-income families."
                    },
                    {
                        "question": "Have you considered hosting a town-wide event to lift people's spirits during the recovery?",
                        "answer": "Yes, hosting a concert or fair could strengthen morale once the situation stabilizes."
                    }
                ]
            },
            {
                "id": "Dorian",
                "name": "Dorian Parker",
                "role": "Parent",
                "description": "Concentrated on family safety and restoring housing, schools, and community centers.",
                "questions": [
                    {
                        "question": "What is your biggest concern as a parent during the recovery?",
                        "answer": "Ensuring a safe place for children to live, access to care, and support for their mental and emotional well-being."
                    },
                    {
                        "question": "How can we make the community safe for families?",
                        "answer": "Restoring essential services, rebuilding safe housing, clearing public spaces, and providing mental health support."
                    },
                    {
                        "question": "How do you usually spend your weekends?",
                        "answer": "Hiking with my kids, but currently focusing on recovery efforts and finding a safe place to live."
                    }
                ]
            },
            {
                "id": "Claire",
                "name": "Claire",
                "role": "Restaurant Owner",
                "description": "Stressed by business closures and seeks quick reopening of small businesses and restoration of clean water and food distribution.",
                "questions": [
                    {
                        "question": "What infrastructure is needed for restaurants to reopen?",
                        "answer": "Restoring power and water supply, clearing debris, and fixing structural damage to ensure safety."
                    },
                    {
                        "question": "What can we do to help ensure there's a steady food supply for the community during recovery?",
                        "answer": "Restoring supply chain routes and establishing temporary food distribution points."
                    },
                    {
                        "question": "Have you thought about offering a new special on your menu to attract customers once you reopen?",
                        "answer": "Yes, but only after ensuring the restaurant is operational and community needs are met."
                    }
                ]
            },
            {
                "id": "Liam",
                "name": "Liam Moore",
                "role": "Police Officer",
                "description": "Focused on public safety, law enforcement, and restoring roads and communication for emergency services.",
                "questions": [
                    {
                        "question": "What should we prioritize to ensure public safety as we begin the recovery?",
                        "answer": "Restoring roads and communication networks, securing essential infrastructure, and patrolling neighborhoods to prevent looting."
                    },
                    {
                        "question": "What additional support do you need to maintain security and assist with recovery efforts?",
                        "answer": "More manpower, resources, cleared debris, and coordination with national agencies."
                    },
                    {
                        "question": "Do you have any favorite hobbies outside of work?",
                        "answer": "Reading mystery novels and watching detective shows, though the focus is currently on recovery efforts."
                    }
                ]
            },
            {
                "id": "Owen",
                "name": "Owen Harper",
                "role": "Farmer",
                "description": "Advocates for repairing rural infrastructure to restore agricultural production and ensure food security.",
                "questions": [
                    {
                        "question": "What is the most urgent need for the agricultural community?",
                        "answer": "Restoring access to water and repairing irrigation systems, along with clearing roads for supplies and transportation."
                    },
                    {
                        "question": "What long-term improvements should we consider for agricultural resilience?",
                        "answer": "Investing in flood protection, strengthening irrigation systems, and diversifying crop types."
                    },
                    {
                        "question": "What's your favorite type of animal to raise on the farm?",
                        "answer": "Cows for dairy, though the focus is on crop restoration for now."
                    }
                ]
            }
        ]

    def load_avatars_data(self):
        """Load avatar data with proper resource path handling"""
        try:
            json_path = resource_path("scenes/avatars_data.json")
            # print(f"AvatarProfile: Attempting to load JSON from: {json_path}")
            # print(f"AvatarProfile: File exists: {os.path.exists(json_path)}")

            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    data = json.load(f)
                    # print(f"AvatarProfile: Successfully loaded avatars_data.json")
                    return data
            else:
                # print(
                #     f"AvatarProfile: JSON file not found at path: {json_path}")
                # print(
                #     f"AvatarProfile: Directory contents: {os.listdir(os.path.dirname(json_path)) if os.path.exists(os.path.dirname(json_path)) else 'directory not found'}")
                # print(f"AvatarProfile: Using fallback avatar data")
                return self.fallback_avatar_data
        except Exception as e:
            # print(f"AvatarProfile: Error loading avatars data: {e}")
            import traceback
            traceback.print_exc()
            # print(f"AvatarProfile: Using fallback avatar data")
            return self.fallback_avatar_data

    def wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current_line = []
        current_width = 0

        for word in words:
            word_surface = font.render(word + ' ', True, (0, 0, 0))
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

    def initialize_questions(self):
        """Initialize question buttons for the selected avatar"""
        self.question_buttons = []
        self.answer_boxes.clear()

        if not hasattr(self.game_state, 'selected_avatar') or self.game_state.selected_avatar is None:
            return

        avatar_id = self.game_state.selected_avatar['data']['id']
        avatar_data = next(
            (a for a in self.avatars_data if a['id'] == avatar_id), None)

        if avatar_data and 'questions' in avatar_data:
            y_pos = self.questions_area["y"]

            for i, qa in enumerate(avatar_data['questions']):
                # Wrap question text
                question_lines = self.wrap_text(qa['question'], self.question_font,
                                                self.questions_area["width"] - 20)

                total_height = self.question_height
                if hasattr(self.game_state, 'is_question_selected') and \
                   self.game_state.is_question_selected(avatar_id, i):
                    total_height += self.answer_height + 10

                button = {
                    "rect": pygame.Rect(
                        self.questions_area["x"],
                        y_pos,
                        self.questions_area["width"],
                        total_height
                    ),
                    "question": qa['question'],
                    "question_lines": question_lines,
                    "answer": qa['answer'],
                    "id": i,
                    "showing_answer": hasattr(self.game_state, 'is_question_selected') and
                    self.game_state.is_question_selected(avatar_id, i)
                }

                # Create scroll box for answer if selected
                if button["showing_answer"]:
                    answer_rect = pygame.Rect(
                        self.questions_area["x"],
                        y_pos + self.question_height + 10,
                        self.questions_area["width"],
                        self.answer_height
                    )
                    self.answer_boxes[i] = ScrollBox(
                        answer_rect,
                        qa['answer'],
                        self.question_font,
                        background_color=(255, 255, 255)
                    )

                self.question_buttons.append(button)
                y_pos += total_height + self.button_padding

            # Calculate max scroll based on total content height
            total_content_height = y_pos - self.questions_area["y"]
            self.questions_max_scroll = max(
                0, total_content_height - self.questions_area["height"])
        else:
            print(f"AvatarProfile: No questions found for avatar {avatar_id}")
            # If no questions found in avatar_data, use default questions
            default_questions = [
                {"question": "What's your perspective on sustainability?",
                 "answer": "I believe sustainability is about finding balance between our current needs and ensuring future generations can thrive."},
                {"question": "How would these changes affect your daily life?",
                 "answer": "I would need to adjust some of my habits and possibly face some short-term inconveniences, but I think the long-term benefits would be worth it."},
                {"question": "What role do you think technology should play?",
                 "answer": "Technology can provide innovative solutions, but we need to be thoughtful about implementation and ensure access is equitable."},
                {"question": "What sacrifices would you be willing to make?",
                 "answer": "I'm willing to adapt my lifestyle in reasonable ways if I understand how my actions contribute to meaningful positive change."}
            ]

            y_pos = self.questions_area["y"]
            for i, qa in enumerate(default_questions):
                # Wrap question text
                question_lines = self.wrap_text(qa['question'], self.question_font,
                                                self.questions_area["width"] - 20)

                button = {
                    "rect": pygame.Rect(
                        self.questions_area["x"],
                        y_pos,
                        self.questions_area["width"],
                        self.question_height
                    ),
                    "question": qa['question'],
                    "question_lines": question_lines,
                    "answer": qa['answer'],
                    "id": i,
                    "showing_answer": False
                }

                self.question_buttons.append(button)
                y_pos += self.question_height + self.button_padding

            # Calculate max scroll
            total_content_height = y_pos - self.questions_area["y"]
            self.questions_max_scroll = max(
                0, total_content_height - self.questions_area["height"])

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if self.back_button.collidepoint(event.pos):
                    self.game_state.current_scene = 'act2_characters'
                    return

                # Adjust mouse position for scrolling
                adjusted_pos = (
                    event.pos[0], event.pos[1] - self.questions_scroll_y)

                if hasattr(self.game_state, 'selected_avatar') and self.game_state.selected_avatar:
                    avatar_id = self.game_state.selected_avatar['data']['id']
                    for button in self.question_buttons:
                        adjusted_rect = button["rect"].copy()
                        adjusted_rect.y += self.questions_scroll_y
                        if adjusted_rect.collidepoint(event.pos):
                            if not button["showing_answer"]:
                                if hasattr(self.game_state, 'can_select_more_questions') and \
                                   self.game_state.can_select_more_questions():
                                    if self.game_state.select_question(avatar_id, button["id"]):
                                        button["showing_answer"] = True
                                        self.initialize_questions()

            # Handle scrolling for the questions area
            elif event.button == 4:  # Mouse wheel up
                self.questions_scroll_y = min(0, self.questions_scroll_y + 30)
            elif event.button == 5:  # Mouse wheel down
                self.questions_scroll_y = max(-self.questions_max_scroll,
                                              self.questions_scroll_y - 30)

            # Handle scrolling in answer boxes
            for scroll_box in self.answer_boxes.values():
                scroll_box.handle_event(event)

        elif event.type == pygame.MOUSEMOTION:
            self.back_button_hover = self.back_button.collidepoint(event.pos)

    def render(self, screen):
        screen.fill(self.background_color)

        if hasattr(self.game_state, 'selected_avatar') and self.game_state.selected_avatar:
            avatar_data = self.game_state.selected_avatar

            # Draw avatar image
            if avatar_data["image"]:
                screen.blit(avatar_data["image"],
                            (self.avatar_area["x"], self.avatar_area["y"]))

            # Draw avatar name
            name_text = self.title_font.render(
                avatar_data["data"]["name"], True, (0, 0, 0))
            name_rect = name_text.get_rect(
                x=self.avatar_area["x"],
                y=self.avatar_area["y"] + 170
            )
            screen.blit(name_text, name_rect)

            # Get the description from avatars_data using the avatar's ID
            avatar_id = avatar_data["data"]["id"]
            avatar_info = next(
                (a for a in self.avatars_data if a["id"] == avatar_id), None)

            if avatar_info and "description" in avatar_info:
                # Draw description with text wrapping
                description_lines = self.wrap_text(
                    avatar_info["description"],
                    self.question_font,
                    self.avatar_area["width"] - 20
                )

                desc_y = name_rect.bottom + 40
                for line in description_lines:
                    desc_text = self.question_font.render(
                        line, True, (80, 80, 80))
                    desc_rect = desc_text.get_rect(
                        x=self.avatar_area["x"],
                        y=desc_y
                    )
                    screen.blit(desc_text, desc_rect)
                    desc_y += self.question_font.get_linesize()

                desc_y += 30
            else:
                desc_y = name_rect.bottom + 40

            # Draw questions counter
            remaining_questions = 16 - self.game_state.get_selected_count()
            counter_text = self.text_font.render(
                f"Questions Remaining:", True, (0, 0, 0))
            counter_value = self.text_font.render(
                f"{remaining_questions}", True, (0, 0, 0))

            counter_rect = counter_text.get_rect(
                x=self.avatar_area["x"],
                y=desc_y
            )
            counter_value_rect = counter_value.get_rect(
                x=self.avatar_area["x"],
                y=counter_rect.bottom + 5
            )

            screen.blit(counter_text, counter_rect)
            screen.blit(counter_value, counter_value_rect)

            # Create a surface for the questions area
            questions_surface = pygame.Surface(
                (self.questions_area["width"], self.questions_area["height"]))
            questions_surface.fill(self.background_color)

            # Draw question buttons with scroll offset
            for button in self.question_buttons:
                # Question box
                question_rect = pygame.Rect(
                    0,  # Local coordinates for the surface
                    button["rect"].y - self.questions_area["y"] +
                        self.questions_scroll_y,
                    button["rect"].width,
                    self.question_height
                )

                # Only draw if visible in the viewport
                if -self.question_height <= question_rect.y <= self.questions_area["height"]:
                    # Button color
                    button_color = (150, 220, 255) if button["showing_answer"] else \
                        (180, 180, 180) if not self.game_state.can_select_more_questions() else \
                        (200, 200, 200)

                    # Draw question box
                    pygame.draw.rect(questions_surface, button_color,
                                     question_rect, border_radius=5)

                    # Draw wrapped question text
                    y_offset = question_rect.y + 10
                    for line in button["question_lines"]:
                        text_surface = self.question_font.render(
                            line, True, (0, 0, 0))
                        text_rect = text_surface.get_rect(x=10, y=y_offset)
                        questions_surface.blit(text_surface, text_rect)
                        y_offset += self.question_font.get_linesize()

            # Draw the questions surface
            screen.blit(questions_surface,
                        (self.questions_area["x"], self.questions_area["y"]))

            # Draw answer boxes
            for scroll_box in self.answer_boxes.values():
                # Adjust the scroll box position
                original_rect = scroll_box.rect.copy()
                scroll_box.rect.y += self.questions_scroll_y
                if -self.answer_height <= scroll_box.rect.y <= self.screen_height:
                    scroll_box.draw(screen)
                scroll_box.rect = original_rect

        # Draw back button
        button_color = (
            150, 220, 255) if self.back_button_hover else self.back_button_color
        pygame.draw.rect(screen, button_color,
                         self.back_button, border_radius=5)
        back_text = self.text_font.render("Back", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=self.back_button.center)
        screen.blit(back_text, back_rect)
