import pygame, sys

pygame.init()

# 화면 설정
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("플레이어 + 배경 레이어")

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# 캐릭터 설정
PLAYER_SPEED = 5
JUMP_STRENGTH = 15
GRAVITY = 1
ROLL_DURATION = 30

# 플레이어 클래스
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.sprite_sheet = pygame.image.load("Idle.png").convert_alpha()  # 업로드한 PNG
        self.frames = []
        self.frame_index = 0
        self.animation_speed = 0.15
        self.load_frames()
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.rect.bottom = SCREEN_HEIGHT - 10

        self.dx = 0
        self.dy = 0
        self.is_jumping = False
        self.is_rolling = False
        self.roll_frames = 0
        self.is_attacking = False
        self.attack_frames = 0
        self.max_health = 100
        self.health = 100
        self.font = pygame.font.SysFont(None, 28, bold=True)

    # 🔹 업로드한 PNG를 캐릭터 중심 기준으로 균등하게 자르기
    def load_frames(self):
        sheet_width = self.sprite_sheet.get_width()
        sheet_height = self.sprite_sheet.get_height()
        num_frames = 6  # PNG에 있는 프레임 수
        frame_width = sheet_width // num_frames
        for i in range(num_frames):
            frame = self.sprite_sheet.subsurface(
                pygame.Rect(i * frame_width, 0, frame_width, sheet_height)
            )
            # 중심 기준으로 프레임 조정 (필요시)
            self.frames.append(frame)

    def update(self):
        if self.health <= 0:
            return

        keys = pygame.key.get_pressed()
        self.dx = 0

        if not self.is_rolling:
            if keys[pygame.K_a]:
                self.dx = -PLAYER_SPEED
            if keys[pygame.K_d]:
                self.dx = PLAYER_SPEED
            if keys[pygame.K_SPACE] and not self.is_jumping:
                self.dy = -JUMP_STRENGTH
                self.is_jumping = True
            if keys[pygame.K_z] and not self.is_rolling:
                self.is_rolling = True
                self.roll_frames = ROLL_DURATION
                self.dx = PLAYER_SPEED * (1 if self.rect.centerx > SCREEN_WIDTH / 2 else -1)

        self.dy += GRAVITY
        self.rect.y += self.dy

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.is_jumping = False

        if self.is_rolling:
            self.roll_frames -= 1
            if self.roll_frames <= 0:
                self.is_rolling = False

        if self.is_attacking:
            self.attack_frames -= 1
            if self.attack_frames <= 0:
                self.is_attacking = False

        # 🔹 애니메이션 업데이트
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def attack(self):
        if not self.is_attacking:
            self.is_attacking = True
            self.attack_frames = 10

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def draw_health_bar(self, surface):
        bar_width = 300
        bar_height = 30
        x, y = 20, 20
        ratio = self.health / self.max_health if self.max_health > 0 else 0
        pygame.draw.rect(surface, (100, 0, 0), (x, y, bar_width, bar_height), border_radius=10)
        pygame.draw.rect(surface, GREEN, (x, y, int(bar_width*ratio), bar_height), border_radius=10)
        pygame.draw.rect(surface, WHITE, (x, y, bar_width, bar_height), 3, border_radius=10)
        health_text = self.font.render(f"{self.health}/{self.max_health}", True, WHITE)
        text_rect = health_text.get_rect(center=(x + bar_width//2, y + bar_height//2))
        surface.blit(health_text, text_rect)

# 플레이어 생성
player = Player()

# 폰트 & 버튼
big_font = pygame.font.SysFont("arial", 80, bold=True)
button_font = pygame.font.SysFont("malgungothic", 40, bold=True)
button_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 50, 300, 80)

def draw_game_over(surface):
    game_over_text = big_font.render("GAME OVER", True, RED)
    text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
    surface.blit(game_over_text, text_rect)
    pygame.draw.rect(surface, WHITE, button_rect, border_radius=15)
    restart_text = button_font.render("게임 재시작", True, BLACK)
    restart_rect = restart_text.get_rect(center=button_rect.center)
    surface.blit(restart_text, restart_rect)

# 🔹 배경 PNG 불러오기
layer1 = pygame.image.load("background1.png")
layer2 = pygame.image.load("background2.png")
layer3 = pygame.image.load("background3.png")
layer4 = pygame.image.load("background4.png")
layer1 = pygame.transform.scale(layer1, (SCREEN_WIDTH, SCREEN_HEIGHT))
layer2 = pygame.transform.scale(layer2, (SCREEN_WIDTH, SCREEN_HEIGHT))
layer3 = pygame.transform.scale(layer3, (SCREEN_WIDTH, SCREEN_HEIGHT))
layer4 = pygame.transform.scale(layer4, (SCREEN_WIDTH, SCREEN_HEIGHT))

# 🔹 배경 위치 변수
bg_x = 0

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
        if player.health > 0:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    player.attack()
                if event.button == 3:
                    player.take_damage(20)
        else:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_rect.collidepoint(event.pos):
                    player.health = player.max_health
                    player.rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT - 50)

    # 플레이어 입력 처리
    keys = pygame.key.get_pressed()
    dx = 0
    if keys[pygame.K_a]:
        dx = -PLAYER_SPEED
    if keys[pygame.K_d]:
        dx = PLAYER_SPEED

    # 플레이어 업데이트
    if player.health > 0:
        player.update()

    # 배경 스크롤 처리 (플레이어 화면 절반 이후부터)
    if (dx > 0 and player.rect.centerx >= SCREEN_WIDTH//2) or (dx < 0 and player.rect.centerx <= SCREEN_WIDTH//2):
        bg_x -= dx
    else:
        player.rect.x += dx

    # 배경 무한 반복
    bg_x %= SCREEN_WIDTH

    # 화면 그리기 (레이어 반복)
    for layer in [layer1, layer2, layer3, layer4]:
        screen.blit(layer, (bg_x, 0))
        screen.blit(layer, (bg_x - SCREEN_WIDTH, 0))

    if player.health > 0:
        player.draw(screen)
        player.draw_health_bar(screen)
    else:
        draw_game_over(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()