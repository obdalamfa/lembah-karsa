import pygame
import sys

# =========================================================================
# 1. SETTINGS & DATA
# =========================================================================
WIDTH = 1280
HEIGHT = 720
FPS = 60
TILESIZE = 64

class C:
    bg = '#111111'
    player = '#2980b9'
    enemy = '#e74c3c'
    soil_dry = '#d35400'
    soil_wet = '#8e44ad'

CROPS = {
    'lobak': {'name': 'Lobak', 'days': 2, 'sell': 22},
    'wortel': {'name': 'Wortel', 'days': 3, 'sell': 35},
}

# =========================================================================
# 2. CLASS PLAYER
# =========================================================================
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites):
        super().__init__(groups)
        
        # Wujud Karakter
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(C.player)
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0, -26) # Hitbox 3D

        # Fisika & Status
        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.status = 'down'
        self.obstacle_sprites = obstacle_sprites

        # State Machine (Kunci Action RPG)
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = 0

        self.farming = False
        self.farm_cooldown = 300
        self.farm_time = 0

    def input(self):
        # Hanya bisa input jika sedang tidak menyerang / bertani
        if not self.attacking and not self.farming:
            keys = pygame.key.get_pressed()

            # Gerak
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.direction.x = 1
                self.status = 'right'
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.direction.x = -1
                self.status = 'left'
            else:
                self.direction.x = 0

            # Aksi Pertarungan (Spasi)
            if keys[pygame.K_SPACE]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.direction.x = 0; self.direction.y = 0
                print(f"⚔️ TEBASAN PEDANG ke arah {self.status}!")

            # Aksi Bertani (Tombol F)
            if keys[pygame.K_f]:
                self.farming = True
                self.farm_time = pygame.time.get_ticks()
                self.direction.x = 0; self.direction.y = 0
                print(f"🌱 MENCANGKUL/MENYIRAM TANAH di {self.status}!")

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if self.attacking and current_time - self.attack_time >= self.attack_cooldown:
            self.attacking = False
        if self.farming and current_time - self.farm_time >= self.farm_cooldown:
            self.farming = False

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
# 3. CLASS ENEMY
# =========================================================================
class Enemy(pygame.sprite.Sprite):
    def __init__(self, name, hp, pos, groups, obstacle_sprites):
        super().__init__(groups)
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(C.enemy)
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0, -10)
        
        self.name = name
        self.health = hp
        self.obstacle_sprites = obstacle_sprites

    def take_damage(self, amount):
        self.health -= amount
        print(f"💥 {self.name} terkena {amount} DMG! (HP: {self.health})")
        if self.health <= 0:
            print(f"☠️ {self.name} MATI! (Drop Loot: Kristal Gua)")
            self.kill()

    def update(self):
        # AI Mengejar pemain akan ditaruh di sini nanti
        pass

# =========================================================================
# 4. SISTEM KAMERA
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

        # Y-Sort Effect (Efek Kedalaman 3D)
        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

# =========================================================================
# 5. CLASS LEVEL
# =========================================================================
class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.create_map()

    def create_map(self):
        # 1. Lahirkan Ksatria Petani kita
        self.player = Player((640, 360), [self.visible_sprites], self.obstacle_sprites)
        
        # 2. Lahirkan Monster dari Gua Sang Hyang
        Enemy('Tuyul Agresif', 50, (800, 400), [self.visible_sprites], self.obstacle_sprites)
        Enemy('Jamur Beracun', 30, (500, 500), [self.visible_sprites], self.obstacle_sprites)
        Enemy('SANG NAGA HYANG', 1000, (1200, 800), [self.visible_sprites], self.obstacle_sprites)

    def run(self):
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()

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
