import os
import sys
import pygame
import json
from scenes.avatar_profile import AvatarProfile


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temporary folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Load avatars_data.json


def load_avatar_data():
    try:
        json_path = resource_path("scenes/avatars_data.json")
        # print(f"Attempting to load JSON from: {json_path}")
        # print(f"File exists: {os.path.exists(json_path)}")

        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                data = json.load(f)
                # Print first 2 items for debugging
                # print(f"JSON loaded successfully: {data[:2]}")
                return data
        else:
            # print(f"JSON file not found at path: {json_path}")
            # Get the current directory contents for debugging
            print(f"Current directory: {os.getcwd()}")
            print(f"Files in current directory: {os.listdir('.')}")
            try:
                print(
                    f"Files in scenes directory: {os.listdir(resource_path('scenes'))}")
            except:
                print("Could not list scenes directory")
            return None
    except Exception as e:
        print(f"Error loading JSON: {e}")
        import traceback
        traceback.print_exc()
        return None


# Try to load avatar data
avatar_data = load_avatar_data()


class CharactersScene:
    def __init__(self, game_state):
        self.game_state = game_state
        self.screen_width = 900
        self.screen_height = 700
        self.background_color = (255, 255, 255)

        # Add counter position and font
        self.counter_font = pygame.font.Font(None, 28)
        self.counter_y = 20

        # Back button
        self.back_button = pygame.Rect(50, self.screen_height - 80, 100, 35)
        self.back_button_hover = False

        # Continue button
        self.continue_button = pygame.Rect(
            self.screen_width - 150, self.screen_height - 80, 100, 35)

        self.continue_button_color = {
            'active': (100, 200, 255),
            'hover': (150, 220, 255)
        }
        self.continue_button_hover = False
        self.button_font = pygame.font.Font(None, 28)

        # Define hardcoded data - ALWAYS use this as a base
        self.avatar_data = [
            {"id": "Jenna", "name": "Jenna", "role": "Mayor",
             "image": resource_path("scenes/avatars/Jenna.webp")},
            {"id": "George", "name": "George", "role": "School Principal",
             "image": resource_path("scenes/avatars/George.webp")},
            {"id": "Jamal", "name": "Jamal", "role": "Factory Owner",
             "image": resource_path("scenes/avatars/Jamal.webp")},
            {"id": "Maria", "name": "Maria", "role": "Community Leader",
             "image": resource_path("scenes/avatars/Maria.webp")},
            {"id": "Dorian", "name": "Dorian", "role": "Parent",
             "image": resource_path("scenes/avatars/Dorian.webp")},
            {"id": "Claire", "name": "Claire", "role": "Restaurant Owner",
             "image": resource_path("scenes/avatars/Claire.webp")},
            {"id": "Liam", "name": "Liam", "role": "Police Officer",
             "image": resource_path("scenes/avatars/Liam.webp")},
            {"id": "Owen", "name": "Owen", "role": "Farmer",
             "image": resource_path("scenes/avatars/Owen.webp")}
        ]

        # Try to use loaded data if it has the right format
        if avatar_data and isinstance(avatar_data, list) and len(avatar_data) > 0:
            # Check if the first item has the required keys
            if all(key in avatar_data[0] for key in ["id", "name", "role"]):
                # print("Using loaded avatar data")
                # We still need to ensure the image paths are correct
                for avatar in avatar_data:
                    if "image" not in avatar:
                        # Add the image path based on id
                        avatar["image"] = resource_path(
                            f"scenes/avatars/{avatar['id']}.webp")

                self.avatar_data = avatar_data
            else:
                print("Loaded avatar data missing required keys, using default")

        # Load avatar images
        self.avatars = []
        for avatar in self.avatar_data:
            try:
                # Make sure avatar has image key
                if "image" not in avatar:
                    avatar["image"] = resource_path(
                        f"scenes/avatars/{avatar['id']}.webp")

                # Load and scale image
                image = pygame.image.load(avatar["image"])
                image = pygame.transform.scale(image, (150, 150))
                self.avatars.append(image)
            except pygame.error as e:
                print(
                    f"Error loading avatar image for {avatar.get('id', 'unknown')}: {e}")
                print(
                    f"Path attempted: {avatar.get('image', 'No image path')}")
                # Create a placeholder image
                placeholder = pygame.Surface((150, 150))
                placeholder.fill((200, 200, 200))
                self.avatars.append(placeholder)

        # Define positions for each avatar
        self.avatar_positions = [
            (50, 100), (275, 100), (500, 100), (725, 100),
            (50, 340), (275, 340), (500, 340), (725, 340)
        ]

        self.hovered_avatar = None

    def handle_character_click(self, character_index):
        # print(f"Clicked character {character_index}")  # Debug print

        # Store the selected avatar data
        self.game_state.selected_avatar = {
            "index": character_index,
            "data": self.avatar_data[character_index],
            "image": self.avatars[character_index]
        }

        # Get the profile scene and initialize it
        profile_scene = self.game_state.scenes['avatar_profile']
        profile_scene.initialize_questions()

        # Change to avatar profile scene
        self.game_state.current_scene = 'avatar_profile'

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = event.pos

                # Check for back button click
                if self.back_button.collidepoint(mouse_pos):
                    self.game_state.current_scene = 'act1_storyline'
                    return

                # Check for clicks on each avatar
                for idx, pos in enumerate(self.avatar_positions):
                    rect = pygame.Rect(pos, (150, 150))
                    if rect.collidepoint(mouse_pos):
                        self.handle_character_click(idx)
                        return

                # Check for continue button click
                if self.continue_button.collidepoint(mouse_pos):
                    self.game_state.current_scene = 'act3_multipleChoice'
                    return

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos

            # Update button hover states
            self.back_button_hover = self.back_button.collidepoint(mouse_pos)
            self.continue_button_hover = self.continue_button.collidepoint(
                mouse_pos)

            # Update avatar hover state
            self.hovered_avatar = None
            for idx, pos in enumerate(self.avatar_positions):
                rect = pygame.Rect(pos, (150, 150))
                if rect.collidepoint(mouse_pos):
                    self.hovered_avatar = idx
                    break

    def render(self, screen):
        screen.fill(self.background_color)

        # Draw question counter at the top
        remaining_questions = 16 - self.game_state.get_selected_count()
        counter_text = self.counter_font.render(
            f"{remaining_questions} Questions Remaining", True, (0, 0, 0))
        counter_rect = counter_text.get_rect(
            centerx=self.screen_width // 2,
            y=self.counter_y
        )
        # Draw a background for the counter
        pygame.draw.rect(screen, (240, 240, 240),
                         counter_rect.inflate(20, 10),
                         border_radius=5)
        screen.blit(counter_text, counter_rect)

        # Draw avatar images with hover effect
        for idx, (avatar, pos) in enumerate(zip(self.avatars, self.avatar_positions)):
            if avatar:
                # Create a surface for the avatar with padding for hover effect
                avatar_surface = pygame.Surface((160, 160), pygame.SRCALPHA)

                # Draw hover effect if this avatar is being hovered over
                if self.hovered_avatar == idx:
                    pygame.draw.rect(avatar_surface, (100, 200, 255, 100),
                                     avatar_surface.get_rect(), border_radius=10)

                # Draw avatar image with a small offset to center it
                avatar_surface.blit(avatar, (5, 5))
                screen.blit(avatar_surface, (pos[0] - 5, pos[1] - 5))

                # Draw name under avatar
                font = pygame.font.Font(None, 24)
                name_text = font.render(
                    self.avatar_data[idx]["name"], True, (0, 0, 0))
                name_rect = name_text.get_rect(
                    centerx=pos[0] + 75, top=pos[1] + 155)
                screen.blit(name_text, name_rect)

                role_font = pygame.font.Font(None, 20)
                role_text = role_font.render(
                    self.avatar_data[idx]["role"], True, (100, 100, 100))
                role_rect = role_text.get_rect(
                    centerx=pos[0] + 75,
                    top=name_rect.bottom + 2
                )
                screen.blit(role_text, role_rect)

        # Draw back button
        button_color = self.continue_button_color[
            'hover'] if self.back_button_hover else self.continue_button_color['active']
        pygame.draw.rect(screen, button_color,
                         self.back_button, border_radius=5)
        back_text = self.button_font.render("Back", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=self.back_button.center)
        screen.blit(back_text, back_rect)

        # Draw continue button
        button_color = self.continue_button_color[
            'hover'] if self.continue_button_hover else self.continue_button_color['active']
        pygame.draw.rect(screen, button_color,
                         self.continue_button, border_radius=5)

        # Draw button text
        pygame.draw.rect(screen, button_color,
                         self.continue_button, border_radius=5)
        continue_text = self.button_font.render(
            "Continue", True, (255, 255, 255))
        text_rect = continue_text.get_rect(center=self.continue_button.center)
        screen.blit(continue_text, text_rect)

       # Draw hint and description texts (always visible)
        desc_font = pygame.font.Font(None, 24)
        hint_font = pygame.font.Font(None, 24)

        # Hint text changes based on selection count (rendered first, at the bottom position)
        hint_message = "Select characters to interview" if self.game_state.get_selected_count(
        ) < 16 else "All questions selected"
        hint_text = hint_font.render(hint_message, True, (100, 100, 100))
        hint_rect = hint_text.get_rect(
            centerx=self.screen_width // 2,
            bottom=self.continue_button.top - 10  # Now at the bottom position
        )
        screen.blit(hint_text, hint_rect)

        # Description text now above hint (rendered second, at the top position)
        desc_text = desc_font.render(
            "You can select up to 16 questions", True, (100, 100, 100))
        desc_rect = desc_text.get_rect(
            centerx=self.screen_width // 2,
            bottom=hint_rect.top - 5  # Position above the hint text with spacing
        )
        screen.blit(desc_text, desc_rect)
