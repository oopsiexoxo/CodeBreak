import pygame
import math
from src.constants import *

def draw_tower_visual(screen, tower_type, x, y, width, height, color):
    rect = pygame.Rect(x - width//2, y - height//2, width, height)
    
    # Base Glow
    s = pygame.Surface((width + 10, height + 10), pygame.SRCALPHA)
    pygame.draw.rect(s, (*color, 50), s.get_rect(), border_radius=5)
    screen.blit(s, (x - width//2 - 5, y - height//2 - 5))

    # Main Body
    pygame.draw.rect(screen, (20, 20, 30), rect, border_radius=5)
    pygame.draw.rect(screen, color, rect, 2, border_radius=5)
    
    # Specific Designs
    if tower_type == "FIREWALL":
        # Brick pattern or shield
        pygame.draw.line(screen, color, (x - 10, y - 10), (x + 10, y - 10), 2)
        pygame.draw.line(screen, color, (x - 10, y), (x + 10, y), 2)
        pygame.draw.line(screen, color, (x - 10, y + 10), (x + 10, y + 10), 2)
        pygame.draw.line(screen, color, (x, y - 15), (x, y + 15), 2)
        
    elif tower_type == "ANTIVIRUS":
        # Cross
        pygame.draw.rect(screen, color, (x - 5, y - 12, 10, 24))
        pygame.draw.rect(screen, color, (x - 12, y - 5, 24, 10))
        
    elif tower_type == "IDS":
        # Eye / Radar
        pygame.draw.circle(screen, color, (x, y), 12, 2)
        pygame.draw.circle(screen, color, (x, y), 4)

    elif tower_type == "HONEYPOT":
         # Trap / Hexagon
         points = [
             (x, y - 15),
             (x + 13, y - 7),
             (x + 13, y + 7),
             (x, y + 15),
             (x - 13, y + 7),
             (x - 13, y - 7)
         ]
         pygame.draw.polygon(screen, color, points, 2)
         pygame.draw.circle(screen, color, (x, y), 5)

class Projectile:
    def __init__(self, x, y, target, damage, color, tower_type):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.color = color
        self.tower_type = tower_type
        self.speed = 12
        self.active = True
        
    def move(self, speed_mult=1.0):
        if self.target.health <= 0:
            self.active = False
            return

        effective_speed = self.speed * speed_mult
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < effective_speed:
            # Calculate Damage Multiplier
            multiplier = 1.0
            if self.tower_type in DAMAGE_MULTIPLIERS:
                multiplier = DAMAGE_MULTIPLIERS[self.tower_type].get(self.target.type, 1.0)
                
            final_damage = self.damage * multiplier
            self.target.take_damage(final_damage)
            self.active = False
        else:
            self.x += (dx / distance) * effective_speed
            self.y += (dy / distance) * effective_speed
            
    def draw(self, screen):
        # Glowing effect
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 4)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), 2)

class Tower:
    def __init__(self, tower_type, x, y):
        self.type = tower_type
        stats = TOWER_TYPES[tower_type]
        self.name = stats["name"]
        self.range = stats["range"]
        self.damage = stats["damage"]
        self.rate = stats["rate"]
        self.color = stats["color"]
        self.slow_factor = stats.get("slow_factor", 1.0)
        
        self.x = x
        self.y = y
        self.reload_timer = 0
        self.width = 40
        self.height = 40
        
    def draw(self, screen):
        draw_tower_visual(screen, self.type, self.x, self.y, self.width, self.height, self.color)

    def draw_range(self, screen):
         range_surface = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
         pygame.draw.circle(range_surface, (*self.color, 30), (self.range, self.range), self.range)
         pygame.draw.circle(range_surface, (*self.color, 100), (self.range, self.range), self.range, 1)
         screen.blit(range_surface, (self.x - self.range, self.y - self.range))

    def update(self, enemies, dt, rate_multiplier=1.0):
        if self.type == "HONEYPOT":
            # Passive effect: Slow enemies in range
            for enemy in enemies:
                dist = math.sqrt((self.x - enemy.x)**2 + (self.y - enemy.y)**2)
                if dist <= self.range:
                    # Calculate Multiplier
                    multiplier = 1.0
                    if self.type in DAMAGE_MULTIPLIERS:
                         multiplier = DAMAGE_MULTIPLIERS[self.type].get(enemy.type, 1.0)
                    
                    effective_slow = self.slow_factor / multiplier
                    if effective_slow > 1.0: effective_slow = 1.0

                    enemy.apply_slow(effective_slow, 100) # Apply slow for 100ms (refreshes every frame)
            return None

        if self.reload_timer > 0:
            self.reload_timer -= dt # dt is actually time elapsed since last frame OR time.time() delta?
            # Wait, in game.py we are passing time.time()! 
            # That is WRONG. 'dt' should be delta time.
            # But the original code passed time.time() ??
            # Let's check game.py again.
            # "tower.update(self.enemies, time.time())" -> This was passing absolute time as dt?
            # If reload_timer is decreased by absolute time, it would be negative instantly.
            # Unless reload_timer was set to future timestamp?
            # self.reload_timer = self.rate (which is like 500ms?)
            # If self.rate is in milliseconds (e.g. 500), and dt is absolute time (huge number), 
            # then reload_timer -= huge_number -> instantly ready.
            # This implies the original code might have been broken or I misunderstood 'rate'.
            # rate in constants.py is "rate": 500.
            # If update was called with time.time(), reload_timer would break.
            # BUT, let's look at previous game.py
            # "tower.update(self.enemies, time.time())"
            # And tower.py: "self.reload_timer -= dt"
            # This confirms the original code was likely broken or rate logic was different.
            # Wait, maybe 'rate' is a timestamp of NEXT shot?
            # "self.reload_timer = self.rate"
            # If self.rate is 500 (ms), reload_timer is 500.
            # dt is time.time() (seconds, e.g. 1700000000).
            # 500 - 1700000000 is negative. Always fires.
            # So towers were firing every frame?
            
            # Correction: I should fix this to use proper delta time.
            # In game.py, I will calculate dt.
            
            # For now, let's update signature.
            return None
            
        target = self.find_target(enemies)
        if target:
            # Scale reload rate by multiplier (rate is delay in ms, so lower is faster)
            self.reload_timer = self.rate * (1.0 / rate_multiplier)
            return Projectile(self.x, self.y, target, self.damage, self.color, self.type)
        return None
        
    def find_target(self, enemies):
        for enemy in enemies:
            dist = math.sqrt((self.x - enemy.x)**2 + (self.y - enemy.y)**2)
            if dist <= self.range:
                return enemy
        return None
