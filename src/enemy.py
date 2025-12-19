import pygame
import math
from src.constants import *

def draw_enemy_visual(screen, enemy_type, x, y, radius, color, health_pct=1.0):
    # Draw distinct shapes for new types
    if enemy_type == "MALWARE":
        pygame.draw.circle(screen, color, (int(x), int(y)), radius)
        for i in range(0, 360, 45):
            rad = math.radians(i)
            sx = x + math.cos(rad) * (radius + 5)
            sy = y + math.sin(rad) * (radius + 5)
            pygame.draw.circle(screen, color, (int(sx), int(sy)), 3)
            
    elif enemy_type == "PHISHING":
        points = [
            (x, y - radius - 5),
            (x - radius - 2, y + radius),
            (x + radius + 2, y + radius)
        ]
        pygame.draw.polygon(screen, color, points)
        
    elif enemy_type == "DDOS":
        pygame.draw.circle(screen, color, (int(x), int(y)), radius)
        pygame.draw.circle(screen, (50, 0, 0), (int(x), int(y)), radius - 5)
        pygame.draw.circle(screen, color, (int(x), int(y)), radius - 10)

    elif enemy_type == "RANSOMWARE":
        # Square / Lock shape
        rect = pygame.Rect(x - radius, y - radius, radius*2, radius*2)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, (x - 5, y - 5, 10, 10)) # Keyhole
        
    elif enemy_type == "SOCIAL_ENG":
        # Question mark / Deceptive shape
        pygame.draw.circle(screen, color, (int(x), int(y)), radius)
        font = pygame.font.SysFont("Arial", 20, bold=True)
        text = font.render("?", True, BLACK)
        screen.blit(text, (x - 5, y - 12))

    elif enemy_type == "ZEUS":
        # Boss visual - Large Red Skull-like shape
        pygame.draw.circle(screen, color, (int(x), int(y)), radius)
        # Eyes
        pygame.draw.circle(screen, BLACK, (int(x) - 15, int(y) - 10), 8)
        pygame.draw.circle(screen, BLACK, (int(x) + 15, int(y) - 10), 8)
        # Glowing pupils
        pygame.draw.circle(screen, NEON_YELLOW, (int(x) - 15, int(y) - 10), 3)
        pygame.draw.circle(screen, NEON_YELLOW, (int(x) + 15, int(y) - 10), 3)
        # Mouth / Grin
        pygame.draw.arc(screen, BLACK, (int(x) - 20, int(y) - 20, 40, 50), 3.14, 0, 3)

    elif enemy_type == "SQL_INJECTION":
            # Orange Diamond / Injection Needle
            points = [
                (x, y - radius),
                (x + radius//2, y),
                (x, y + radius),
                (x - radius//2, y)
            ]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.line(screen, WHITE, (x, y - radius), (x, y + radius), 2)
            
    elif enemy_type == "APT":
            # Mega Boss - Dark Purple Hexagon with core
            points = []
            for i in range(6):
                angle_deg = 60 * i
                rad = math.radians(angle_deg)
                px = x + math.cos(rad) * radius
                py = y + math.sin(rad) * radius
                points.append((px, py))
            pygame.draw.polygon(screen, color, points)
            pygame.draw.circle(screen, (50, 0, 50), (int(x), int(y)), radius - 10)
            pygame.draw.circle(screen, NEON_PURPLE, (int(x), int(y)), 10) # Core

    # Health Bar (Optional, only if health_pct < 1 or strictly requested, but for codex we might skip it or show full)
    if health_pct < 1.0:
        health_width = 30
        if enemy_type == "ZEUS": health_width = 60 # Bigger bar for boss
        elif enemy_type == "APT": health_width = 80
    
        health_height = 4
        health_x = x - health_width / 2
        health_y = y - radius - 12
        
        pygame.draw.rect(screen, (50, 0, 0), (health_x, health_y, health_width, health_height))
        current_health_width = health_pct * health_width
        pygame.draw.rect(screen, NEON_GREEN, (health_x, health_y, current_health_width, health_height))

class Enemy:
    def __init__(self, enemy_type, waypoints):
        self.type = enemy_type
        stats = ENEMY_TYPES[enemy_type]
        self.base_speed = stats["speed"]
        self.speed = self.base_speed
        self.health = stats["health"]
        self.max_health = stats["health"]
        self.reward = stats["reward"]
        self.color = stats["color"]
        self.radius = stats["radius"]
        
        self.waypoints = waypoints
        self.waypoint_index = 0
        self.x = self.waypoints[0][0]
        self.y = self.waypoints[0][1]
        self.finished = False
        
        self.target_x, self.target_y = self.waypoints[1]
        
        # Status Effects
        self.slow_timer = 0
        
    def apply_slow(self, factor, duration):
        # Apply slow effect (doesn't stack, just refreshes)
        self.speed = self.base_speed * factor
        self.slow_timer = duration

    def move(self, speed_mult=1.0):
        # Handle Slow timer
        if self.slow_timer > 0:
            self.slow_timer -= 16 * speed_mult # Scale timer by speed
            if self.slow_timer <= 0:
                self.speed = self.base_speed
        else:
            self.speed = self.base_speed

        effective_speed = self.speed * speed_mult

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < effective_speed:
            self.x = self.target_x
            self.y = self.target_y
            self.waypoint_index += 1
            
            if self.waypoint_index >= len(self.waypoints):
                self.finished = True
                return
                
            self.target_x, self.target_y = self.waypoints[self.waypoint_index]
        else:
            self.x += (dx / distance) * effective_speed
            self.y += (dy / distance) * effective_speed
            
    def draw(self, screen):
        draw_enemy_visual(screen, self.type, self.x, self.y, self.radius, self.color, self.health / self.max_health)
        
        # Slow Indicator
        if self.slow_timer > 0:
            pygame.draw.circle(screen, NEON_PINK, (int(self.x), int(self.y - self.radius - 15)), 3)

    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0
