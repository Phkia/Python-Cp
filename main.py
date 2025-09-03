import pygame, sys, time, random, math

pygame.init()

# 화면 설정
SCREEN_WIDTH, SCREEN_HEIGHT = 750, 1000
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flying Bullet Game")

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)

# 플레이어 속도
PLAYER_SPEED = 7.5

# 상태
STATE_MENU = "menu"
STATE_COUNTDOWN = "countdown"
STATE_GAME = "game"
STATE_GAMEOVER = "gameover"
STATE_WIN = "win"
STATE_PAUSE = "pause"
game_state = STATE_MENU

countdown_start_time = 0
countdown_number = 3  # 카운트다운 숫자
last_count_update = 0  # 마지막 업데이트 시간

# 이미지 로드
def load_image_or_placeholder(path, size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception:
        surf = pygame.Surface(size if size else (64,64), pygame.SRCALPHA)
        pygame.draw.rect(surf, (200,200,200), (0,0,surf.get_width(),surf.get_height()))
        return surf

# 배경
menu_background = load_image_or_placeholder("menu_background.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
game_background = load_image_or_placeholder("level1_background.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
gameover_background = load_image_or_placeholder("gameover_background.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
win_background = load_image_or_placeholder("win_background.png", (SCREEN_WIDTH, SCREEN_HEIGHT))

# 버튼
class Button:
    def __init__(self, text, pos, size=(300,100), font_size=50):
        self.rect = pygame.Rect(0,0,*size)
        self.rect.center = pos
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.color_idle = (220,220,220)
        self.color_hover = (255,255,255)
        self.border_radius = 25

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = self.color_hover if self.rect.collidepoint(mouse_pos) else self.color_idle
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

# 총알
class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image = load_image_or_placeholder("bullet.png",(30,60))
        self.rect = self.image.get_rect(center=(x,y))
        self.speed = -10
        self.damage = 5
        self.active = True

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

# 적 탄막
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, image_path="enemy_bullet.png", size_x=20, size_y=35):
        super().__init__()
        # 이미지 로드
        try:
            self.image_orig = pygame.image.load(image_path).convert_alpha()
            self.image_orig = pygame.transform.scale(self.image_orig, (size_x, size_y))
        except Exception:
            # 이미지 없으면 정사각형 대체
            self.image_orig = pygame.Surface((size_x, size_y), pygame.SRCALPHA)
            pygame.draw.rect(self.image_orig, (255,50,50), (0,0,size_x,size_y))

        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect(center=(x, y))
        speed = 5
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)
        self.gravity = 0.15
        self.angle = 0
        self.rotation_speed = random.uniform(-5,5)

    def update(self):
        self.vy += self.gravity
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)
        self.angle += self.rotation_speed
        self.image = pygame.transform.rotate(self.image_orig, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        if self.rect.top > SCREEN_HEIGHT or self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

# 플레이어
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image_or_placeholder("Idle.png",(60,60))
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2+200))
        self.is_invincible = False
        self.invincible_start = 0
        self.last_shot_time = 0

    def update(self):
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_a]: dx = -PLAYER_SPEED
        if keys[pygame.K_d]: dx = PLAYER_SPEED
        if keys[pygame.K_w]: dy = -PLAYER_SPEED
        if keys[pygame.K_s]: dy = PLAYER_SPEED
        self.rect.x += dx
        self.rect.y += dy
        self.rect.clamp_ip(pygame.Rect(0,0,SCREEN_WIDTH,SCREEN_HEIGHT))
        if self.is_invincible and time.time()-self.invincible_start>=2:
            self.is_invincible = False

    def shoot(self, bullets_group):
        now = time.time()
        if now - self.last_shot_time >= 2:
            bullet = Bullet(self.rect.centerx, self.rect.top)
            bullets_group.add(bullet)
            self.last_shot_time = now

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# 하트
class Heart:
    def __init__(self,image_path,pos):
        self.image = load_image_or_placeholder(image_path,(50,50))
        self.rect = self.image.get_rect(topleft=pos)
        self.alive = True
    def draw(self,surface):
        if self.alive:
            surface.blit(self.image,self.rect)

