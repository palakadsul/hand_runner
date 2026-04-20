import pygame
import random

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 220)
YELLOW = (255, 220, 0)
GRAY = (180, 180, 180)
DARK = (30, 30, 30)
ORANGE = (255, 140, 0)

# Game settings
WIDTH, HEIGHT = 480, 640
FPS = 60
LANE_COUNT = 3
LANE_WIDTH = WIDTH // LANE_COUNT

class Player:
    def __init__(self):
        self.lane = 1  # 0=left, 1=center, 2=right
        self.y = HEIGHT - 150
        self.width = 50
        self.height = 70
        self.color = BLUE
        self.is_jumping = False
        self.is_sliding = False
        self.jump_offset = 0
        self.jump_velocity = 0
        self.slide_timer = 0

    def get_x(self):
        return self.lane * LANE_WIDTH + LANE_WIDTH // 2 - self.width // 2

    def move_left(self):
        if self.lane > 0:
            self.lane -= 1

    def move_right(self):
        if self.lane < 2:
            self.lane += 1

    def jump(self):
        if not self.is_jumping and not self.is_sliding:
            self.is_jumping = True
            self.jump_velocity = -18

    def slide(self):
        if not self.is_jumping:
            self.is_sliding = True
            self.slide_timer = 30

    def update(self):
        if self.is_jumping:
            self.jump_offset += self.jump_velocity
            self.jump_velocity += 1
            if self.jump_offset >= 0:
                self.jump_offset = 0
                self.is_jumping = False
                self.jump_velocity = 0

        if self.is_sliding:
            self.slide_timer -= 1
            if self.slide_timer <= 0:
                self.is_sliding = False

    def get_rect(self):
        x = self.get_x()
        y = self.y + self.jump_offset
        if self.is_sliding:
            return pygame.Rect(x, y + self.height // 2,
                               self.width, self.height // 2)
        return pygame.Rect(x, y, self.width, self.height)

    def draw(self, surface):
        x = self.get_x()
        y = self.y + self.jump_offset

        if self.is_sliding:
            # Draw sliding character
            pygame.draw.rect(surface, self.color,
                             (x, y + self.height // 2,
                              self.width, self.height // 2),
                             border_radius=8)
            # Head
            pygame.draw.circle(surface, YELLOW,
                                (x + self.width // 2,
                                 y + self.height // 2 - 10), 12)
        else:
            # Body
            pygame.draw.rect(surface, self.color,
                             (x, y + 20, self.width, self.height - 20),
                             border_radius=8)
            # Head
            pygame.draw.circle(surface, YELLOW,
                                (x + self.width // 2, y + 12), 14)
            # Eyes
            pygame.draw.circle(surface, WHITE,
                                (x + self.width // 2 - 5, y + 10), 4)
            pygame.draw.circle(surface, WHITE,
                                (x + self.width // 2 + 5, y + 10), 4)
            pygame.draw.circle(surface, BLACK,
                                (x + self.width // 2 - 5, y + 10), 2)
            pygame.draw.circle(surface, BLACK,
                                (x + self.width // 2 + 5, y + 10), 2)


class Obstacle:
    def __init__(self, speed):
        self.lane = random.randint(0, 2)
        self.y = -80
        self.width = 50
        self.height = 60
        self.speed = speed
        self.color = RED
        self.type = random.choice(["barrier", "low"])

    def get_x(self):
        return self.lane * LANE_WIDTH + LANE_WIDTH // 2 - self.width // 2

    def update(self):
        self.y += self.speed

    def get_rect(self):
        x = self.get_x()
        if self.type == "low":
            return pygame.Rect(x, self.y + self.height // 2,
                               self.width, self.height // 2)
        return pygame.Rect(x, self.y, self.width, self.height)

    def draw(self, surface):
        x = self.get_x()
        if self.type == "barrier":
            # Tall barrier
            pygame.draw.rect(surface, RED,
                             (x, self.y, self.width, self.height),
                             border_radius=6)
            pygame.draw.rect(surface, ORANGE,
                             (x + 5, self.y + 5,
                              self.width - 10, 10),
                             border_radius=3)
        else:
            # Low obstacle - must slide
            pygame.draw.rect(surface, (180, 0, 0),
                             (x, self.y + self.height // 2,
                              self.width, self.height // 2),
                             border_radius=6)


class Coin:
    def __init__(self, speed):
        self.lane = random.randint(0, 2)
        self.y = -30
        self.radius = 12
        self.speed = speed
        self.collected = False

    def get_x(self):
        return self.lane * LANE_WIDTH + LANE_WIDTH // 2

    def update(self):
        self.y += self.speed

    def get_rect(self):
        return pygame.Rect(self.get_x() - self.radius,
                           self.y - self.radius,
                           self.radius * 2, self.radius * 2)

    def draw(self, surface):
        if not self.collected:
            pygame.draw.circle(surface, YELLOW,
                               (self.get_x(), self.y), self.radius)
            pygame.draw.circle(surface, (200, 170, 0),
                               (self.get_x(), self.y), self.radius, 2)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Hand Runner 🖐️")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 28, bold=True)
        self.big_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 20)
        self.reset()

    def reset(self):
        self.player = Player()
        self.obstacles = []
        self.coins = []
        self.score = 0
        self.coin_count = 0
        self.speed = 5
        self.frame_count = 0
        self.game_over = False
        self.started = False
        self.bg_offset = 0
        self.last_gesture = None
        self.gesture_display_timer = 0

    def apply_gesture(self, gesture):
        if gesture == "LEFT":
            self.player.move_left()
        elif gesture == "RIGHT":
            self.player.move_right()
        elif gesture == "UP":
            self.player.jump()
        elif gesture == "DOWN":
            self.player.slide()

        if gesture:
            self.last_gesture = gesture
            self.gesture_display_timer = 30

    def draw_background(self):
        # Sky
        self.screen.fill((135, 206, 235))

        # Ground
        pygame.draw.rect(self.screen, (101, 67, 33),
                         (0, HEIGHT - 60, WIDTH, 60))

        # Lane lines
        for i in range(1, LANE_COUNT):
            x = i * LANE_WIDTH
            pygame.draw.line(self.screen, (150, 100, 50),
                             (x, HEIGHT - 60), (x, 0), 2)

        # Road surface
        pygame.draw.rect(self.screen, (80, 80, 80),
                         (0, HEIGHT - 80, WIDTH, 80))

        # Dashed lane markers
        for i in range(1, LANE_COUNT):
            x = i * LANE_WIDTH
            for y in range(0, HEIGHT, 40):
                offset = (self.bg_offset * 2) % 40
                pygame.draw.line(self.screen, WHITE,
                                 (x, y - offset),
                                 (x, y - offset + 20), 2)

        self.bg_offset += 1

    def draw_hud(self):
        # Score
        score_text = self.font.render(f"Score: {self.score}",
                                      True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Coins
        coin_text = self.font.render(f"🪙 {self.coin_count}",
                                     True, YELLOW)
        self.screen.blit(coin_text, (10, 45))

        # Speed
        speed_text = self.small_font.render(
            f"Speed: {self.speed:.1f}", True, WHITE)
        self.screen.blit(speed_text, (10, 80))

        # Gesture indicator
        if self.gesture_display_timer > 0:
            colors = {
                "LEFT": (100, 100, 255),
                "RIGHT": (100, 255, 100),
                "UP": (255, 255, 100),
                "DOWN": (255, 100, 100)
            }
            color = colors.get(self.last_gesture, WHITE)
            g_text = self.font.render(
                f"← {self.last_gesture} →"
                if self.last_gesture in ["LEFT", "RIGHT"]
                else f"↑ {self.last_gesture} ↓",
                True, color)
            self.screen.blit(g_text, (WIDTH // 2 - 60, 10))
            self.gesture_display_timer -= 1

    def draw_start_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        title = self.big_font.render("HAND RUNNER", True, YELLOW)
        self.screen.blit(title,
                         (WIDTH // 2 - title.get_width() // 2, 180))

        sub = self.font.render("Control with your hand!", True, WHITE)
        self.screen.blit(sub,
                         (WIDTH // 2 - sub.get_width() // 2, 260))

        controls = [
            "← Move Left",
            "→ Move Right",
            "↑ Jump",
            "↓ Slide"
        ]
        for i, ctrl in enumerate(controls):
            t = self.small_font.render(ctrl, True, GRAY)
            self.screen.blit(t,
                             (WIDTH // 2 - t.get_width() // 2,
                              320 + i * 28))

        start = self.font.render("Show hand to START!", True, GREEN)
        self.screen.blit(start,
                         (WIDTH // 2 - start.get_width() // 2, 460))

    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        go = self.big_font.render("GAME OVER", True, RED)
        self.screen.blit(go,
                         (WIDTH // 2 - go.get_width() // 2, 200))

        sc = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(sc,
                         (WIDTH // 2 - sc.get_width() // 2, 280))

        co = self.font.render(
            f"Coins: {self.coin_count}", True, YELLOW)
        self.screen.blit(co,
                         (WIDTH // 2 - co.get_width() // 2, 320))

        restart = self.font.render(
            "Show hand to RESTART", True, GREEN)
        self.screen.blit(restart,
                         (WIDTH // 2 - restart.get_width() // 2,
                          400))

    def update(self, gesture):
        if not self.started:
            if gesture is not None:
                self.started = True
            return

        if self.game_over:
            if gesture is not None:
                self.reset()
                self.started = True
            return

        self.apply_gesture(gesture)
        self.player.update()
        self.frame_count += 1
        self.score += 1

        # Increase speed
        if self.frame_count % 500 == 0:
            self.speed += 0.5

        # Spawn obstacles
        if self.frame_count % 60 == 0:
            self.obstacles.append(Obstacle(self.speed))

        # Spawn coins
        if self.frame_count % 45 == 0:
            self.coins.append(Coin(self.speed))

        # Update obstacles
        for obs in self.obstacles[:]:
            obs.update()
            if obs.y > HEIGHT:
                self.obstacles.remove(obs)
            elif obs.get_rect().colliderect(self.player.get_rect()):
                self.game_over = True

        # Update coins
        for coin in self.coins[:]:
            coin.update()
            if coin.y > HEIGHT:
                self.coins.remove(coin)
            elif (not coin.collected and
                  coin.get_rect().colliderect(
                      self.player.get_rect())):
                coin.collected = True
                self.coin_count += 1
                self.coins.remove(coin)

    def draw(self):
        self.draw_background()

        for coin in self.coins:
            coin.draw(self.screen)

        for obs in self.obstacles:
            obs.draw(self.screen)

        self.player.draw(self.screen)
        self.draw_hud()

        if not self.started:
            self.draw_start_screen()
        elif self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def tick(self):
        self.clock.tick(FPS)