import pygame
import time
import math
import random
from src.constants import *
from src.enemy import Enemy
from src.tower import Tower

class LootDrop:
    def __init__(self, x, y, loot_type):
        self.x = x
        self.y = y
        self.type = loot_type
        self.data = LOOT_TYPES[loot_type]
        self.creation_time = time.time()
        self.duration = self.data["duration"]
        self.collected = False
        
        # Floating animation
        self.float_offset = 0
        self.float_speed = 5.0
        
    def update(self):
        # Check if expired
        if time.time() - self.creation_time > self.duration:
            return False # Remove me
            
        # Animate
        self.float_offset = math.sin(time.time() * self.float_speed) * 3
        return True # Keep me
        
    def draw(self, screen):
        # Draw glowing orb
        color = self.data["color"]
        radius = self.data["radius"]
        
        # Pulse alpha
        alpha = int(150 + math.sin(time.time() * 10) * 100)
        s = pygame.Surface((radius*4, radius*4), pygame.SRCALPHA)
        
        # Outer glow
        pygame.draw.circle(s, (*color, 100), (radius*2, radius*2), radius + 2)
        # Inner core
        pygame.draw.circle(s, (*color, 255), (radius*2, radius*2), radius)
        
        # Symbol
        if self.type == "CRYPTO":
             # $ sign
             font = pygame.font.SysFont("Arial", 12, bold=True)
             txt = font.render("$", True, BLACK)
             s.blit(txt, (radius*2 - 3, radius*2 - 7))
        elif self.type == "PATCH":
             # + sign
             pygame.draw.line(s, BLACK, (radius*2 - 4, radius*2), (radius*2 + 4, radius*2), 2)
             pygame.draw.line(s, BLACK, (radius*2, radius*2 - 4), (radius*2, radius*2 + 4), 2)
             
        screen.blit(s, (self.x - radius*2, self.y - radius*2 + self.float_offset))

