import pygame
import sys
from scenes.act1_storyline import StorylineScene
from scenes.act2_characters import CharactersScene
from scenes.act3_multipleChoice import DecisionDescriptionScene
from scenes.avatar_profile import AvatarProfile
from TetrisGame.tetris_game import TetrisScene
from scenes.final_scene import FinalScene
from scenes.game_purpose import GamePurposeScene


class GameState:
    def __init__(self):
        self.current_scene = 'act1_storyline'
        self.selected_avatar = None
        self.multiple_choice_score = 0
        self.tetris_difficulty = 'easy'  # Default Tetris difficulty

        # Question tracking
        # Format: {(avatar_id, question_id): True}
        self.selected_questions = {}
        self.max_questions = 16
        self.total_questions = 24

        # Initialize scenes dictionary
        self.scenes = {}

    def can_select_more_questions(self):
        return len(self.selected_questions) < self.max_questions

    def is_question_selected(self, avatar_id, question_id):
        return (avatar_id, question_id) in self.selected_questions

    def select_question(self, avatar_id, question_id):
        if self.can_select_more_questions():
            self.selected_questions[(avatar_id, question_id)] = True
            return True
        return False

    def deselect_question(self, avatar_id, question_id):
        if (avatar_id, question_id) in self.selected_questions:
            del self.selected_questions[(avatar_id, question_id)]
            return True
        return False

    def get_selected_count(self):
        return len(self.selected_questions)

    def set_tetris_difficulty(self, difficulty):
        """Set the Tetris difficulty level"""
        self.tetris_difficulty = difficulty


class SceneManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((900, 700))
        pygame.display.set_caption("Game Project")

        self.game_state = GameState()

        # Initialize scenes and store them in both scene manager and game state
        self.scenes = {
            'act1_storyline': StorylineScene(self.game_state),
            'act2_characters': CharactersScene(self.game_state),
            'act3_multipleChoice': DecisionDescriptionScene(self.game_state),
            'avatar_profile': AvatarProfile(self.game_state)
        }

        # Store scenes in game_state as well
        self.game_state.scenes = self.scenes

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            # Create Tetris scene on demand with the correct difficulty
            if self.game_state.current_scene == 'tetris' and 'tetris' not in self.scenes:
                self.scenes['tetris'] = TetrisScene(
                    self.game_state,
                    difficulty=self.game_state.tetris_difficulty
                )
                # Update scenes in game state
                self.game_state.scenes = self.scenes

            # Create Final scene on demand
            if self.game_state.current_scene == 'final_scene' and 'final_scene' not in self.scenes:
                self.scenes['final_scene'] = FinalScene(self.game_state)
                # Update scenes in game state
                self.game_state.scenes = self.scenes

            # Create GamePurpose scene on demand
            if self.game_state.current_scene == 'game_purpose' and 'game_purpose' not in self.scenes:
                self.scenes['game_purpose'] = GamePurposeScene(self.game_state)
                # Update scenes in game state
                self.game_state.scenes = self.scenes

            current_scene = self.scenes[self.game_state.current_scene]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                current_scene.handle_events(event)

            if hasattr(current_scene, 'update'):
                current_scene.update()

            current_scene.render(self.screen)
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()


def main():
    game = SceneManager()
    game.run()


if __name__ == "__main__":
    main()
