import pygame
import sys
import os
import math

# =========================================================================
# 1. SETTINGS & DATA
# =========================================================================
WIDTH = 1280
HEIGHT = 720
FPS = 60
TILESIZE = 64

class C:
    bg = (120, 224, 143) 
    player = (41, 128, 185)
    soil_dry = (211, 84, 0) # Warna tanah kering
    hp_color = (231, 76, 60)
    energy_color = (241, 196, 15)
    ui_bg = (34, 34, 34)
    ui_border = (236, 240, 241)

def load_img(path, size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size: img = pygame.transform.scale(img, size)
        return img
    except:
        surf = pygame.Surface(size if size else (TILESIZE, TILESIZE))
        surf.fill((255, 0, 255))
        return surf

# =========================================================================
# 2. SISTEM UI (HUD)
# =========================================================================
class UI:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 24)

    def show_bar(self, current, max_amount, x, y, width, height, color):
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.display_surface, C.ui_bg, bg_rect)
        ratio = max(0, current / max_amount) 
        current_rect = pygame.Rect(x, y, width * ratio, height)
        pygame.draw.rect(self.display_surface, color, current_rect)
        pygame.draw.rect(self.display_surface, C.ui_border, bg_rect, 2)

    def display(self, player):
        self.show_bar(player.health, player.max_health, 20, 20, 200, 20, C.hp_color)
        self.show_bar(player.energy, player.max_energy, 20, 50, 150, 15, C.energy_color)

# =========================================================================
# 3. ENVIRONMENT & FARMING (BARU!)
# =========================================================================
class Soil(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(C.soil_dry)
        self.rect = self.image.get_rect(topleft = pos)
        # Hitbox dibuat sangat rendah agar selalu digambar di bawah kaki pemain
        self.hitbox = self.rect.inflate(0, -60) 

# =========================================================================
# 4. CLASS PLAYER (DENGAN FARMING GRID-SNAP)
# =========================================================================
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, enemy_sprites):
        super().__init__(groups)
        
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
        self.visible_sprites = groups[0] # Butuh akses ke grup untuk mencetak tanah

        self.max_health = 100
        self.health = 100
        self.max_energy = 100
        self.energy = 100

        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = 0

        self.farming = False
        self.farm_cooldown = 300
        self.farm_time = 0

        self.vulnerable = True
        self.hurt_time = 0
        self.invincibility_duration = 1000 

    def input(self):
        if not self.attacking and not self.farming:
            keys = pygame.key.get_pressed()

            # Gerak
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

            self.image = self.animations[self.status]

            # Serang (SPASI)
            if keys[pygame.K_SPACE] and self.energy >= 5: 
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.energy -= 5 
                self.direction.x = 0; self.direction.y = 0
                self.attack_logic()

            # Bertani (F) -> Grid Snapping!
            if keys[pygame.K_f] and self.energy >= 2:
                self.farming = True
                self.farm_time = pygame.time.get_ticks()
                self.energy -= 2
                self.direction.x = 0; self.direction.y = 0
                
                # Matematika Snap-to-Grid: Mengunci kordinat ke kelipatan 64
                target_x = (self.rect.centerx // TILESIZE) * TILESIZE
                target_y = (self.rect.centery // TILESIZE) * TILESIZE
                
                # Cetak tanah di koordinat yang sudah terkunci
                Soil((target_x, target_y), [self.visible_sprites])

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
        if self.farming and current_time - self.farm_time >= self.farm_cooldown:
            self.farming = False
        if not self.vulnerable and current_time - self.hurt_time >= self.invincibility_duration:
            self.vulnerable = True
        if self.energy < self.max_energy and not self.attacking and not self.farming:
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

        if not self.vulnerable:
            alpha = self.image.get_alpha()
            if alpha is None: alpha = 255
            self.image.set_alpha(255 if alpha == 100 else 100)
        else:
            self.image.set_alpha(255)

# =========================================================================
# 5. CLASS ENEMY (DENGAN KECERDASAN BUATAN / AI!)
# =========================================================================
class Enemy(pygame.sprite.Sprite):
    def __init__(self, name, hp, speed, pos, image_path, size, groups, obstacle_sprites, player):
        super().__init__(groups)
        self.image = load_img(image_path, size)
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(-10, -20)
        
        self.name = name
        self.health = hp
        self.speed = speed
        self.obstacle_sprites = obstacle_sprites
        self.player = player # Musuh harus tahu siapa yang diincar
        self.aggro_radius = 400 # Seberapa jauh musuh bisa "melihat" pemain
        
        self.vulnerable = True
        self.hurt_time = 0

    def get_player_distance_direction(self):
        """Matematika Vektor untuk mencari jarak dan arah pemain"""
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(self.player.rect.center)
        
        distance = (player_vec - enemy_vec).magnitude()
        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()
            
        return distance, direction

    def take_damage(self, amount):
        if self.vulnerable:
            self.health -= amount
            self.vulnerable = False
            self.hurt_time = pygame.time.get_ticks()
            self.image.set_alpha(100) 
            
            if self.health <= 0:
                print(f"☠️ {self.name} MUSNAH!")
                self.kill()

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if not self.vulnerable and current_time - self.hurt_time >= 400: # Kebal 400ms setelah dipukul
            self.vulnerable = True
            if self.image.get_alpha() is not None and self.image.get_alpha() < 255:
                self.image.set_alpha(255)

    def update(self):
        self.cooldowns()
        
        # AI LOGIC: Jika pemain masuk area aggro, KEJAR!
        if self.vulnerable:
            distance, direction = self.get_player_distance_direction()
            if 0 < distance < self.aggro_radius:
                self.hitbox.x += direction.x * self.speed
                self.hitbox.y += direction.y * self.speed
                self.rect.center = self.hitbox.center

# =========================================================================
# 6. KAMERA & LEVEL
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
        # 1. Panggil Pemain dulu (karena musuh butuh referensi pemain untuk mengejar)
        self.player = Player((640, 360), [self.visible_sprites], self.obstacle_sprites, self.enemy_sprites)

        # 2. Panggil Monster dengan kecepatan (speed) yang berbeda-beda
        # Enemy(Nama, HP, Speed, Posisi, Path_Gambar, Size, Groups, Obstacles, Target_Player)
        Enemy('Tuyul Agresif', 50, 3, (800, 400), 'assets/chars/npc_tuyul/down_0.png', (TILESIZE, TILESIZE), [self.visible_sprites, self.enemy_sprites], self.obstacle_sprites, self.player)
        Enemy('Jamur Beracun', 40, 1.5, (400, 600), 'assets/chars/running_mushroom/down_0.png', (TILESIZE, TILESIZE), [self.visible_sprites, self.enemy_sprites], self.obstacle_sprites, self.player)
        
        # SANG BOS NAGA RAKSASA (HP Tebal, Kecepatan sedang, Aggro Radius luas)
        naga = Enemy('SANG NAGA HYANG', 300, 2, (1000, 200), 'assets/chars/npc_naga/down_0.png', (150, 150), [self.visible_sprites, self.enemy_sprites], self.obstacle_sprites, self.player)
        naga.aggro_radius = 600 # Naga bisa melihatmu dari jauh!

    def run(self):
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()
        self.ui.display(self.player) 

# =========================================================================
# 7. ENGINE UTAMA
# =========================================================================
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Lembah Karsa V17: Action-RPG Farming')
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
