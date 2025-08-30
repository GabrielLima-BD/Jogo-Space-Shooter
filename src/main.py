# Space Shooter Demo - Python + Pygame
# Controles:
#  - Esquerda/Direita ou A/D: mover
#  - ESPAÇO: atirar
#  - P: pausar
#  - R: reiniciar (após game over)
#  - ESC: sair

import os
import sys
import random
import pygame

# ---------------- Paths ----------------
if getattr(sys, 'frozen', False):  # executável via PyInstaller
    BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------- Config ----------------
WIDTH, HEIGHT = 480, 720
FPS = 60
TITLE = "Space Shooter Demo"
SAVE_FILE = os.path.join(BASE_DIR, "save_highscore.json")

# Player
PLAYER_SPEED = 6
PLAYER_COOLDOWN = 300  # ms
PLAYER_MAX_LIVES = 3

# Bullets
BULLET_SPEED = -9
BULLET_SIZE = (4, 12)

# Colors
WHITE = (235, 235, 235)
BG = (7, 7, 16)
GREEN = (80, 220, 100)

# ---------------- Utils ----------------
def load_highscore():
    try:
        if os.path.exists(SAVE_FILE):
            import json
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return int(data.get("highscore", 0))
    except Exception:
        pass
    return 0

def save_highscore(value: int):
    try:
        import json
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump({"highscore": int(value)}, f)
    except Exception:
        pass

# ---------------- Entities -------------
class Player(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = pygame.image.load(
            os.path.join(BASE_DIR, "assets/ships/player.png")
        ).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))  # Player maior
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 70))
        self.speed = PLAYER_SPEED
        self.last_shot = 0
        self.lives = PLAYER_MAX_LIVES
        self.invuln_ms = 0

    def update(self, dt, keys):
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
        self.rect.x += dx

        if self.rect.left < 20:
            self.rect.left = 20
        if self.rect.right > WIDTH - 20:
            self.rect.right = WIDTH - 20

        if self.invuln_ms > 0:
            self.invuln_ms -= dt

    def can_shoot(self):
        now = pygame.time.get_ticks()
        return (now - self.last_shot) >= PLAYER_COOLDOWN

    def shoot(self, bullet_group, all_sprites, sound):
        if not self.can_shoot():
            return
        self.last_shot = pygame.time.get_ticks()
        bullet = Bullet(self.rect.centerx, self.rect.top)
        bullet_group.add(bullet)
        all_sprites.add(bullet)
        sound.play()

    def hit(self):
        if self.invuln_ms > 0:
            return False
        self.lives -= 1
        self.invuln_ms = 1200
        return True

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface(BULLET_SIZE, pygame.SRCALPHA)
        pygame.draw.rect(self.image, (250, 210, 80),
                         self.image.get_rect(), border_radius=2)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = BULLET_SPEED

    def update(self, dt):
        self.rect.y += self.vel
        if self.rect.bottom < 0:
            self.kill()

class EnemyBase(pygame.sprite.Sprite):
    def __init__(self, image_path, health, speed, size):
        super().__init__()
        self.image = pygame.image.load(
            os.path.join(BASE_DIR, image_path)
        ).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect(
            midbottom=(random.randint(30, WIDTH-30), -10))
        self.health = health
        self.speed = speed

    def update(self, dt):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()
            return True
        return False

class EnemyEasy(EnemyBase):
    def __init__(self):
        super().__init__("assets/ships/EnemyEasy.png", 1, 2, (40, 40))

class EnemyMedium(EnemyBase):
    def __init__(self):
        super().__init__("assets/ships/EnemyMedium.png", 3, 2, (55, 55))

class EnemyHard(EnemyBase):
    def __init__(self):
        super().__init__("assets/ships/EnemyHard.png", 5, 1, (75, 75))

class StarField:
    def __init__(self, n=40):
        self.stars = []
        for _ in range(n):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            s = random.choice([1, 2])  # estrelas menores
            speed = random.uniform(0.5, 1.2) * s
            self.stars.append([x, y, s, speed])

    def update(self, dt):
        for st in self.stars:
            st[1] += st[3]
            if st[1] > HEIGHT:
                st[0] = random.randint(0, WIDTH)
                st[1] = -5

    def draw(self, screen):
        for x, y, s, _ in self.stars:
            pygame.draw.circle(screen, WHITE, (int(x), int(y)), s)

