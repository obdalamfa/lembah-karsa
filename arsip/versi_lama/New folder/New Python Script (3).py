import pygame
import sys
import os

# =========================================================================
# 1. SETTINGS & DATA
# =========================================================================
WIDTH = 1280
HEIGHT = 720
FPS = 60
TILESIZE = 64

class C:
    # Menggunakan format RGB murni agar support di SEMUA versi Pygame
    bg = (120, 224, 143) 
    player = (41, 128, 185)
    enemy = (231, 76, 60)
    hp_color = (231, 76, 60)
    energy_color = (241, 196, 15)
    ui_bg = (34, 34, 34)
    ui_border = (236, 240, 241)

# =========================================================================
# 2. FUNGSI LOAD GAMBAR & UI HUD
# =========================================================================
def load_img(path, size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except:
        surf = pygame.Surface(size if size else (TILESIZE, TILESIZE))
        surf.fill((255, 0, 255)) # Warna Magenta sebagai fallback
        return surf

class UI:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 24)

    def show_bar(self, current, max_amount, x, y, width, height, color):
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.display_surface, C.ui_bg, bg_rect)

        # Mencegah error jika HP minus
        ratio = max(0, current / max_amount) 
        current_width = width * ratio
        current_rect = pygame.Rect(x, y, current_width, height)
        pygame.draw.rect(self.display_surface, color, current_rect)
        
        pygame.draw.rect(self.display_surface, C.ui_border, bg_rect, 2)

    def display(self, player):
        self.show_bar(player.health, player.max_health, 20, 20, 200, 20, C.hp_color)
        self.show_bar(player.energy, player.max_energy, 20, 50, 150, 15, C.energy_color)

# =========================================================================
# 3. CLASS PLAYER
# =========================================================================
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, enemy_sprites):
        super().__init__(groups)
        
        # PRE-LOAD SEMUA GAMBAR DI AWAL (Anti-Lag/Anti-Memory Leak)
        self.animations = {
            'up': load_img('assets/chars/player/up_0.png', (TILESIZE, TILESIZE)),
            'down': load_img('assets/chars/player/down_0.png', (TILESIZE, TILESIZE)),
            'left': load_img('assets/chars/player/left_0.png', (TILESIZE, TILESIZE)),
            'right': load_img('assets/chars/player/right_0.png', (TILESIZE, TILESIZE))
        }

        self.status = 'down'
        self.image = self.animations[self.status]
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(-10, -26)

        self.direction = pygame.math.Vector2()
        self.speed = 5
        
        self.obstacle_sprites = obstacle_sprites
        self.enemy_sprites = enemy_sprites

        self.max_health = 100
        self.health = 100
        self.max_energy = 100
        self.energy = 100

        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = 0

        self.vulnerable = True
        self.hurt_time = 0
        self.invincibility_duration = 1000 

    def input(self):
        if not self.attacking:
            keys = pygame.key.get_pressed()

            # Gerak & Ganti Status
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.direction.y = -1; self.status = 'up'
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.direction.y = 1; self.status = 'down'
            else:
                self.direction.y = 0

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.direction.x = 1; self.status = 'right'
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.direction.x = -1; self.status = 'left'
            else:
                self.direction.x = 0

            # Ganti gambar sesuai status tanpa nge-load dari harddisk lagi
            self.image = self.animations[self.status]

            # Serang
            if keys[pygame.K_SPACE] and self.energy >= 5: 
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.energy -= 5 
                self.direction.x = 0; self.direction.y = 0
                self.attack_logic()

    def attack_logic(self):
        attack_rect = self.rect.copy()
        jarak_serang = 40
        if self.status == 'right': attack_rect.x += jarak_serang
        elif self.status == 'left': attack_rect.x -= jarak_serang
        elif self.status == 'down': attack_rect.y += jarak_serang
        elif self.status == 'up': attack_rect.y -= jarak_serang

        for enemy in self.enemy_sprites:
            if attack_rect.colliderect(enemy.hitbox):
                enemy.take_damage(25)

    def check_enemy_collision(self):
        if self.vulnerable:
            for enemy in self.enemy_sprites:
                if self.hitbox.colliderect(enemy.hitbox):
                    self.health -= 15 
                    self.vulnerable = False
                    self.hurt_time = pygame.time.get_ticks()
                    break 

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if self.attacking and current_time - self.attack_time >= self.attack_cooldown:
            self.attacking = False
        
        if not self.vulnerable and current_time - self.hurt_time >= self.invincibility_duration:
            self.vulnerable = True

        if self.energy < self.max_energy and not self.attacking:
            self.energy += 0.1 

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        self.hitbox.x += self.direction.x * speed
        self.hitbox.y += self.direction.y * speed
        self.rect.center = self.hitbox.center

    def update(self):
        self.input()
        self.cooldowns()
        self.move(self.speed)
        self.check_enemy_collision() 

        # Keamanan pengecekan Alpha
        if not self.vulnerable:
            alpha = self.image.get_alpha()
            if alpha is None: alpha = 255 # Pencegah Error
            self.image.set_alpha(255 if alpha == 100 else 100)
        else:
            self.image.set_alpha(255)

# =========================================================================
# 4. CLASS ENEMY
# =========================================================================
class Enemy(pygame.sprite.Sprite):
    def __init__(self, name, hp, pos, image_path, size, groups, obstacle_sprites):
        super().__init__(groups)
        self.image = load_img(image_path, size)
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(-10, -20)
        
        self.name = name
        self.health = hp
        self.obstacle_sprites = obstacle_sprites

    def take_damage(self, amount):
        self.health -= amount
        self.image.set_alpha(100) 
        if self.health <= 0:
            self.kill()

    def update(self):
        alpha = self.image.get_alpha()
        if alpha is not None and alpha < 255:
            self.image.set_alpha(255)

# =========================================================================
# 5. KAMERA & LEVEL
# =========================================================================
class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group() 
        self.ui = UI() 
        
        self.create_map()

    def create_map(self):
        Enemy('Tuyul Agresif', 50, (800, 400), 'assets/chars/npc_tuyul/down_0.png', (TILESIZE, TILESIZE), [self.visible_sprites, self.enemy_sprites], self.obstacle_sprites)
        Enemy('Jamur Beracun', 50, (500, 500), 'assets/chars/running_mushroom/down_0.png', (TILESIZE, TILESIZE), [self.visible_sprites, self.enemy_sprites], self.obstacle_sprites)
        Enemy('SANG NAGA HYANG', 200, (1000, 200), 'assets/chars/npc_naga/down_0.png', (150, 150), [self.visible_sprites, self.enemy_sprites], self.obstacle_sprites)

        self.player = Player((640, 360), [self.visible_sprites], self.obstacle_sprites, self.enemy_sprites)

    def run(self):
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()
        self.ui.display(self.player) 

# =========================================================================
# 6. ENGINE UTAMA
# =========================================================================
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Lembah Karsa: Action-RPG Farming')
        self.clock = pygame.time.Clock()
        self.level = Level()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill(C.bg)
            self.level.run()
            
            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()