# 크라켄
class Kraken(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image_or_placeholder("kraken.png",(500,300))
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//2.1, SCREEN_HEIGHT//4.4))
        self.max_health = 80
        self.health = 80
        self.font = pygame.font.Font(None,40)
    def update(self):
        pass
    def draw(self,surface):
        surface.blit(self.image,self.rect)
        bar_width, bar_height = 400,25
        x = (SCREEN_WIDTH-bar_width)//2
        y = SCREEN_HEIGHT-bar_height-20
        pygame.draw.rect(surface, RED, (x,y,bar_width,bar_height))
        current_width = int(bar_width*(self.health/self.max_health))
        pygame.draw.rect(surface, GREEN, (x,y,current_width,bar_height))
        pygame.draw.rect(surface, BLACK, (x,y,bar_width,bar_height),3)
        text_surf = self.font.render(f"{self.health}/{self.max_health}", True, WHITE)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, y+bar_height//2))
        surface.blit(text_surf, text_rect)

# 폭죽
class FireworkParticle:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3,3)
        self.vy = random.uniform(-12,-6)
        self.color = random.choice([(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,128,0)])
        self.life = random.randint(50,80)
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.25
        self.life -= 1
    def draw(self,surface):
        pygame.draw.circle(surface,self.color,(int(self.x),int(self.y)),8)

# 하트 초기화
heart_positions = [(20+i*60,20) for i in range(5)]
hearts = [Heart("heart.png", pos) for pos in heart_positions]

# 게임 객체
player = Player()
kraken = Kraken()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
particles = []

