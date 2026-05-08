"""
particles.py — Sistem partikel visual bergaya Octopath Traveller HD-2D.
Partikel di-manage di world-space, render mengikuti kamera.
"""
import pygame
import random
import math
from .config import TILE

# ─── Satu partikel ────────────────────────────────────────
class Particle:
    __slots__ = ['x', 'y', 'vx', 'vy', 'lt', 'max_lt',
                 'r', 'g', 'b', 'size', 'a0', 'grav', 'rot', 'rot_spd']

    def __init__(self, x, y, vx, vy, lifetime, color, size=2, alpha=210, grav=0.0, rot=0.0):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.lt = lifetime
        self.max_lt = lifetime
        self.r, self.g, self.b = int(color[0]), int(color[1]), int(color[2])
        self.size = size
        self.a0 = alpha
        self.grav = grav
        self.rot = rot
        self.rot_spd = random.uniform(-2, 2)

    def update(self, dt_ms: float):
        s = dt_ms * 0.001
        self.x += self.vx * s
        self.y += self.vy * s
        self.vy += self.grav * s
        self.vx *= 0.98          # mild air resistance
        self.lt -= dt_ms
        self.rot += self.rot_spd * s

    @property
    def alive(self) -> bool:
        return self.lt > 0

    def alpha(self) -> int:
        ratio = max(0.0, self.lt / self.max_lt)
        return int(self.a0 * ratio)


