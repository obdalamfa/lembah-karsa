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
    bg = '#78e08f' # Warna rumput sementara
    player = '#2980b9'
    enemy = '#e74c3c'

# =========================================================================
# 2. FUNGSI LOAD GAMBAR
# =========================================================================
def load_img(path, size=None):
    """Fungsi ajaib untuk mengambil gambar PNG dari folder assets"""
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except:
        # Jika gambar tidak ada, buat kotak warna darurat
        surf = pygame.Surface(size if size else (TILESIZE, TILESIZE))
        surf.fill('magenta')
        return surf

# =========================================================================
# 3. CLASS PLAYER (DENGAN SISTEM TEBASAN!)
# =========================================================================
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, enemy_sprites):
        super().__init__(groups)
        
        # Load Gambar Asli Pemain (Sesuai folder V17)
        self.image = load_img('assets/chars/player/down_0.png', (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(-10, -26) # Hitbox badan

        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.status = 'down'
        
        self.obstacle_sprites = obstacle_sprites
        self.enemy_sprites = enemy_sprites # Pemain harus tahu siapa musuhnya!

        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = 0

    def input(self):
        if not self.attacking:
            keys = pygame.key.get_pressed()

            # Gerak
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.direction.y = -1
                self.status = 'up'
                self.image = load_img('assets/chars/player/up_0.png', (TILESIZE, TILESIZE))
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.direction.y = 1
                self.status = 'down'
                self.image = load_img('assets/chars/player/down_0.png', (TILESIZE, TILESIZE))
            else:
                self.direction.y = 0

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.direction.x = 1
                self.status = 'right'
                self.image = load_img('assets/chars/player/right_0.png', (TILESIZE, TILESIZE))
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.direction.x = -1
                self.status = 'left'
                self.image = load_img('assets/chars/player/left_0.png', (TILESIZE, TILESIZE))
            else:
                self.direction.x = 0

            # Aksi Pertarungan (Spasi)
            if keys[pygame.K_SPACE]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.direction.x = 0
                self.direction.y = 0
                self.attack_logic() # Panggil jurus pedang!

    def attack_logic(self):
        """Logika untuk melukai musuh di depan pemain"""
        # 1. Buat "Pedang Tak Kasat Mata" (Attack Rect) di depan pemain
        attack_rect = self.rect.copy()
        jarak_serang = 40

        if self.status == 'right': attack_rect.x += jarak_serang
        elif self.status == 'left': attack_rect.x -= jarak_serang
        elif self.status == 'down': attack_rect.y += jarak_serang
        elif self.status == 'up': attack_rect.y -= jarak_serang

        # 2. Cek apakah Pedang ini mengenai Musuh
        for enemy in self.enemy_sprites:
            if attack_rect.colliderect(enemy.hitbox):
                enemy.take_damage(25) # Beri 25 Damage ke monster!

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if self.attacking and current_time - self.attack_time >= self.attack_cooldown:
            self.attacking = False

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
        print(f"💥 {self.name} terkena tebasan! Sisa HP: {self.health}")
        
        # Efek berkedip saat kena pukul (Bikin gambar jadi putih sebentar)
        self.image.set_alpha(100) 
        
        if self.health <= 0:
            print(f"☠️ {self.name} MUSNAH!")
            self.kill()

    def update(self):
        # Kembalikan warna normal
        if self.image.get_alpha() < 255:
            self.image.set_alpha(255)

# =========================================================================
# 5. SISTEM KAMERA Y-SORT
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

# =========================================================================
# 6. CLASS LEVEL & ENGINE UTAMA
# =========================================================================
class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group() # Grup khusus untuk musuh
        
        self.create_map()

    def create_map(self):
        # 1. Panggil Monster
        # Memakai gambar dari folder assets/chars/
        Enemy('Tuyul Agresif', 50, (800, 400), 'assets/chars/npc_tuyul/down_0.png', (TILESIZE, TILESIZE), [self.visible_sprites, self.enemy_sprites], self.obstacle_sprites)
        Enemy('Jamur Beracun', 50, (500, 500), 'assets/chars/running_mushroom/down_0.png', (TILESIZE, TILESIZE), [self.visible_sprites, self.enemy_sprites], self.obstacle_sprites)
        
        # SANG BOS NAGA RAKSASA!
        Enemy('SANG NAGA HYANG', 200, (1000, 200), 'assets/chars/npc_naga/down_0.png', (150, 150), [self.visible_sprites, self.enemy_sprites], self.obstacle_sprites)

        # 2. Panggil Karakter Pemain (Dan kenalkan dia ke musuh-musuhnya)
        self.player = Player((640, 360), [self.visible_sprites], self.obstacle_sprites, self.enemy_sprites)

    def run(self):
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()

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
    