class Game:
    def __init__(self, mode="STORY"):
        self.mode = mode
        self.level_index = 0
        self.load_level(self.level_index)
        
        self.game_over = False
        self.game_won = False
        
    def get_level_intel(self):
        # Gather unique enemy types from all waves
        unique_enemies = set()
        for wave in self.waves:
            for group in wave:
                # group is (type, count, delay)
                unique_enemies.add(group[0])
        
        intel_data = []
        for enemy_type in unique_enemies:
            # Find effective towers
            effective_towers = []
            for tower_type, multipliers in DAMAGE_MULTIPLIERS.items():
                if enemy_type in multipliers and multipliers[enemy_type] > 1.0:
                    effective_towers.append(TOWER_TYPES[tower_type]["name"])
            
            intel_data.append({
                "type": enemy_type,
                "name": ENEMY_TYPES[enemy_type]["name"],
                "color": ENEMY_TYPES[enemy_type]["color"],
                "radius": ENEMY_TYPES[enemy_type]["radius"],
                "effective": effective_towers
            })
            
        return intel_data

    def load_level(self, index):
        if self.mode == "STORY":
            if index >= len(LEVELS):
                self.game_won = True
                return
            self.level_data = LEVELS[index]
            self.waves = self.level_data["waves"]
        else: # ENDLESS
            # Pick a map (Corporate Server is good)
            self.level_data = {
                "name": f"ENDLESS WAVE {self.level_index + 1}",
                "story": [
                    "MODE: ENDLESS",
                    "OBJECTIVE: SURVIVE",
                    "WAVES ARE INFINITE."
                ],
                "waypoints": LEVELS[1]["waypoints"],
                "starting_money": 600,
                "waves": [] # Placeholder
            }
            self.waves = []

        self.level_index = index
        self.money = self.level_data["starting_money"]
        self.lives = STARTING_LIVES
        
        self.waypoints = self.level_data["waypoints"]
        
        self.wave_index = 0
        self.enemies = []
        self.towers = []
        self.projectiles = []
        
        self.wave_in_progress = False
        self.enemies_to_spawn = []
        self.spawn_timer = 0
        self.level_complete = False
        
        self.game_speed = 1.0
        self.last_update_time = pygame.time.get_ticks()
        
        # Roguelike Perk System
        self.modifiers = {
            "damage": 1.0,
            "range": 1.0,
            "rate": 1.0,
            "cost": 1.0,
            "reward": 1.0,
            "enemy_slow": 1.0 # Multiplier for enemy speed (lower is slower)
        }
        self.pending_perk_choice = False
        self.generated_perks = []
        self.claimed_perks = set()
        
        self.loot_drops = []
        self.active_buffs = {} # "buff_name": end_time

    def generate_endless_wave(self):
        wave_num = self.wave_index + 1
        budget = wave_num * 300 + 500
        
        generated = []
        possible_enemies = ["MALWARE", "PHISHING", "DDOS", "SOCIAL_ENG", "RANSOMWARE"]
        
        # Difficulty Scaling
        if wave_num >= 5: possible_enemies.append("ZEUS")
        if wave_num >= 10: possible_enemies.append("SQL_INJECTION")
        if wave_num >= 20: possible_enemies.append("APT")

        # Boss Waves (Guaranteed Spawns)
        if wave_num % 10 == 0:
             # Every 10th wave is a mini-boss wave
             generated.append(("SQL_INJECTION", wave_num // 5, 2000))
        
        if wave_num % 25 == 0:
             # Every 25th wave is a MEGA boss wave
             generated.append(("APT", 1, 0))

        while budget > 50:
            etype = random.choice(possible_enemies)
            stats = ENEMY_TYPES[etype]
            cost = stats["health"] * 0.5 + stats["speed"] * 10
            
            if budget >= cost:
                count = random.randint(1, 5)
                total_cost = cost * count
                if total_cost > budget:
                    count = int(budget // cost)
                    total_cost = cost * count
                
                if count > 0:
                    delay = random.randint(300, 1500)
                    generated.append((etype, count, delay))
                    budget -= total_cost
            else:
                # Try cheaper enemy or break
                if cost > 200: continue
                break
                
        if not generated:
             generated.append(("MALWARE", 5, 500))
             
        return generated

    def generate_perk_choices(self):
        keys = list(PERK_TYPES.keys())
        weights = [PERK_TYPES[k].get("weight", 10) for k in keys]
        
        # Weighted selection without replacement is tricky with random.choices (it does replacement)
        # So we iterate 3 times
        
        choices = []
        temp_keys = keys[:]
        temp_weights = weights[:]
        
        for _ in range(3):
            if not temp_keys: break
            choice = random.choices(temp_keys, weights=temp_weights, k=1)[0]
            choices.append(choice)
            
            # Remove chosen to avoid duplicates
            idx = temp_keys.index(choice)
            temp_keys.pop(idx)
            temp_weights.pop(idx)
            
        self.generated_perks = choices

    def apply_perk(self, perk_key):
        perk = PERK_TYPES[perk_key]
        eff = perk["effect"]
        val = perk["value"]
        
        if eff == "lives":
            self.lives += val
        elif eff == "hybrid_dmg_spd":
            # Legendary Quantum Core
            self.modifiers["damage"] *= 1.5
            self.modifiers["rate"] *= 0.8
            # Update towers
            for t in self.towers:
                t.damage *= 1.5
                t.rate *= 0.8
        elif eff == "enemy_slow":
            # Legendary Time Warp
            self.modifiers["enemy_slow"] *= val
        else:
            self.modifiers[eff] *= val
            # Update existing towers
            if eff in ["damage", "range", "rate"]:
                for t in self.towers:
                    if eff == "damage": t.damage *= val
                    elif eff == "range": t.range *= val
                    elif eff == "rate": t.rate *= val
        
        self.pending_perk_choice = False
        self.claimed_perks.add(self.wave_index)
        self.generated_perks = []

    def check_loot_collection(self, mx, my):
        for loot in self.loot_drops[:]:
            dx = mx - loot.x
            dy = my - loot.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            # Collection radius slightly larger than visual
            if dist < 25: 
                # Collect!
                effect = loot.data["effect"]
                value = loot.data["value"]
                
                if effect == "money":
                    self.money += value
                elif effect == "life":
                    self.lives += value
                    if self.lives > STARTING_LIVES: self.lives = STARTING_LIVES
                elif effect == "buff_rate":
                    self.active_buffs["rate_boost"] = time.time() + loot.data["duration"]
                    
                self.loot_drops.remove(loot)

    def start_next_wave(self):
        # Prevent starting next wave if one is active
        if self.wave_in_progress:
            return
            
        # Check for Perk Milestone (every 3 waves)
        if self.wave_index > 0 and self.wave_index % 3 == 0 and not self.level_complete:
             if self.wave_index not in self.claimed_perks:
                 self.pending_perk_choice = True
                 self.generate_perk_choices()
                 return

        wave_data = []
        if self.mode == "STORY":
            if self.wave_index < len(self.waves):
                wave_data = self.waves[self.wave_index]
        else:
            wave_data = self.generate_endless_wave()

        if wave_data:
            self.enemies_to_spawn = []
            
            # wave_data is like [("MALWARE", 5, 1000), ("PHISHING", 2, 500)]
            for enemy_type, count, delay in wave_data:
                for _ in range(count):
                    self.enemies_to_spawn.append({"type": enemy_type, "delay": delay})
            
            self.wave_in_progress = True
            self.spawn_timer = 0
            self.wave_index += 1

    def update(self):
        if self.lives <= 0:
            self.game_over = True
            return

        if self.game_won:
            return

        current_time = pygame.time.get_ticks()
        dt_ms = current_time - self.last_update_time
        self.last_update_time = current_time
        
        if dt_ms > 100: dt_ms = 16 # Cap dt to prevent jumps
        
        game_dt = dt_ms * self.game_speed

        # Spawning
        if self.wave_in_progress and self.enemies_to_spawn:
            self.spawn_timer += game_dt
            next_enemy = self.enemies_to_spawn[0]
            delay = next_enemy["delay"]
            
            if self.spawn_timer > delay:
                enemy_data = self.enemies_to_spawn.pop(0)
                # Pass self.waypoints to Enemy
                self.enemies.append(Enemy(enemy_data["type"], self.waypoints))
                self.spawn_timer = 0
                
        elif self.wave_in_progress and not self.enemies_to_spawn and not self.enemies:
            self.wave_in_progress = False
            if self.mode == "STORY":
                if self.wave_index == len(self.waves):
                    self.level_complete = True
            # Endless Mode: Just waits for next wave, no level complete condition

        # Updates
        
        # Buff Expiration
        if "rate_boost" in self.active_buffs:
            if time.time() > self.active_buffs["rate_boost"]:
                del self.active_buffs["rate_boost"]

        # Loot Updates
        for loot in self.loot_drops[:]:
            if not loot.update():
                self.loot_drops.remove(loot)

        enemies_to_remove = []
        for enemy in self.enemies:
            # Apply global slow modifier
            enemy.move(self.game_speed * self.modifiers["enemy_slow"])
            if enemy.finished:
                self.lives -= 1
                enemies_to_remove.append(enemy)
            elif enemy.health <= 0:
                self.money += int(enemy.reward * self.modifiers["reward"])
                
                # Loot Drop Chance
                if random.random() < 0.2: # 20% chance
                    roll = random.random()
                    loot_type = None
                    if roll < LOOT_TYPES["PATCH"]["chance"]: loot_type = "PATCH"
                    elif roll < LOOT_TYPES["PATCH"]["chance"] + LOOT_TYPES["DATA_STREAM"]["chance"]: loot_type = "DATA_STREAM"
                    elif roll < LOOT_TYPES["PATCH"]["chance"] + LOOT_TYPES["DATA_STREAM"]["chance"] + LOOT_TYPES["CRYPTO"]["chance"]: loot_type = "CRYPTO"
                    
                    if loot_type:
                        self.loot_drops.append(LootDrop(enemy.x, enemy.y, loot_type))

                enemies_to_remove.append(enemy)
        
        for e in enemies_to_remove:
            if e in self.enemies:
                self.enemies.remove(e)

        # Towers
        tower_dt = (time.time() * 1000) - (self.last_tower_update if hasattr(self, 'last_tower_update') else time.time() * 1000)
        # Fix delta time logic: we need real dt in ms
        current_time = time.time()
        if not hasattr(self, 'last_tower_update'):
            self.last_tower_update = current_time
        
        # Calculate dt in milliseconds
        dt_ms = (current_time - self.last_tower_update) * 1000
        self.last_tower_update = current_time
        
        # Apply game speed to dt
        dt_ms *= self.game_speed

        rate_multiplier = 1.0
        if "rate_boost" in self.active_buffs:
             rate_multiplier = 2.0 # 100% faster (half delay)

        for tower in self.towers:
            projectile = tower.update(self.enemies, dt_ms, rate_multiplier)
            if projectile:
                self.projectiles.append(projectile)

        projectiles_to_remove = []
        for p in self.projectiles:
            p.move(self.game_speed)
            if not p.active:
                projectiles_to_remove.append(p)
        
        for p in projectiles_to_remove:
            if p in self.projectiles:
                self.projectiles.remove(p)

    def place_tower(self, tower_type, x, y):
        base_cost = TOWER_TYPES[tower_type]["cost"]
        cost = int(base_cost * self.modifiers["cost"])
        
        if self.money >= cost:
            t = Tower(tower_type, x, y)
            # Apply current modifiers
            t.damage *= self.modifiers["damage"]
            t.range *= self.modifiers["range"]
            t.rate *= self.modifiers["rate"]
            
            self.towers.append(t)
            self.money -= cost
            return True
        return False

    def sell_tower(self, x, y):
        # Find tower at x, y
        for tower in self.towers:
            # Simple distance check (assume ~20px radius click area)
            dist = ((tower.x - x)**2 + (tower.y - y)**2)**0.5
            if dist < 20:
                self.towers.remove(tower)
                refund = int(TOWER_TYPES[tower.type]["cost"] * 0.5)
                self.money += refund
                return True, refund
        return False, 0
        
    def draw_grid(self, screen):
        # Draw grid lines
        for x in range(0, MAP_WIDTH, GRID_SIZE):
            pygame.draw.line(screen, DARK_GRID, (x, 0), (x, MAP_HEIGHT))
        for y in range(0, MAP_HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, DARK_GRID, (0, y), (MAP_WIDTH, y))

    def draw(self, screen):
        # Background
        screen.fill(BLACK)
        self.draw_grid(screen)

        # Draw Path (Glow effect) using self.waypoints
        if len(self.waypoints) >= 2:
            # Outer Glow
            pygame.draw.lines(screen, (0, 50, 0), False, self.waypoints, 26)
            # Inner Path
            pygame.draw.lines(screen, (0, 100, 0), False, self.waypoints, 10)
            # Center Line
            pygame.draw.lines(screen, NEON_GREEN, False, self.waypoints, 2)

        # Draw Elements
        for tower in self.towers:
            tower.draw(screen)
            
        # Draw Loot
        for loot in self.loot_drops:
            loot.draw(screen)

        for enemy in self.enemies:
            enemy.draw(screen)

        for p in self.projectiles:
            p.draw(screen)
            
        # Draw Base
        if self.waypoints:
             bx, by = self.waypoints[-1]
             pygame.draw.circle(screen, NEON_GREEN, (bx, by), 20)
             pygame.draw.circle(screen, (0, 100, 0), (bx, by), 30, 2)
             
        # Buff Indicators
        if self.active_buffs:
             y_off = 100
             for buff, end_time in self.active_buffs.items():
                 remaining = int(end_time - time.time())
                 if remaining > 0:
                     font = pygame.font.SysFont("Arial", 20, bold=True)
                     txt = font.render(f"{buff.upper()}: {remaining}s", True, NEON_BLUE)
                     screen.blit(txt, (20, y_off))
                     y_off += 30
