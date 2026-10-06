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

        self.paddle = Paddle(width // 2 - 50, height - 30, 100, 14)

        self.ball = Ball(width // 2, height - 50, radius=8)
        self.ball.vx, self.ball.vy = 4, -4

        self.rows, self.cols = 5, 8
        self.bricks = self._build_bricks(self.rows, self.cols)

        self.lives = 3
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 28)

        self.game_over = False
        self.result = None  # "win" or "lose"

    def _build_bricks(self, rows, cols):
        bricks = []
        margin, gap, top = 30, 6, 60

        brick_w = (self.width - margin * 2 - gap * (cols - 1)) // cols
        brick_h = 22

        for r in range(rows):
            for c in range(cols):
                x = margin + c * (brick_w + gap)
                y = top + r * (brick_h + gap)
                bricks.append(Brick(x, y, brick_w, brick_h))

        return bricks

    def handle_event(self, event):
        # This game only needs continuously-held-key input for the
        # paddle, handled in handle_input each frame.
        pass

    def handle_input(self):
        if self.game_over:
            return

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.paddle.move(-self.paddle.speed, self.width)

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.paddle.move(self.paddle.speed, self.width)

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
        if current_rect.colliderect(self.paddle.rect()):
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
            if brick.alive and current_rect.colliderect(brick.rect()):
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
        if self.ball.y - self.ball.radius > self.height:
            self.lives -= 1

            if self.lives <= 0:
                self.game_over = True
                self.result = "lose"
            else:
                self._reset_ball()

        # Win condition
        if all(not b.alive for b in self.bricks):
            self.game_over = True
            self.result = "win"

    def _reset_ball(self):
        self.ball.x, self.ball.y = self.width // 2, self.height - 50
        self.ball.vx, self.ball.vy = 4, -4

    def render(self, screen):
        screen.fill(BG)

        pygame.draw.rect(screen, WHITE, self.paddle.rect())

        pygame.draw.circle(
            screen,
            WHITE,
            (int(self.ball.x), int(self.ball.y)),
            self.ball.radius,
        )

        for i, brick in enumerate(self.bricks):
            if brick.alive:
                row = i // self.cols
                color = BRICK_COLORS[row % len(BRICK_COLORS)]
                pygame.draw.rect(screen, color, brick.rect())

        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            WHITE,
        )
        screen.blit(score_text, (10, 10))

        lives_text = self.font.render(
            f"Lives: {self.lives}",
            True,
            WHITE,
        )
        screen.blit(
            lives_text,
            (self.width - 130, 10),
        )

        if self.game_over and not getattr(
            self,
            "_game_over_logged",
            False,
        ):
            # NOTE: no proper end screen yet - see Task 2 in the README.
            if self.result == "win":
                print("You win! Final score:", self.score)
            else:
                print("Game over! Final score:", self.score)

            self._game_over_logged = True