# ─── Sistem partikel ──────────────────────────────────────
class ParticleSystem:
    MAX = 400   # batas atas partikel sekaligus

    def __init__(self):
        self.particles: list[Particle] = []
        self._amb_acc = 0
        # Surface kecil reusable untuk rendering dot
        self._dot1 = pygame.Surface((2, 2), pygame.SRCALPHA)
        self._dot2 = pygame.Surface((4, 4), pygame.SRCALPHA)
        self._dot3 = pygame.Surface((6, 6), pygame.SRCALPHA)
        self._dot4 = pygame.Surface((8, 8), pygame.SRCALPHA)

    def _add(self, p: Particle):
        if len(self.particles) < self.MAX:
            self.particles.append(p)

    def update(self, dt: float):
        alive = []
        for p in self.particles:
            p.update(dt)
            if p.alive:
                alive.append(p)
        self.particles = alive

    def render(self, surface: pygame.Surface, cam_px: int, cam_py: int, view_h_px: int):
        sw = surface.get_width()
        for p in self.particles:
            sx = int(p.x + cam_px)
            sy = int(p.y + cam_py)
            if sx < -8 or sx > sw + 8 or sy < -8 or sy > view_h_px + 8:
                continue
            a = p.alpha()
            if a < 4:
                continue
            col = (p.r, p.g, p.b, a)
            sz = p.size
            if sz <= 1:
                self._dot1.fill(col)
                surface.blit(self._dot1, (sx, sy))
            elif sz == 2:
                self._dot2.fill((0, 0, 0, 0))
                pygame.draw.circle(self._dot2, col, (2, 2), 2)
                surface.blit(self._dot2, (sx - 2, sy - 2))
            elif sz == 3:
                self._dot3.fill((0, 0, 0, 0))
                pygame.draw.circle(self._dot3, col, (3, 3), 3)
                surface.blit(self._dot3, (sx - 3, sy - 3))
            else:
                self._dot4.fill((0, 0, 0, 0))
                pygame.draw.circle(self._dot4, col, (4, 4), 4)
                surface.blit(self._dot4, (sx - 4, sy - 4))

    # ── Spawn helpers ──────────────────────────────────────

    def spawn_leaf(self, wx: float, wy: float, n: int = 2):
        """Daun jatuh dari pohon — terinspirasi Octopath musim gugur."""
        colors = [
            (88, 168, 58), (68, 135, 48), (115, 185, 68),
            (205, 168, 55), (225, 132, 42), (190, 110, 35),
        ]
        for _ in range(n):
            self._add(Particle(
                wx + random.uniform(-TILE * 0.6, TILE * 0.6),
                wy + random.uniform(-TILE * 0.3, TILE * 0.3),
                random.uniform(-28, 28),
                random.uniform(18, 45),
                random.randint(1400, 3200),
                random.choice(colors),
                size=random.choice([1, 1, 2]),
                alpha=random.randint(160, 230),
                grav=15.0,
                rot=random.uniform(0, math.pi * 2),
            ))

    def spawn_dust(self, wx: float, wy: float):
        """Debu langkah kaki di tanah."""
        for _ in range(random.randint(1, 3)):
            self._add(Particle(
                wx + random.uniform(-TILE * 0.4, TILE * 0.4),
                wy + TILE * 0.8,
                random.uniform(-20, 20),
                random.uniform(-12, -3),
                random.randint(280, 550),
                random.choice([(195, 165, 115), (185, 155, 105), (205, 175, 125)]),
                size=1,
                alpha=75,
            ))

    def spawn_sparkle(self, wx: float, wy: float, n: int = 7):
        """Bintang sparkle saat panen."""
        colors = [(255, 238, 58), (255, 215, 105), (215, 255, 108), (255, 255, 210)]
        for _ in range(n):
            angle = random.uniform(0, math.pi * 2)
            spd = random.uniform(28, 95)
            self._add(Particle(
                wx + random.uniform(-5, 5),
                wy + random.uniform(-5, 5),
                math.cos(angle) * spd,
                math.sin(angle) * spd - 45,
                random.randint(650, 1150),
                random.choice(colors),
                size=random.choice([1, 1, 2]),
                alpha=245,
                grav=32.0,
            ))

    def spawn_harvest_burst(self, wx: float, wy: float):
        """Efek panen besar — naik ke atas."""
        self.spawn_sparkle(wx + TILE / 2, wy + TILE / 2, n=10)
        colors = [(255, 228, 58), (200, 255, 80)]
        for _ in range(5):
            self._add(Particle(
                wx + TILE / 2 + random.uniform(-6, 6),
                wy + TILE / 2,
                random.uniform(-30, 30),
                random.uniform(-80, -35),
                random.randint(700, 1300),
                random.choice(colors),
                size=2,
                alpha=230,
                grav=28.0,
            ))

    def spawn_magic(self, wx: float, wy: float, n: int = 4):
        """Partikel ungu untuk makhluk supernatural."""
        colors = [(185, 105, 255), (225, 155, 255), (145, 82, 225), (255, 185, 255)]
        for _ in range(n):
            angle = random.uniform(0, math.pi * 2)
            spd = random.uniform(14, 58)
            self._add(Particle(
                wx + random.uniform(-TILE * 0.5, TILE * 0.5),
                wy + random.uniform(-TILE * 0.5, TILE * 0.5),
                math.cos(angle) * spd,
                math.sin(angle) * spd - 24,
                random.randint(650, 1350),
                random.choice(colors),
                size=random.choice([1, 2]),
                alpha=210,
            ))

    def spawn_fire_ember(self, wx: float, wy: float):
        """Bara api mengambang dari perapian/lentera."""
        colors = [(255, 125, 22), (255, 205, 58), (255, 82, 12), (255, 168, 32)]
        self._add(Particle(
            wx + random.uniform(-TILE * 0.3, TILE * 0.3),
            wy + random.uniform(-TILE * 0.2, TILE * 0.1),
            random.uniform(-14, 14),
            random.uniform(-55, -28),
            random.randint(380, 780),
            random.choice(colors),
            size=random.choice([1, 1, 2]),
            alpha=238,
        ))

    def spawn_chop_debris(self, wx: float, wy: float):
        """Serpihan kayu saat menebang pohon."""
        colors = [(145, 92, 42), (185, 125, 62), (105, 68, 32)]
        for _ in range(7):
            angle = random.uniform(0, math.pi * 2)
            spd = random.uniform(45, 105)
            self._add(Particle(
                wx + TILE / 2 + random.uniform(-5, 5),
                wy + TILE / 2 + random.uniform(-5, 5),
                math.cos(angle) * spd,
                math.sin(angle) * spd,
                random.randint(420, 750),
                random.choice(colors),
                size=random.choice([1, 2]),
                alpha=215,
                grav=65.0,
            ))

    def spawn_rain_splash(self, wx: float, wy: float):
        """Percikan hujan mengenai tanah."""
        for _ in range(2):
            self._add(Particle(
                wx + random.uniform(-4, 4),
                wy,
                random.uniform(-24, 24),
                random.uniform(-20, -7),
                random.randint(115, 285),
                (145, 188, 255),
                size=1,
                alpha=155,
                grav=42.0,
            ))

    def spawn_capture_burst(self, wx: float, wy: float):
        """Efek saat makhluk halus tertangkap."""
        self.spawn_magic(wx, wy, n=12)
        self.spawn_sparkle(wx, wy, n=6)

    def spawn_water_splash(self, wx: float, wy: float):
        """Percikan saat menyiram."""
        for _ in range(4):
            self._add(Particle(
                wx + TILE / 2 + random.uniform(-6, 6),
                wy + TILE / 2,
                random.uniform(-35, 35),
                random.uniform(-45, -18),
                random.randint(300, 620),
                random.choice([(130, 200, 255), (100, 180, 255), (160, 220, 255)]),
                size=random.choice([1, 1, 2]),
                alpha=190,
                grav=45.0,
            ))

    def tick_ambient(self, cam_wx: float, cam_wy: float, view_w: int, view_h: int,
                     dt: float, is_night: bool):
        """Ambient particles tiap frame (debu melayang, serbuk sari, dll)."""
        self._amb_acc += dt
        if self._amb_acc < 600:
            return
        self._amb_acc = 0
        if len(self.particles) >= self.MAX - 10:
            return
        # Dust mote melayang lembut
        wx = (cam_wx + random.uniform(0, view_w)) * TILE
        wy = (cam_wy + random.uniform(0, view_h)) * TILE
        if is_night:
            # Partikel ungu samar di malam hari
            self._add(Particle(
                wx, wy,
                random.uniform(-5, 5),
                random.uniform(-8, -2),
                random.randint(4000, 8000),
                random.choice([(180, 150, 240), (200, 170, 255)]),
                size=1,
                alpha=35,
            ))
        else:
            # Serbuk sari / debu emas siang hari
            self._add(Particle(
                wx, wy,
                random.uniform(-6, 6),
                random.uniform(-9, -3),
                random.randint(3500, 7000),
                random.choice([(215, 208, 185), (235, 225, 190), (200, 210, 175)]),
                size=1,
                alpha=40,
            ))