# ---------------- Game -----------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # Sons
        self.shoot_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "assets/sounds/gunplayer.mp3"))
        self.dead_player_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "assets/sounds/deadplayer.mp3"))
        self.dead_enemy_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "assets/sounds/deadenemy.mp3"))
        self.start_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "assets/sounds/gamestart.mp3"))
        self.music = pygame.mixer.Sound(os.path.join(BASE_DIR, "assets/sounds/musicgame.mp3"))
        self.music.set_volume(0.3)
        self.music.play(-1)

        # Fontes
        self.font_sm = pygame.font.SysFont("arial", 18)
        self.font_md = pygame.font.SysFont("arial", 28, bold=True)
        self.font_lg = pygame.font.SysFont("arial", 48, bold=True)

        self.reset()

    def reset(self):
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        self.starfield = StarField(n=40)
        self.player = Player()
        self.all_sprites.add(self.player)

        self.score = 0
        self.highscore = load_highscore()
        self.game_over = False
        self.paused = False

        self.enemy_spawn_ms = 1200
        self._last_enemy = 0
        self._last_hard_spawn = 0  # Corrige crash ao atingir 100 pontos

        self.start_sound.play()
        
    def spawn_enemy(self):
        now = pygame.time.get_ticks()

        # Contagem atual
        easy_alive = len([e for e in self.enemies if isinstance(e, EnemyEasy)])
        medium_alive = len([e for e in self.enemies if isinstance(e, EnemyMedium)])
        hard_alive = len([e for e in self.enemies if isinstance(e, EnemyHard)])

        # Regras por score
        if self.score < 50:
            # Apenas Easy
            if easy_alive < 6:  
                enemy = EnemyEasy()
            else:
                return

        elif self.score < 100:
            # Easy + Medium
            if random.random() < 0.6:
                if easy_alive < 6:
                    enemy = EnemyEasy()
                else:
                    enemy = EnemyMedium()
            else:
                if medium_alive < 4:
                    enemy = EnemyMedium()
                else:
                    enemy = EnemyEasy()

        else:
            # A partir de 100 → Easy + Medium + Hard
            r = random.random()

            # Chance de Hard, respeitando limites
            if r > 0.8 and hard_alive < 2 and (now - self._last_hard_spawn >= 5000):
                enemy = EnemyHard()
                self._last_hard_spawn = now  

            elif r > 0.4:
                # Medium preferido
                if hard_alive > 0 and medium_alive >= 4:
                    return  # não deixa passar limite
                enemy = EnemyMedium()

            else:
                # Easy
                if hard_alive > 0 and easy_alive >= 2:
                    return
                enemy = EnemyEasy()

        self.enemies.add(enemy)
        self.all_sprites.add(enemy)


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if not self.game_over and event.key == pygame.K_p:
                    self.paused = not self.paused
                if self.game_over and event.key == pygame.K_r:
                    self.reset()

        keys = pygame.key.get_pressed()
        if not self.game_over and not self.paused:
            if keys[pygame.K_SPACE]:
                self.player.shoot(self.bullets, self.all_sprites, self.shoot_sound)
        return keys

    def update(self, dt, keys):
        if self.game_over or self.paused:
            return

        if self.score < 200:
            self.enemy_spawn_ms = 1200
        elif self.score < 500:
            self.enemy_spawn_ms = 900
        else:
            self.enemy_spawn_ms = 600

        now = pygame.time.get_ticks()
        if now - self._last_enemy >= self.enemy_spawn_ms:
            self._last_enemy = now
            self.spawn_enemy()

        self.player.update(dt, keys)
        self.bullets.update(dt)
        self.enemies.update(dt)
        self.starfield.update(dt)

        # Colisões: bala x inimigo
        for bullet in self.bullets:
            hits = pygame.sprite.spritecollide(bullet, self.enemies, False)
            for enemy in hits:
                if enemy.hit():
                    self.dead_enemy_sound.play()
                    self.score += 10
                bullet.kill()

        # Colisões: player x inimigo
        hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
        if hits:
            if self.player.hit():
                self.dead_player_sound.play()
            if self.player.lives <= 0:
                self._end_game()

    def _end_game(self):
        self.game_over = True
        if self.score > self.highscore:
            self.highscore = self.score
            save_highscore(self.highscore)

    def draw_hud(self):
        score_s = self.font_md.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_s, (16, 12))
        hs_s = self.font_sm.render(f"Recorde: {self.highscore}", True, (200, 200, 200))
        self.screen.blit(hs_s, (16, 44))

        for i in range(self.player.lives):
            pygame.draw.polygon(self.screen, GREEN,
                                [(WIDTH-30 - i*22, 20), (WIDTH-22 - i*22, 36), (WIDTH-38 - i*22, 36)])

        if self.paused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            self.screen.blit(overlay, (0, 0))
            t = self.font_lg.render("PAUSADO", True, WHITE)
            self.screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2 - 10)))

    def draw_gameover(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))

        t = self.font_lg.render("GAME OVER", True, WHITE)
        self.screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2 - 30)))
        s1 = self.font_md.render(f"Pontuação: {self.score}", True, WHITE)
        self.screen.blit(s1, s1.get_rect(center=(WIDTH//2, HEIGHT//2 + 10)))
        s2 = self.font_sm.render("Pressione R para reiniciar", True, WHITE)
        self.screen.blit(s2, s2.get_rect(center=(WIDTH//2, HEIGHT//2 + 44)))

    def draw(self):
        self.screen.fill(BG)
        self.starfield.draw(self.screen)
        self.all_sprites.draw(self.screen)
        self.draw_hud()
        if self.game_over:
            self.draw_gameover()
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            keys = self.handle_events()
            self.update(dt, keys)
            self.draw()
        pygame.quit()

def main():
    Game().run()

if __name__ == "__main__":
    main()
