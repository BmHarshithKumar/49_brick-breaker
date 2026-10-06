import pygame
from .paddle import Paddle
from .ball import Ball
from .brick import Brick

# Game Engine

WHITE = (255, 255, 255)
BG = (15, 15, 25)

BRICK_COLORS = [
    (200, 60, 60),
    (200, 140, 60),
    (200, 200, 60),
    (80, 180, 80),
    (80, 140, 200),
]


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.rows, self.cols = 5, 8

        self.font = pygame.font.SysFont("Arial", 28)
        self.end_font = pygame.font.SysFont("Arial", 56, bold=True)
        self.score_font = pygame.font.SysFont("Arial", 32)
        self.instruction_font = pygame.font.SysFont("Arial", 24)

        self.difficulty_font = pygame.font.SysFont(
            "Arial", 30, bold=True
        )

        self.difficulty = "Medium"

        self.game_over = False
        self.result = None
        self.replay_menu = False

        self._game_over_logged = False

        self._start_game()

    def _start_game(self):
        """Create/reset all gameplay objects for a new game."""

        # Difficulty settings
        if self.difficulty == "Easy":
            paddle_width = 120
            ball_speed = 3

        elif self.difficulty == "Hard":
            paddle_width = 80
            ball_speed = 6

        else:
            # Medium
            paddle_width = 100
            ball_speed = 4

        self.paddle = Paddle(
            self.width // 2 - paddle_width // 2,
            self.height - 30,
            paddle_width,
            14,
        )

        self.ball = Ball(
            self.width // 2,
            self.height - 50,
            radius=8,
        )

        self.ball.vx = ball_speed
        self.ball.vy = -ball_speed

        self.bricks = self._build_bricks(
            self.rows,
            self.cols,
        )

        self.lives = 3
        self.score = 0

        self.game_over = False
        self.result = None
        self.replay_menu = False
        self._game_over_logged = False

    def _build_bricks(self, rows, cols):
        bricks = []
        margin, gap, top = 30, 6, 60

        brick_w = (
            self.width
            - margin * 2
            - gap * (cols - 1)
        ) // cols

        brick_h = 22

        for r in range(rows):
            for c in range(cols):
                x = margin + c * (brick_w + gap)
                y = top + r * (brick_h + gap)

                bricks.append(
                    Brick(
                        x,
                        y,
                        brick_w,
                        brick_h,
                    )
                )

        return bricks

    def handle_event(self, event):
        # Task 3: Handle the replay/difficulty menu
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.difficulty = "Easy"
                    self._start_game()

                elif event.key == pygame.K_2:
                    self.difficulty = "Medium"
                    self._start_game()

                elif event.key == pygame.K_3:
                    self.difficulty = "Hard"
                    self._start_game()

                elif event.key in (
                    pygame.K_q,
                    pygame.K_ESCAPE,
                ):
                    pygame.quit()
                    raise SystemExit

            return

        # Normal gameplay event handling.
        # Continuous paddle movement is handled in handle_input().
        pass

    def handle_input(self):
        if self.game_over:
            return

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.paddle.move(
                -self.paddle.speed,
                self.width,
            )

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.paddle.move(
                self.paddle.speed,
                self.width,
            )

    def update(self):
        if self.game_over:
            return

        # Store the ball position before moving it.
        # This allows us to determine which side of a rectangle
        # the ball came from.
        previous_rect = self.ball.rect()

        self.ball.move()

        current_rect = self.ball.rect()

        # Wall collision
        if (
            self.ball.x - self.ball.radius <= 0
            or self.ball.x + self.ball.radius >= self.width
        ):
            self.ball.vx *= -1

        if self.ball.y - self.ball.radius <= 0:
            self.ball.vy *= -1

        # Paddle collision
        if current_rect.colliderect(
            self.paddle.rect()
        ):
            paddle_rect = self.paddle.rect()

            # Ball came from above the paddle
            if previous_rect.bottom <= paddle_rect.top:
                self.ball.vy = -abs(self.ball.vy)

            # Ball came from below the paddle
            elif previous_rect.top >= paddle_rect.bottom:
                self.ball.vy = abs(self.ball.vy)

            # Ball came from the left side of the paddle
            elif previous_rect.right <= paddle_rect.left:
                self.ball.vx = -abs(self.ball.vx)

            # Ball came from the right side of the paddle
            elif previous_rect.left >= paddle_rect.right:
                self.ball.vx = abs(self.ball.vx)

        # Brick collision
        for brick in self.bricks:
            if (
                brick.alive
                and current_rect.colliderect(
                    brick.rect()
                )
            ):
                brick.alive = False
                self.score += 1

                brick_rect = brick.rect()

                # Ball came from above the brick
                if previous_rect.bottom <= brick_rect.top:
                    self.ball.vy = -abs(self.ball.vy)

                # Ball came from below the brick
                elif previous_rect.top >= brick_rect.bottom:
                    self.ball.vy = abs(self.ball.vy)

                # Ball came from the left side of the brick
                elif previous_rect.right <= brick_rect.left:
                    self.ball.vx = -abs(self.ball.vx)

                # Ball came from the right side of the brick
                elif previous_rect.left >= brick_rect.right:
                    self.ball.vx = abs(self.ball.vx)

                break

        # Ball fell below the screen
        if (
            self.ball.y - self.ball.radius
            > self.height
        ):
            self.lives -= 1

            if self.lives <= 0:
                self.game_over = True
                self.result = "lose"
                self.replay_menu = True
            else:
                self._reset_ball()

        # Win condition
        if all(
            not b.alive
            for b in self.bricks
        ):
            self.game_over = True
            self.result = "win"
            self.replay_menu = True

    def _reset_ball(self):
        self.ball.x = self.width // 2
        self.ball.y = self.height - 50

        if self.difficulty == "Easy":
            speed = 3
        elif self.difficulty == "Hard":
            speed = 6
        else:
            speed = 4

        self.ball.vx = speed
        self.ball.vy = -speed

    def render(self, screen):
        screen.fill(BG)

        # Normal game objects
        pygame.draw.rect(
            screen,
            WHITE,
            self.paddle.rect(),
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (
                int(self.ball.x),
                int(self.ball.y),
            ),
            self.ball.radius,
        )

        for i, brick in enumerate(self.bricks):
            if brick.alive:
                row = i // self.cols

                color = BRICK_COLORS[
                    row % len(BRICK_COLORS)
                ]

                pygame.draw.rect(
                    screen,
                    color,
                    brick.rect(),
                )

        # Score
        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            WHITE,
        )

        screen.blit(
            score_text,
            (10, 10),
        )

        # Lives
        lives_text = self.font.render(
            f"Lives: {self.lives}",
            True,
            WHITE,
        )

        screen.blit(
            lives_text,
            (
                self.width - 130,
                10,
            ),
        )

        # Task 2 + Task 3 end screen
        if self.game_over:
            self._render_end_screen(screen)

    def _render_end_screen(self, screen):
        # Dark overlay
        overlay = pygame.Surface(
            (
                self.width,
                self.height,
            ),
            pygame.SRCALPHA,
        )

        overlay.fill(
            (
                0,
                0,
                0,
                190,
            )
        )

        screen.blit(
            overlay,
            (0, 0),
        )

        # Result
        if self.result == "win":
            result_text = self.end_font.render(
                "YOU WIN!",
                True,
                WHITE,
            )
        else:
            result_text = self.end_font.render(
                "GAME OVER",
                True,
                WHITE,
            )

        result_rect = result_text.get_rect(
            center=(
                self.width // 2,
                100,
            )
        )

        screen.blit(
            result_text,
            result_rect,
        )

        # Final score
        final_score_text = self.score_font.render(
            f"Final Score: {self.score}",
            True,
            WHITE,
        )

        final_score_rect = (
            final_score_text.get_rect(
                center=(
                    self.width // 2,
                    160,
                )
            )
        )

        screen.blit(
            final_score_text,
            final_score_rect,
        )

        # Replay heading
        replay_text = self.difficulty_font.render(
            "PLAY AGAIN?",
            True,
            WHITE,
        )

        replay_rect = replay_text.get_rect(
            center=(
                self.width // 2,
                230,
            )
        )

        screen.blit(
            replay_text,
            replay_rect,
        )

        # Difficulty options
        easy_text = self.instruction_font.render(
            "1 - Easy",
            True,
            WHITE,
        )

        medium_text = self.instruction_font.render(
            "2 - Medium",
            True,
            WHITE,
        )

        hard_text = self.instruction_font.render(
            "3 - Hard",
            True,
            WHITE,
        )

        quit_text = self.instruction_font.render(
            "Q - Quit",
            True,
            WHITE,
        )

        options = [
            (easy_text, 290),
            (medium_text, 330),
            (hard_text, 370),
            (quit_text, 410),
        ]

        for text, y in options:
            rect = text.get_rect(
                center=(
                    self.width // 2,
                    y,
                )
            )

            screen.blit(
                text,
                rect,
            )