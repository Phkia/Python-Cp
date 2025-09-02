import pygame, sys, random
import time

pygame.init()

# 화면 설정
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flying Bullet Game")

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (120, 120, 120)

# 플레이어 속도
PLAYER_SPEED = 10

# 상태
STATE_MENU = "menu"
STATE_GAME = "game"
STATE_GAMEOVER = "gameover"
game_state = STATE_MENU

# 유틸: 이미지 로드
def load_image_or_placeholder(path, size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception:
        surf = pygame.Surface(size if size else (64, 64), pygame.SRCALPHA)
        pygame.draw.rect(surf, (200, 200, 200), (0, 0, surf.get_width(), surf.get_height()))
        return surf

# 배경 이미지
menu_background = load_image_or_placeholder("menu_background.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
game_background = load_image_or_placeholder("level1_background.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
gameover_background = load_image_or_placeholder("gameover_background.png", (SCREEN_WIDTH, SCREEN_HEIGHT))

# 버튼 클래스
class Button:
    def __init__(self, text, pos, size=(300, 100), font_size=50):
        self.rect = pygame.Rect(0, 0, *size)
        self.rect.center = pos
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.color_idle = (70, 70, 70)
        self.color_hover = (150, 150, 150)
        self.border_radius = 25

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = self.color_hover if self.rect.collidepoint(mouse_pos) else self.color_idle
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

# 플레이어 클래스
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image_or_placeholder("Idle.png", (80, 80))
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.is_invincible = False
        self.invincible_start = 0

    def update(self):
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_a]:
            dx = -PLAYER_SPEED
        if keys[pygame.K_d]:
            dx = PLAYER_SPEED
        if keys[pygame.K_w]:
            dy = -PLAYER_SPEED
        if keys[pygame.K_s]:
            dy = PLAYER_SPEED
        self.rect.x += dx
        self.rect.y += dy
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        # 무적 시간 체크
        if self.is_invincible and time.time() - self.invincible_start >= 2:
            self.is_invincible = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# 하트 클래스
class Heart:
    def __init__(self, image_path, pos):
        self.image = load_image_or_placeholder(image_path, (50,50))
        self.rect = self.image.get_rect(topleft=pos)
        self.alive = True

    def draw(self, surface):
        if self.alive:
            surface.blit(self.image, self.rect)

# Kraken 클래스
class Kraken(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image_or_placeholder("kraken.png", (520,420))
        # 중앙보다 위쪽에 고정 배치
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))

    def update(self):
        # 움직이지 않도록 업데이트 비움
        pass

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# 체력(하트) 세팅
heart_positions = [(20 + i*60, 20) for i in range(5)]
hearts = [Heart("heart.png", pos) for pos in heart_positions]

# 게임 객체
player = Player()
kraken = Kraken()

# 버튼 생성
start_button = Button("Game Start", (SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
restart_button = Button("ReStart", (SCREEN_WIDTH//2, SCREEN_HEIGHT//2))

# 제목 렌더링
def render_text_with_smooth_border(text, font, text_color, border_color, border_thickness=6):
    base_surf = font.render(text, True, text_color)
    w, h = base_surf.get_size()
    surf = pygame.Surface((w + 2*border_thickness, h + 2*border_thickness), pygame.SRCALPHA)
    for dx in range(-border_thickness, border_thickness+1):
        for dy in range(-border_thickness, border_thickness+1):
            distance = (dx**2 + dy**2)**0.5
            if 0 < distance <= border_thickness:
                alpha = max(0, 255 - int(255 * distance / border_thickness))
                border_surf = font.render(text, True, border_color)
                border_surf.set_alpha(alpha)
                surf.blit(border_surf, (dx + border_thickness, dy + border_thickness))
    surf.blit(base_surf, (border_thickness, border_thickness))
    return surf

title_font = pygame.font.Font(None, 150)
menu_title_surf = render_text_with_smooth_border("Monster Hunting", title_font, WHITE, BLACK, 6)
menu_title_rect = menu_title_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 200))
gameover_title_surf = render_text_with_smooth_border("Game Over", title_font, WHITE, BLACK, 6)
gameover_title_rect = gameover_title_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 200))

# 게임 루프
clock = pygame.time.Clock()
running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        if game_state == STATE_MENU and start_button.is_clicked(event):
            game_state = STATE_GAME
            for heart in hearts:
                heart.alive = True
            player.rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
            player.is_invincible = False

        if game_state == STATE_GAMEOVER and restart_button.is_clicked(event):
            game_state = STATE_MENU

    # 게임 업데이트
    if game_state == STATE_GAME:
        player.update()
        kraken.update()

        # 충돌 체크
        if not player.is_invincible and player.rect.colliderect(kraken.rect):
            for heart in reversed(list(hearts)):
                if heart.alive:
                    heart.alive = False
                    break
            player.is_invincible = True
            player.invincible_start = time.time()

        if all(not heart.alive for heart in hearts):
            game_state = STATE_GAMEOVER

    # 화면 그리기
    if game_state == STATE_MENU:
        screen.blit(menu_background, (0,0))
        screen.blit(menu_title_surf, menu_title_rect)
        start_button.draw(screen)

    elif game_state == STATE_GAME:
        screen.blit(game_background, (0,0))
        kraken.draw(screen)
        player.draw(screen)
        for heart in hearts:
            heart.draw(screen)

    elif game_state == STATE_GAMEOVER:
        screen.blit(gameover_background, (0,0))
        screen.blit(gameover_title_surf, gameover_title_rect)
        restart_button.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()