import pygame
import sys
import textwrap
from src.constants import *
from src.game import Game
from src.enemy import draw_enemy_visual
from src.tower import draw_tower_visual

def draw_sidebar(screen, game, selected_tower, font_title, font_body):
    # Sidebar Background
    sidebar_width = SCREEN_WIDTH - MAP_WIDTH
    panel_width = sidebar_width - 20
    
    sidebar_rect = pygame.Rect(MAP_WIDTH, 0, sidebar_width, SCREEN_HEIGHT)
    pygame.draw.rect(screen, UI_BG, sidebar_rect)
    pygame.draw.line(screen, NEON_BLUE, (MAP_WIDTH, 0), (MAP_WIDTH, SCREEN_HEIGHT), 2)

    # Title
    title_surf = font_title.render("CODEBREAK", True, NEON_BLUE)
    screen.blit(title_surf, (MAP_WIDTH + 20, 20))
    subtitle_surf = font_body.render("CYBER DEFENSE", True, WHITE)
    screen.blit(subtitle_surf, (MAP_WIDTH + 20, 60))

    # Stats Panel
    y_offset = 120
    stats = [
        f"MONEY: ${game.money}",
        f"LIVES: {game.lives}",
        f"WAVE: {game.wave_index}/{len(game.waves)}"
    ]
    
    for stat in stats:
        pygame.draw.rect(screen, (30, 30, 40), (MAP_WIDTH + 10, y_offset - 5, panel_width, 35), border_radius=5)
        pygame.draw.rect(screen, NEON_BLUE, (MAP_WIDTH + 10, y_offset - 5, panel_width, 35), 1, border_radius=5)
        
        text = font_body.render(stat, True, NEON_GREEN)
        screen.blit(text, (MAP_WIDTH + 20, y_offset))
        y_offset += 50

    # Tower Selection
    y_offset += 20
    header = font_body.render("DEFENSES (R-Click Sell):", True, WHITE)
    screen.blit(header, (MAP_WIDTH + 20, y_offset))
    y_offset += 30

    tower_keys = ["FIREWALL", "ANTIVIRUS", "IDS", "HONEYPOT"]
    for i, key in enumerate(tower_keys):
        t_data = TOWER_TYPES[key]
        color = t_data["color"]
        
        # Selection Box Highlight
        if selected_tower == key:
            pygame.draw.rect(screen, color, (MAP_WIDTH + 10, y_offset - 10, panel_width, 60), 2, border_radius=5)
        
        # Tower Info
        name_text = font_body.render(f"[{i+1}] {t_data['name']}", True, color)
        cost_text = font_body.render(f"${t_data['cost']}", True, WHITE)
        
        screen.blit(name_text, (MAP_WIDTH + 20, y_offset))
        screen.blit(cost_text, (MAP_WIDTH + panel_width - 60, y_offset)) # Right align cost
        y_offset += 70

    # Global Abilities (Patch Management)
    pygame.draw.rect(screen, (50, 50, 60), (MAP_WIDTH + 10, y_offset, panel_width, 40), border_radius=5)
    patch_text = font_body.render("[P] PATCH SYSTEM", True, WHITE)
    cost_text = font_body.render("$500 (Heal 5 Lives)", True, NEON_YELLOW)
    screen.blit(patch_text, (MAP_WIDTH + 20, y_offset + 5))
    screen.blit(cost_text, (MAP_WIDTH + 20, y_offset + 25))

    # Speed Button
    speed_y = SCREEN_HEIGHT - 130
    pygame.draw.rect(screen, (50, 50, 60), (MAP_WIDTH + 20, speed_y, panel_width - 20, 40), border_radius=10)
    pygame.draw.rect(screen, NEON_BLUE, (MAP_WIDTH + 20, speed_y, panel_width - 20, 40), 2, border_radius=10)
    
    speed_label = f"SPEED: {int(game.game_speed)}x [S]"
    speed_surf = font_body.render(speed_label, True, NEON_BLUE)
    text_rect = speed_surf.get_rect(center=(MAP_WIDTH + 20 + (panel_width - 20)//2, speed_y + 20))
    screen.blit(speed_surf, text_rect)

    # Codex Button (New)
    codex_y = SCREEN_HEIGHT - 180
    pygame.draw.rect(screen, (30, 0, 30), (MAP_WIDTH + 20, codex_y, panel_width - 20, 40), border_radius=10)
    pygame.draw.rect(screen, NEON_PINK, (MAP_WIDTH + 20, codex_y, panel_width - 20, 40), 2, border_radius=10)
    
    codex_label = "OPEN CODEX [C]"
    codex_surf = font_body.render(codex_label, True, NEON_PINK)
    text_rect = codex_surf.get_rect(center=(MAP_WIDTH + 20 + (panel_width - 20)//2, codex_y + 20))
    screen.blit(codex_surf, text_rect)

    # Next Wave Button
    pygame.draw.rect(screen, NEON_PURPLE, (MAP_WIDTH + 20, SCREEN_HEIGHT - 80, panel_width - 20, 50), border_radius=10)
    wave_text = font_body.render("NEXT WAVE [SPACE]", True, WHITE)
    
    # Center text in button
    text_rect = wave_text.get_rect(center=(MAP_WIDTH + 20 + (panel_width - 20)//2, SCREEN_HEIGHT - 55))
    screen.blit(wave_text, text_rect)

def draw_story_panel(screen, game, font_title, font_body):
    # Overlay
    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 245)) # Dark overlay
    screen.blit(s, (0, 0))
    
    # Text Box
    box_rect = pygame.Rect(100, 100, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 200)
    pygame.draw.rect(screen, UI_BG, box_rect, border_radius=10)
    pygame.draw.rect(screen, NEON_BLUE, box_rect, 2, border_radius=10)
    
    # Title
    title = font_title.render(game.level_data["name"], True, NEON_BLUE)
    screen.blit(title, (140, 120))
    
    # Content
    story_lines = game.level_data["story"]
    y_off = 180
    
    # Use a medium font for story text if possible, otherwise use font_body (size 18)
    # Or create a local font
    story_font = pygame.font.SysFont("Consolas", 22)
    
    max_width_chars = 60 # Approx characters per line
    
    for line in story_lines:
        wrapped_lines = textwrap.wrap(line, width=max_width_chars)
        for wrapped_line in wrapped_lines:
            text = story_font.render(wrapped_line, True, NEON_GREEN)
            screen.blit(text, (140, y_off))
            y_off += 30
        y_off += 10 # Extra spacing between paragraphs
        
    # Instruction
    inst = font_body.render("PRESS [SPACE] TO INITIALIZE DEFENSE...", True, WHITE)
    # Pulsing effect or just static
    screen.blit(inst, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT - 150))

def draw_codex(screen, font_title, font_body, current_category=None):
    # Overlay
    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    s.fill((10, 10, 15, 250)) # Almost opaque background
    screen.blit(s, (0, 0))
    
    # Border
    pygame.draw.rect(screen, NEON_PINK, (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100), 2, border_radius=15)
    
    # Header
    title = font_title.render("SECURITY CODEX", True, NEON_PINK)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 70))
    
    # Close Hint
    hint = font_body.render("[ESC] CLOSE", True, WHITE)
    screen.blit(hint, (SCREEN_WIDTH - 180, 70))

    mx, my = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()[0]
    
    if current_category is None:
        # CATEGORY SELECTION
        cats = ["DEFENSES", "THREATS"]
        y = 200
        
        for cat in cats:
            rect = pygame.Rect(SCREEN_WIDTH//2 - 150, y, 300, 80)
            color = (40, 30, 40)
            border = NEON_BLUE
            
            if rect.collidepoint(mx, my):
                color = (60, 40, 60)
                border = NEON_PINK
                if click:
                    return cat # Select this category
            
            pygame.draw.rect(screen, color, rect, border_radius=10)
            pygame.draw.rect(screen, border, rect, 2, border_radius=10)
            
            text = font_title.render(cat, True, WHITE)
            screen.blit(text, (rect.centerx - text.get_width()//2, rect.centery - text.get_height()//2))
            
            y += 120
            
        return None

    else:
        # ITEM LIST + DETAILS
        # Left Panel: List
        pygame.draw.line(screen, NEON_PINK, (300, 120), (300, SCREEN_HEIGHT - 80), 2)
        
        items = list(CODEX_CONTENT[current_category].keys())
        y = 150
        
        selected_item = None
        
        # We need to store selection state, but for simplicity let's just use hover for now
        # or better, rely on mouse position for detail view
        
        hovered_item_key = None
        
        for key in items:
            rect = pygame.Rect(70, y, 210, 40)
            color = (0, 0, 0, 0) # Transparent
            text_color = (150, 150, 150)
            
            if rect.collidepoint(mx, my):
                text_color = NEON_BLUE
                hovered_item_key = key
            
            text = font_body.render(key, True, text_color)
            screen.blit(text, (80, y + 10))
            y += 50

        # Right Panel: Details
        if hovered_item_key:
            data = CODEX_CONTENT[current_category][hovered_item_key]
            
            # Title
            # Handle long titles by reducing font size or splitting
            title_text = data["title"]
            if len(title_text) > 30: # Check if title is very long
                 title_surf = pygame.font.SysFont("Consolas", 24, bold=True).render(title_text, True, NEON_GREEN)
            else:
                 title_surf = font_title.render(title_text, True, NEON_GREEN)
            
            screen.blit(title_surf, (340, 150))
            
            # Visual Preview
            preview_x = 900 # Move further right
            preview_y = 170
            
            if current_category == "THREATS":
                e_stats = ENEMY_TYPES[hovered_item_key]
                # Scale up visual for clarity
                draw_enemy_visual(screen, hovered_item_key, preview_x, preview_y, e_stats["radius"] * 1.5, e_stats["color"])
            elif current_category == "DEFENSES":
                t_stats = TOWER_TYPES[hovered_item_key]
                draw_tower_visual(screen, hovered_item_key, preview_x, preview_y, 60, 60, t_stats["color"])

            y_det = 230 # Start lower to avoid overlap
            
            # Description
            desc_lines = textwrap.wrap(data["desc"], width=60)
            for line in desc_lines:
                t = font_body.render(line, True, WHITE)
                screen.blit(t, (340, y_det))
                y_det += 25
            
            y_det += 20
            
            # Stats/Strengths
            if "strength" in data:
                s_txt = font_body.render(data["strength"], True, NEON_BLUE)
                screen.blit(s_txt, (340, y_det))
                y_det += 30
            if "weakness" in data:
                w_txt = font_body.render(data["weakness"], True, NEON_RED)
                screen.blit(w_txt, (340, y_det))
                y_det += 30
            if "counter" in data:
                c_txt = font_body.render(data["counter"], True, NEON_YELLOW)
                screen.blit(c_txt, (340, y_det))
                y_det += 30
                
            y_det += 20
            
            # Educational Content
            edu_lines = textwrap.wrap(data["edu"], width=58) # Reduced width to ensure it fits inside box padding
            # Calculate required height
            box_height = 45 + (len(edu_lines) * 25) + 20
            
            pygame.draw.rect(screen, (20, 30, 20), (340, y_det, 600, box_height), border_radius=10)
            pygame.draw.rect(screen, NEON_GREEN, (340, y_det, 600, box_height), 1, border_radius=10)
            
            edu_label = font_body.render("CYBER INTEL:", True, NEON_GREEN)
            screen.blit(edu_label, (360, y_det + 15))
            
            y_edu = y_det + 45
            for line in edu_lines:
                t = font_body.render(line, True, (200, 255, 200))
                screen.blit(t, (360, y_edu))
                y_edu += 25

        else:
             hint_text = font_body.render("HOVER OVER AN ITEM TO ANALYZE", True, (100, 100, 100))
             screen.blit(hint_text, (450, 300))
             
        # Back Button (Simulated by clicking outside list or pressing ESC handled by main loop)
        return current_category

def draw_perk_selection(screen, game, font_title, font_body):
    # Overlay
    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 220))
    screen.blit(s, (0, 0))
    
    # Header
    title = font_title.render("SYSTEM UPGRADE AVAILABLE", True, NEON_GREEN)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
    
    sub = font_body.render("SELECT A PROTOCOL ENHANCEMENT", True, WHITE)
    screen.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, 150))
    
    # Cards
    card_width = 250
    card_height = 350
    spacing = 50
    total_width = 3 * card_width + 2 * spacing
    start_x = (SCREEN_WIDTH - total_width) // 2
    y = 250
    
    mx, my = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()[0]
    
    for i, perk_key in enumerate(game.generated_perks):
        perk = PERK_TYPES[perk_key]
        x = start_x + i * (card_width + spacing)
        rect = pygame.Rect(x, y, card_width, card_height)
        
        # Hover Effect
        hovered = rect.collidepoint(mx, my)
        color = perk["color"]
        bg_color = (20, 20, 30)
        
        if hovered:
            bg_color = (40, 40, 50)
            pygame.draw.rect(screen, color, (x-2, y-2, card_width+4, card_height+4), border_radius=15)
            
            if click:
                game.apply_perk(perk_key)
                return # Done
        
        pygame.draw.rect(screen, bg_color, rect, border_radius=15)
        pygame.draw.rect(screen, color, rect, 2, border_radius=15)
        
        # Icon (Simple Circle for now)
        pygame.draw.circle(screen, color, (x + card_width//2, y + 80), 40, 2)
        initial = font_title.render(perk["name"][0], True, color)
        screen.blit(initial, (x + card_width//2 - initial.get_width()//2, y + 80 - initial.get_height()//2))
        
        # Text
        name_lines = textwrap.wrap(perk["name"], width=15)
        ny = y + 140
        for line in name_lines:
             n_txt = font_title.render(line, True, WHITE)
             screen.blit(n_txt, (x + card_width//2 - n_txt.get_width()//2, ny))
             ny += 35
             
        # Rarity
        r_txt = font_body.render(perk["rarity"], True, color)
        screen.blit(r_txt, (x + card_width//2 - r_txt.get_width()//2, y + 200))
        
        # Desc
        desc_lines = textwrap.wrap(perk["desc"], width=20)
        dy = y + 240
        for line in desc_lines:
            d_txt = font_body.render(line, True, (200, 200, 200))
            screen.blit(d_txt, (x + card_width//2 - d_txt.get_width()//2, dy))
            dy += 20

def draw_level_intel(screen, game, font_title, font_body):
    # Overlay
    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    s.fill((10, 10, 20, 252)) # Almost Opaque background
    screen.blit(s, (0, 0))
    
    # Border
    pygame.draw.rect(screen, NEON_BLUE, (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100), 2, border_radius=15)
    
    # Title
    title = font_title.render(f"INTEL: {game.level_data['name']}", True, NEON_BLUE)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 70))
    
    sub = font_body.render("INCOMING THREATS DETECTED - ANALYZING WEAKNESSES...", True, NEON_RED)
    screen.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, 110))
    
    # Get Intel
    intel = game.get_level_intel()
    
    y_start = 160
    col_width = 700
    x_left = SCREEN_WIDTH//2 - col_width//2
    
    for i, data in enumerate(intel):
        # Card Background
        card_rect = pygame.Rect(x_left, y_start, col_width, 90)
        pygame.draw.rect(screen, (30, 30, 40), card_rect, border_radius=10)
        pygame.draw.rect(screen, data["color"], card_rect, 2, border_radius=10)
        
        # Enemy Visual
        # Draw a small background for the visual
        pygame.draw.circle(screen, (10, 10, 10), (x_left + 60, y_start + 45), 30)
        draw_enemy_visual(screen, data["type"], x_left + 60, y_start + 45, data["radius"] * 1.5, data["color"])
        
        # Text Info
        # Name
        name_txt = pygame.font.SysFont("Consolas", 24, bold=True).render(data["name"], True, WHITE)
        screen.blit(name_txt, (x_left + 120, y_start + 15))
        
        # Effective Towers
        if data["effective"]:
            eff_str = "VULNERABLE TO: " + ", ".join(data["effective"])
            eff_color = NEON_GREEN
        else:
            eff_str = "NO SPECIFIC WEAKNESS (Use high damage)"
            eff_color = (200, 200, 200)
            
        eff_txt = font_body.render(eff_str, True, eff_color)
        screen.blit(eff_txt, (x_left + 120, y_start + 50))
        
        y_start += 110
        
    # Continue Prompt
    prompt = font_body.render("PRESS [SPACE] TO INITIATE DEFENSE PROTOCOLS", True, WHITE)
    screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT - 100))

def draw_main_menu(screen, font_title, font_body):
    screen.fill(BLACK)
    
    # Title
    title = font_title.render("CODEBREAK", True, NEON_BLUE)
    sub = font_body.render("CYBER DEFENSE PROTOCOL", True, NEON_GREEN)
    
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
    screen.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, 200))
    
    # Buttons
    mx, my = pygame.mouse.get_pos()
    click = False
    if pygame.mouse.get_pressed()[0]:
        click = True
    
    options = ["STORY MODE", "ENDLESS MODE", "QUIT"]
    clicked_option = None
    
    y = 350
    for opt in options:
        rect = pygame.Rect(SCREEN_WIDTH//2 - 100, y, 200, 50)
        
        color = (50, 50, 60)
        border = NEON_BLUE
        
        if rect.collidepoint(mx, my):
            color = (70, 70, 80)
            border = NEON_PINK
            if click:
                clicked_option = opt
        
        pygame.draw.rect(screen, color, rect, border_radius=10)
        pygame.draw.rect(screen, border, rect, 2, border_radius=10)
        
        text = font_body.render(opt, True, WHITE)
        screen.blit(text, (rect.centerx - text.get_width()//2, rect.centery - text.get_height()//2))
        
        y += 70
        
    return clicked_option

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("CodeBreak: Cyber Defense Simulator")
    clock = pygame.time.Clock()
    
    font_title = pygame.font.SysFont("Consolas", 32, bold=True)
    font_body = pygame.font.SysFont("Consolas", 18)
    
    state = "MENU" # MENU, GAME, CODEX
    codex_category = None
    game = None
    selected_tower = "FIREWALL"
    showing_story = False
    showing_intel = False
    
    running = True
    while running:
        # Check Loot Collection (Mouse Hover)
        mx, my = pygame.mouse.get_pos()
        if game and not game.game_over and not game.game_won and not showing_story and not showing_intel:
            game.check_loot_collection(mx, my)

        # Event Handling
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        
        if state == "MENU":
            clicked = draw_main_menu(screen, font_title, font_body)
            if clicked == "STORY MODE":
                game = Game(mode="STORY")
                state = "GAME"
                showing_story = True
                showing_intel = False
                pygame.time.wait(150)
            elif clicked == "ENDLESS MODE":
                game = Game(mode="ENDLESS")
                state = "GAME"
                showing_story = True
                showing_intel = False
                pygame.time.wait(150)
            elif clicked == "QUIT":
                running = False
                
            pygame.display.flip()
            clock.tick(FPS)
            continue
            
        elif state == "CODEX":
            # Draw game background faintly if paused
            if game:
                game.draw(screen)
                draw_sidebar(screen, game, selected_tower, font_title, font_body)
            else:
                screen.fill(BLACK)
                
            # Draw Codex Overlay
            new_cat = draw_codex(screen, font_title, font_body, codex_category)
            if new_cat:
                codex_category = new_cat
            
            # Input Handling for Codex
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if codex_category is not None:
                            codex_category = None # Go back to category list
                        else:
                            state = "GAME" if game else "MENU" # Close Codex
            
            pygame.display.flip()
            clock.tick(FPS)
            continue

        # GAME STATE
        
        # Perk Selection Screen (Blocks Game Loop)
        if game.pending_perk_choice:
            game.draw(screen)
            draw_sidebar(screen, game, selected_tower, font_title, font_body)
            draw_perk_selection(screen, game, font_title, font_body)
            
            # Handle basic events like Quit
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                    
            pygame.display.flip()
            clock.tick(FPS)
            continue

        # Handle Input
        for event in events:
            if showing_story:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    showing_story = False
                    showing_intel = True
                continue

            if showing_intel:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    showing_intel = False
                continue
            
            if game.level_complete:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game.load_level(game.level_index + 1)
                    if not game.game_won: 
                        showing_story = True
                        showing_intel = False
                continue
                
            if game.game_won or game.game_over:
                 # Press ESC to return to menu
                 if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                     state = "MENU"
                 continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: selected_tower = "FIREWALL"
                elif event.key == pygame.K_2: selected_tower = "ANTIVIRUS"
                elif event.key == pygame.K_3: selected_tower = "IDS"
                elif event.key == pygame.K_4: selected_tower = "HONEYPOT"
                elif event.key == pygame.K_SPACE: game.start_next_wave()
                elif event.key == pygame.K_s: 
                        if game.game_speed == 1.0: game.game_speed = 2.0
                        elif game.game_speed == 2.0: game.game_speed = 4.0
                        else: game.game_speed = 1.0
                elif event.key == pygame.K_c: 
                    state = "CODEX"
                    codex_category = None
                elif event.key == pygame.K_p:
                    if game.money >= 500:
                        game.money -= 500
                        game.lives += 5
                        if game.lives > STARTING_LIVES: game.lives = STARTING_LIVES
                elif event.key == pygame.K_ESCAPE:
                    state = "MENU"
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left Click
                    if mx < MAP_WIDTH:
                        game.place_tower(selected_tower, mx, my)
                    else:
                        if SCREEN_HEIGHT - 60 < my < SCREEN_HEIGHT - 20:
                            game.start_next_wave()
                        if SCREEN_HEIGHT - 110 < my < SCREEN_HEIGHT - 70:
                            if game.game_speed == 1.0: game.game_speed = 2.0
                            elif game.game_speed == 2.0: game.game_speed = 4.0
                            else: game.game_speed = 1.0
                        if SCREEN_HEIGHT - 160 < my < SCREEN_HEIGHT - 120: # Codex Button
                            state = "CODEX"
                            codex_category = None
                        if 600 < my < 650: 
                                if game.money >= 500:
                                    game.money -= 500
                                    game.lives += 5
                                    if game.lives > STARTING_LIVES: game.lives = STARTING_LIVES
                elif event.button == 3: # Right Click
                    if mx < MAP_WIDTH:
                        game.sell_tower(mx, my)

        # Render Logic
        if showing_story:
            game.draw(screen) 
            draw_story_panel(screen, game, font_title, font_body) 
            pygame.display.flip()
            clock.tick(FPS)
            continue
            
        if showing_intel:
            game.draw(screen)
            draw_level_intel(screen, game, font_title, font_body)
            pygame.display.flip()
            clock.tick(FPS)
            continue

        if game.level_complete:
            game.draw(screen)
            draw_sidebar(screen, game, selected_tower, font_title, font_body)
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 200))
            screen.blit(s, (0,0))
            text = font_title.render("LEVEL COMPLETE", True, NEON_GREEN)
            screen.blit(text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 50))
            sub = font_body.render("PRESS [SPACE] TO PROCEED", True, WHITE)
            screen.blit(sub, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 20))
            pygame.display.flip()
            clock.tick(FPS)
            continue

        if not game.game_over and not game.game_won:
            game.update()
        
        game.draw(screen)
        
        # Hover Range
        if mx < MAP_WIDTH and not game.game_over and not game.game_won:
            range_val = TOWER_TYPES[selected_tower]["range"]
            color = TOWER_TYPES[selected_tower]["color"]
            s = pygame.Surface((range_val*2, range_val*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*color, 50), (range_val, range_val), range_val)
            pygame.draw.circle(s, (*color, 150), (range_val, range_val), range_val, 1)
            screen.blit(s, (mx - range_val, my - range_val))
            pygame.draw.circle(screen, color, (mx, my), 5)

        draw_sidebar(screen, game, selected_tower, font_title, font_body)

        if game.game_over:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 200))
            screen.blit(s, (0,0))
            text = font_title.render("SYSTEM COMPROMISED", True, NEON_RED)
            screen.blit(text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2))
            sub = font_body.render("PRESS [ESC] FOR MENU", True, WHITE)
            screen.blit(sub, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 40))
            
        elif game.game_won:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 200))
            screen.blit(s, (0,0))
            text = font_title.render("MISSION ACCOMPLISHED", True, NEON_GREEN)
            sub = font_body.render("ALL THREATS ELIMINATED.", True, WHITE)
            screen.blit(text, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 50))
            screen.blit(sub, (SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 + 20))
            sub2 = font_body.render("PRESS [ESC] FOR MENU", True, WHITE)
            screen.blit(sub2, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 60))
            
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