# 버튼
button_spacing = 120
center_y = SCREEN_HEIGHT//2
start_button = Button("Game Start",(SCREEN_WIDTH//2, center_y-button_spacing//2))
quit_main_button = Button("Quit Game",(SCREEN_WIDTH//2, center_y+button_spacing//2))
restart_button = Button("Restart",(SCREEN_WIDTH//2, center_y-button_spacing//2))
quit_game_button = Button("Quit Game",(SCREEN_WIDTH//2, center_y+button_spacing//2))
resume_button = Button("Resume",(SCREEN_WIDTH//2, center_y-button_spacing))
pause_menu_button = Button("Main Menu",(SCREEN_WIDTH//2, center_y))
quit_pause_button = Button("Quit Game",(SCREEN_WIDTH//2, center_y+button_spacing))

# 텍스트 렌더링
def render_text_with_smooth_border(text, font, text_color, border_color, border_thickness=6):
    base_surf = font.render(text, True, text_color)
    w,h = base_surf.get_size()
    surf = pygame.Surface((w+2*border_thickness, h+2*border_thickness), pygame.SRCALPHA)
    for dx in range(-border_thickness,border_thickness+1):
        for dy in range(-border_thickness,border_thickness+1):
            distance = (dx**2+dy**2)**0.5
            if 0<distance<=border_thickness:
                alpha = max(0,255-int(255*distance/border_thickness))
                border_surf = font.render(text, True, border_color)
                border_surf.set_alpha(alpha)
                surf.blit(border_surf,(dx+border_thickness, dy+border_thickness))
    surf.blit(base_surf,(border_thickness, border_thickness))
    return surf

title_font = pygame.font.Font(None,100)
menu_title_surf = render_text_with_smooth_border("Monster Hunt : Ocean", title_font, WHITE, BLACK, 6)
menu_title_rect = menu_title_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2-200))
gameover_font = pygame.font.Font(None,150)
gameover_title_surf = render_text_with_smooth_border("Game Over", gameover_font, WHITE, BLACK, 6)
gameover_title_rect = gameover_title_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2-200))
victory_font = pygame.font.Font(None,150)
win_title_surf = render_text_with_smooth_border("Victory", victory_font, WHITE, BLACK, 6)
win_title_rect = win_title_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2-200))

# 적 발사 타이머
enemy_last_shot = 0
enemy_shot_delay = 1.5

# 게임 루프
clock = pygame.time.Clock()
running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ESC 처리
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if game_state == STATE_GAME:
                game_state = STATE_PAUSE
            elif game_state == STATE_PAUSE:
                game_state = STATE_COUNTDOWN
                countdown_start_time = time.time()
                countdown_number = 3
                last_count_update = 0

        # 메뉴 버튼
        if game_state == STATE_MENU:
            if start_button.is_clicked(event):
                game_state = STATE_COUNTDOWN
                countdown_start_time = time.time()
                countdown_number = 3
                last_count_update = 0
                for heart in hearts: heart.alive=True
                player.rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2+200)
                player.is_invincible=False
                kraken.health = kraken.max_health
                bullets.empty()
                enemy_bullets.empty()
                particles.clear()
            if quit_main_button.is_clicked(event):
                running=False

        # 게임오버 버튼
        if game_state == STATE_GAMEOVER:
            if restart_button.is_clicked(event):
                game_state=STATE_MENU
                particles.clear()
            if quit_game_button.is_clicked(event):
                running=False

        # 승리 버튼
        if game_state==STATE_WIN:
            if restart_button.is_clicked(event):
                game_state=STATE_MENU
                particles.clear()
            if quit_game_button.is_clicked(event):
                running=False

        # PAUSE 버튼
        if game_state==STATE_PAUSE:
            if resume_button.is_clicked(event):
                game_state=STATE_COUNTDOWN
                countdown_start_time = time.time()
                countdown_number = 3
                last_count_update = 0
            if pause_menu_button.is_clicked(event):
                game_state=STATE_MENU
                particles.clear()
            if quit_pause_button.is_clicked(event):
                running=False

    # COUNTDOWN 처리
    if game_state == STATE_COUNTDOWN:
        elapsed = time.time() - countdown_start_time
        new_count = 3 - int(elapsed)

        if new_count != countdown_number:
            countdown_number = new_count
            last_count_update = time.time()

        screen.blit(game_background, (0,0))
        kraken.draw(screen)
        player.draw(screen)
        bullets.draw(screen)
        enemy_bullets.draw(screen)
        for heart in hearts: heart.draw(screen)

        if countdown_number >= 0:
            font = pygame.font.Font(None, 200)
            count_surf = render_text_with_smooth_border(str(countdown_number), font, WHITE, BLACK, 8)
            count_rect = count_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(count_surf, count_rect)
        else:
            game_state = STATE_GAME

        pygame.display.flip()

    # GAME
    elif game_state == STATE_GAME:
        player.update()
        player.shoot(bullets)
        bullets.update()
        kraken.update()

        # 크라켄 탄막
        now = time.time()
        if now-enemy_last_shot>enemy_shot_delay:
            spawn_x=random.randint(100,SCREEN_WIDTH-100)
            spawn_y=kraken.rect.bottom
            for i in range(12):
                angle=(2*math.pi/12)*i
                enemy_bullets.add(EnemyBullet(spawn_x,spawn_y,angle))
            enemy_last_shot=now

        enemy_bullets.update()

        # 충돌 처리
        if not player.is_invincible and player.rect.colliderect(kraken.rect):
            for heart in reversed(hearts):
                if heart.alive:
                    heart.alive=False
                    break
            player.is_invincible=True
            player.invincible_start=time.time()

        if not player.is_invincible:
            if pygame.sprite.spritecollide(player, enemy_bullets, True):
                for heart in reversed(hearts):
                    if heart.alive:
                        heart.alive=False
                        break
                player.is_invincible=True
                player.invincible_start=time.time()

        for bullet in bullets:
            if bullet.active and bullet.rect.colliderect(kraken.rect):
                kraken.health-=bullet.damage
                bullet.active=False

        if kraken.health<=0:
            kraken.health=0
            game_state=STATE_WIN

        if all(not heart.alive for heart in hearts):
            game_state=STATE_GAMEOVER

    # WIN 폭죽
    if game_state==STATE_WIN:
        if random.random()<0.2:
            particles.append(FireworkParticle(random.randint(100,SCREEN_WIDTH-100), SCREEN_HEIGHT-50))

    # 파티클 업데이트
    for particle in particles[:]:
        particle.update()
        if particle.life<=0:
            particles.remove(particle)

    # 화면 그리기
    if game_state==STATE_MENU:
        screen.blit(menu_background,(0,0))
        screen.blit(menu_title_surf,menu_title_rect)
        start_button.draw(screen)
        quit_main_button.draw(screen)
    elif game_state==STATE_GAMEOVER:
        screen.blit(gameover_background,(0,0))
        screen.blit(gameover_title_surf,gameover_title_rect)
        restart_button.draw(screen)
        quit_game_button.draw(screen)
    elif game_state==STATE_WIN:
        screen.blit(win_background,(0,0))
        screen.blit(win_title_surf,win_title_rect)
        restart_button.draw(screen)
        quit_game_button.draw(screen)
        for particle in particles: particle.draw(screen)
    elif game_state==STATE_PAUSE:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        screen.blit(overlay,(0,0))
        resume_button.draw(screen)
        pause_menu_button.draw(screen)
        quit_pause_button.draw(screen)
    elif game_state==STATE_GAME or game_state==STATE_COUNTDOWN:
        screen.blit(game_background,(0,0))
        kraken.draw(screen)
        player.draw(screen)
        bullets.draw(screen)
        enemy_bullets.draw(screen)
        for heart in hearts: heart.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()