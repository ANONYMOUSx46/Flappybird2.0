import pygame
import sys
import random
import os
import math

# Initialize pygame
pygame.init()

# Load sound effects
def load_sound(name):
    return pygame.mixer.Sound(name) if os.path.exists(name) else None

flap_sound = load_sound('flap.wav')
hit_sound = load_sound('hit.wav')
score_sound = load_sound('score.wav')

# Optional background image
if os.path.exists('background.png'):
    bg_image = pygame.image.load('background.png').convert()
    bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
else:
    bg_image = None

# Game constants
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
GRAVITY = 0.25
FLAP_STRENGTH = -5
PIPE_GAP = 100
PIPE_SPEED = 3
PIPE_FREQUENCY = 1500  # milliseconds
FLOOR_HEIGHT = 112
ANIMATION_SPEED = 0.1

# Colors
SKY_BLUE = (113, 197, 207)
LIGHT_BLUE = (174, 228, 238)
CLOUD_WHITE = (255, 255, 255)
GRASS_GREEN = (111, 196, 76)
DIRT_BROWN = (222, 184, 135)
PIPE_GREEN = (95, 173, 65)
PIPE_BORDER = (76, 140, 54)
SCORE_YELLOW = (255, 204, 0)
SCORE_OUTLINE = (255, 100, 10)
GOLD = (255, 215, 0)
TITLE_ORANGE = (255, 102, 0)

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Function to create gradient background
def create_gradient_background():
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    # Draw sky gradient
    for y in range(SCREEN_HEIGHT - FLOOR_HEIGHT):
        ratio = y / (SCREEN_HEIGHT - FLOOR_HEIGHT)
        r = int(LIGHT_BLUE[0] * (1 - ratio) + SKY_BLUE[0] * ratio)
        g = int(LIGHT_BLUE[1] * (1 - ratio) + SKY_BLUE[1] * ratio)
        b = int(LIGHT_BLUE[2] * (1 - ratio) + SKY_BLUE[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    # Draw some clouds
    for i in range(5):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(20, 150)
        size = random.randint(20, 40)
        for j in range(3):
            offset_x = random.randint(-10, 10)
            offset_y = random.randint(-5, 5)
            pygame.draw.circle(surface, CLOUD_WHITE, (x + offset_x, y + offset_y), size)
    # Add a sun in the corner
    pygame.draw.circle(surface, (255, 255, 220), (30, 30), 40)
    pygame.draw.circle(surface, (255, 255, 180), (30, 30), 30)
    # Add distant hills
    for i in range(3):
        hill_height = random.randint(30, 60)
        hill_width = random.randint(100, 200)
        hill_x = random.randint(-50, SCREEN_WIDTH)
        hill_y = SCREEN_HEIGHT - FLOOR_HEIGHT
        hill_color = (GRASS_GREEN[0] - 20, GRASS_GREEN[1] - 20, GRASS_GREEN[2] - 20)
        pygame.draw.ellipse(surface, hill_color, (hill_x, hill_y - hill_height, hill_width, hill_height * 2))
    return surface

# Function to create decorative base/ground
def create_base():
    surface = pygame.Surface((336, FLOOR_HEIGHT))
    pygame.draw.rect(surface, GRASS_GREEN, (0, 0, 336, 20))
    pygame.draw.rect(surface, DIRT_BROWN, (0, 20, 336, FLOOR_HEIGHT - 20))
    for i in range(30):
        x = random.randint(0, 336)
        pygame.draw.line(surface, (111, 196, 76), (x, 0), (x, random.randint(3, 10)), 2)
    for i in range(80):
        x = random.randint(0, 336)
        y = random.randint(25, FLOOR_HEIGHT - 5)
        size = random.randint(2, 6)
        color_offset = random.randint(-20, 20)
        dirt_color = (DIRT_BROWN[0] + color_offset, DIRT_BROWN[1] + color_offset, DIRT_BROWN[2] + color_offset)
        pygame.draw.circle(surface, dirt_color, (x, y), size)
    return surface

# Create function to render outlined text
def draw_text_with_outline(text, font, text_color, outline_color, outline_width=2):
    base = font.render(text, True, text_color)
    w, h = base.get_size()
    outline_surface = pygame.Surface((w + outline_width * 2, h + outline_width * 2), pygame.SRCALPHA)
    for dx in range(-outline_width, outline_width + 1, 2):
        for dy in range(-outline_width, outline_width + 1, 2):
            if dx == 0 and dy == 0:
                continue
            outline_surface.blit(font.render(text, True, outline_color), (outline_width + dx, outline_width + dy))
    outline_surface.blit(base, (outline_width, outline_width))
    return outline_surface

# Create start screen
def create_start_screen():
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    title_font = pygame.font.SysFont('Arial', 40, bold=True)
    title = draw_text_with_outline("FLAPPY", title_font, TITLE_ORANGE, (0, 0, 0), 3)
    title2 = draw_text_with_outline("BIRD", title_font, TITLE_ORANGE, (0, 0, 0), 3)
    for i in range(10, 0, -2):
        glow_color = (255, 200, 0, int(10 * i))
        glow_surface = pygame.Surface((title.get_width() + i * 2, title.get_height() + i * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surface, glow_color, (0, 0, title.get_width() + i * 2, title.get_height() + i * 2))
        surface.blit(glow_surface, ((SCREEN_WIDTH - title.get_width()) // 2 - i, 80 - i))
    surface.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 80))
    surface.blit(title2, ((SCREEN_WIDTH - title2.get_width()) // 2, 130))
    instr_font = pygame.font.SysFont('Arial', 20)
    instr1 = draw_text_with_outline("Tap to flap", instr_font, (255, 255, 255), (0, 0, 0), 2)
    instr2 = draw_text_with_outline("Avoid pipes", instr_font, (255, 255, 255), (0, 0, 0), 2)
    surface.blit(instr1, ((SCREEN_WIDTH - instr1.get_width()) // 2, 200))
    surface.blit(instr2, ((SCREEN_WIDTH - instr2.get_width()) // 2, 230))
    ready_font = pygame.font.SysFont('Arial', 30, bold=True)
    ready_text = draw_text_with_outline("GET READY!", ready_font, (255, 255, 100), (200, 0, 0), 2)
    surface.blit(ready_text, ((SCREEN_WIDTH - ready_text.get_width()) // 2, 300))
    bird = load_image("bird1")
    surface.blit(bird, ((SCREEN_WIDTH - bird.get_width()) // 2, 350))
    pygame.draw.polygon(surface, (255, 255, 255), [(SCREEN_WIDTH // 2, 400), (SCREEN_WIDTH // 2 - 10, 390), (SCREEN_WIDTH // 2 + 10, 390)])
    return surface

# Create game over screen
def create_game_over_screen():
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    font_large = pygame.font.SysFont('Arial', 40, bold=True)
    game_over = draw_text_with_outline("GAME OVER", font_large, (255, 50, 50), (0, 0, 0), 3)
    shadow = pygame.Surface((game_over.get_width() + 20, game_over.get_height() + 20), pygame.SRCALPHA)
    shadow.fill((0, 0, 0, 100))
    surface.blit(shadow, ((SCREEN_WIDTH - shadow.get_width()) // 2, 150))
    surface.blit(game_over, ((SCREEN_WIDTH - game_over.get_width()) // 2, 150))
    font_small = pygame.font.SysFont('Arial', 20)
    restart = draw_text_with_outline("Tap to restart", font_small, (255, 255, 255), (0, 0, 0), 2)
    surface.blit(restart, ((SCREEN_WIDTH - restart.get_width()) // 2, 250))
    bird = load_image("bird1")
    sad_bird = pygame.transform.rotate(bird, -90)
    surface.blit(sad_bird, ((SCREEN_WIDTH - sad_bird.get_width()) // 2, 300))
    pygame.draw.line(surface, (255, 0, 0), (SCREEN_WIDTH // 2 - 5, 305), (SCREEN_WIDTH // 2 + 5, 315), 2)
    pygame.draw.line(surface, (255, 0, 0), (SCREEN_WIDTH // 2 + 5, 305), (SCREEN_WIDTH // 2 - 5, 315), 2)
    return surface

# Create Easter egg screen
def create_easter_egg_screen():
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    surface.fill((20, 20, 40))

    # Draw golden egg
    egg_rect = pygame.Rect(0, 0, 80, 110)
    egg_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    pygame.draw.ellipse(surface, (255, 215, 0), egg_rect)  # Shiny golden

    # Draw crown
    crown_color = (255, 223, 0)
    base_y = egg_rect.top - 10
    points = [
        (egg_rect.centerx - 30, base_y),
        (egg_rect.centerx - 15, base_y - 20),
        (egg_rect.centerx, base_y),
        (egg_rect.centerx + 15, base_y - 20),
        (egg_rect.centerx + 30, base_y),
    ]
    pygame.draw.polygon(surface, crown_color, points)
    pygame.draw.rect(surface, crown_color, (egg_rect.centerx - 30, base_y, 60, 10))

    # Add message
    font = pygame.font.SysFont('Arial', 28, bold=True)
    text = draw_text_with_outline("You won the Easter Egg!", font, (255, 255, 255), (0, 0, 0), 2)
    surface.blit(text, ((SCREEN_WIDTH - text.get_width()) // 2, egg_rect.bottom + 20))

    return surface

# Load images
def load_image(name):
    if name == "bird1":
        surface = pygame.Surface((34, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(surface, (255, 216, 0), (0, 0, 34, 24))
        pygame.draw.ellipse(surface, (255, 230, 120), (5, 5, 24, 14))
        pygame.draw.circle(surface, (255, 255, 255), (25, 10), 6)
        pygame.draw.circle(surface, (0, 0, 0), (27, 10), 3)
        pygame.draw.polygon(surface, (255, 103, 0), [(30, 12), (34, 12), (32, 16)])
        pygame.draw.ellipse(surface, (255, 254, 174), (8, 12, 15, 10))
        return surface
    elif name == "bird2":
        surface = pygame.Surface((34, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(surface, (255, 216, 0), (0, 0, 34, 24))
        pygame.draw.ellipse(surface, (255, 230, 120), (5, 5, 24, 14))
        pygame.draw.circle(surface, (255, 255, 255), (25, 10), 6)
        pygame.draw.circle(surface, (0, 0, 0), (27, 10), 3)
        pygame.draw.polygon(surface, (255, 103, 0), [(30, 12), (34, 12), (32, 16)])
        pygame.draw.ellipse(surface, (255, 254, 174), (8, 10, 15, 10))
        return surface
    elif name == "bird3":
        surface = pygame.Surface((34, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(surface, (255, 216, 0), (0, 0, 34, 24))
        pygame.draw.ellipse(surface, (255, 230, 120), (5, 5, 24, 14))
        pygame.draw.circle(surface, (255, 255, 255), (25, 10), 6)
        pygame.draw.circle(surface, (0, 0, 0), (27, 10), 3)
        pygame.draw.polygon(surface, (255, 103, 0), [(30, 12), (34, 12), (32, 16)])
        pygame.draw.ellipse(surface, (255, 254, 174), (8, 14, 15, 10))
        return surface
    elif name == "pipe":
        surface = pygame.Surface((52, 320), pygame.SRCALPHA)
        pygame.draw.rect(surface, PIPE_GREEN, (0, 0, 52, 320))
        pygame.draw.rect(surface, PIPE_BORDER, (0, 0, 52, 20))
        pygame.draw.rect(surface, PIPE_BORDER, (0, 300, 52, 20))
        pygame.draw.rect(surface, PIPE_BORDER, (0, 0, 5, 320))
        pygame.draw.rect(surface, PIPE_BORDER, (47, 0, 5, 320))
        pygame.draw.rect(surface, (120, 200, 80), (5, 20, 10, 280))
        return surface

# Load all assets
background = create_gradient_background()
base_img = create_base()
bird_frames = [load_image("bird1"), load_image("bird2"), load_image("bird3")]
pipe_img = load_image("pipe")
start_screen = create_start_screen()
game_over_screen = create_game_over_screen()
easter_egg_screen = create_easter_egg_screen()

# Fonts
score_font = pygame.font.SysFont('Arial', 50, bold=True)

class Bird:
    def __init__(self):
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.frame_count = 0
        self.current_frame = 0
        self.angle = 0
        self.alive = True
        self.flap_sound = flap_sound

    def flap(self):
        self.velocity = FLAP_STRENGTH
        if self.flap_sound:
            self.flap_sound.play()

    def update(self):
        self.frame_count += 1
        if self.frame_count >= 5:
            self.current_frame = (self.current_frame + 1) % 3
            self.frame_count = 0
        self.velocity += GRAVITY
        self.y += self.velocity
        if self.velocity < 0:
            self.angle = 25
        else:
            self.angle = min(-25, -self.velocity * 2)
        if self.y <= 0:
            self.y = 0
            self.velocity = 0
        if self.y >= SCREEN_HEIGHT - FLOOR_HEIGHT - 24:
            self.y = SCREEN_HEIGHT - FLOOR_HEIGHT - 24
            self.velocity = 0
            self.alive = False

    def draw(self):
        bird_surface = bird_frames[self.current_frame]
        rotated_bird = pygame.transform.rotate(bird_surface, self.angle)
        screen.blit(rotated_bird, (self.x - rotated_bird.get_width() // 2, self.y - rotated_bird.get_height() // 2))

    def get_mask(self):
        return pygame.Rect(self.x - 12, self.y - 9, 24, 18)

class Pipe:
    def __init__(self):
        self.is_easter_egg_pipe = False
        self.x = SCREEN_WIDTH
        self.height = random.randint(80, SCREEN_HEIGHT - FLOOR_HEIGHT - PIPE_GAP - 80)
        self.passed = False
        self.top_pipe_rect = pygame.Rect(self.x, 0, 52, self.height)
        self.bottom_pipe_rect = pygame.Rect(self.x, self.height + PIPE_GAP, 52, SCREEN_HEIGHT)

    def update(self):
        self.x -= PIPE_SPEED
        self.top_pipe_rect.x = self.x
        self.bottom_pipe_rect.x = self.x

    def draw(self):
        top_pipe = pygame.transform.flip(pipe_img, False, True)
        screen.blit(top_pipe, (self.x, self.height - 320))
        screen.blit(pipe_img, (self.x, self.height + PIPE_GAP))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        return bird_mask.colliderect(self.top_pipe_rect) or bird_mask.colliderect(self.bottom_pipe_rect)

class Base:
    def __init__(self):
        self.x1 = 0
        self.x2 = 336
        self.y = SCREEN_HEIGHT - FLOOR_HEIGHT

    def update(self):
        self.x1 -= PIPE_SPEED
        self.x2 -= PIPE_SPEED
        if self.x1 + 336 < 0:
            self.x1 = self.x2 + 336
        if self.x2 + 336 < 0:
            self.x2 = self.x1 + 336

    def draw(self):
        screen.blit(base_img, (self.x1, self.y))
        screen.blit(base_img, (self.x2, self.y))

def show_score(score):
    score_text = draw_text_with_outline(str(score), score_font, SCORE_YELLOW, SCORE_OUTLINE, 4)
    scale = 1.0 + 0.05 * math.sin(pygame.time.get_ticks() / 200)
    scaled_score = pygame.transform.scale(score_text, (int(score_text.get_width() * scale), int(score_text.get_height() * scale)))
    screen.blit(scaled_score, (SCREEN_WIDTH // 2 - scaled_score.get_width() // 2, 50))

def trigger_easter_egg():
    print("🐣 Easter Egg Triggered!")
    global game_active, game_over, score, easter_egg_active
    game_active = False
    game_over = False
    score = 1000000
    easter_egg_active = True

def main():
    bird = Bird()
    base = Base()
    pipes = []
    score = 0
    game_active = False
    game_over = False
    easter_egg_active = False
    last_pipe_time = pygame.time.get_ticks()
    pulse_timer = 0
    right_click_times = []
    DOUBLE_CLICK_INTERVAL = 400

    while True:
        clock.tick(60)
        pulse_timer += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE:
                    if game_active:
                        bird.flap()
                    elif game_over or easter_egg_active:
                        bird = Bird()
                        base = Base()
                        pipes = []
                        score = 0
                        game_active = True
                        game_over = False
                        easter_egg_active = False
                    else:
                        game_active = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if game_active:
                        bird.flap()
                    elif game_over or easter_egg_active:
                        bird = Bird()
                        base = Base()
                        pipes = []
                        score = 0
                        game_active = True
                        game_over = False
                        easter_egg_active = False
                    else:
                        game_active = True

                elif event.button == 3:  # Right click
                    now = pygame.time.get_ticks()
                    right_click_times.append(now)
                    right_click_times = right_click_times[-2:]  # Keep last 2 clicks
                    if len(right_click_times) == 2 and (right_click_times[1] - right_click_times[0]) <= DOUBLE_CLICK_INTERVAL:
                        trigger_easter_egg()

        # Draw background
    # Draw background
        if bg_image:
            screen.blit(bg_image, (0, 0))
        else:
            screen.blit(background, (0, 0))

    # ✨ Easter Egg display (moved up to prevent overwrite)
        if easter_egg_active:
            print("🎨 Drawing Easter Egg screen")
            screen.fill((0, 0, 0))
            pygame.draw.circle(screen, (255, 215, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 60)
            pygame.display.update()
            pygame.time.wait(3000)
            print("Resetting after Easter Egg...")
            bird = Bird()
            base = Base()
            pipes = []
            score = 0
            game_active = False
            game_over = False
            easter_egg_active = False
            continue  # This prevents any other screen from drawing over it



        if game_active:
            bird.update()
            bird.draw()

            current_time = pygame.time.get_ticks()
            if current_time - last_pipe_time > PIPE_FREQUENCY:
                new_pipe = Pipe()
                pipes.append(new_pipe)
                last_pipe_time = current_time

            pipes_to_remove = []
            for pipe in pipes:
                pipe.update()
                pipe.draw()

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    score += 1
                    
                    if score_sound:
                        score_sound.play()

                if pipe.x < -52:
                    pipes_to_remove.append(pipe)

                if pipe.collide(bird):
                    game_active = False
                    game_over = True
                    if hit_sound:
                        hit_sound.play()

            for pipe in pipes_to_remove:
                pipes.remove(pipe)

            if bird.y >= SCREEN_HEIGHT - FLOOR_HEIGHT - 24:
                game_active = False
                game_over = True
                if hit_sound:
                    hit_sound.play()

            base.update()
        else:
            if game_over:
                offset = math.sin(pulse_timer / 20) * 3
                screen.blit(game_over_screen, (0, offset))
            elif easter_egg_active:
                print("🎨 Drawing Easter Egg screen")
                screen.fill((0, 0, 0))
                pygame.draw.circle(screen, (255, 215, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 60)
                pygame.display.update()
                pygame.time.wait(3000)
                print("Resetting after Easter Egg...")
                bird = Bird()
                base = Base()
                pipes = []
                score = 0
                game_active = False
                game_over = False
                easter_egg_active = False
                continue
            else:
                scale = 1.0 + 0.02 * math.sin(pulse_timer / 30)
                scaled_start = pygame.transform.scale(start_screen, (int(SCREEN_WIDTH * scale), int(SCREEN_HEIGHT * scale)))
                screen.blit(scaled_start, (SCREEN_WIDTH // 2 - scaled_start.get_width() // 2, SCREEN_HEIGHT // 2 - scaled_start.get_height() // 2))
            for pipe in pipes:
                pipe.draw()
            bird.current_frame = (pulse_timer // 10) % 3
            bird.draw()

        base.draw()
        if game_active or game_over:
            show_score(score)

        pygame.display.update()

if __name__ == "__main__":
    main()
