import pygame
from enemy import Enemy, Boss
from player import Player
import random
from pathlib import Path
from world import World
from portal import Portal
from opening import show_opening
from ending import show_ending, show_boss_defeated

pygame.init()

# Set up the display (full screen) 
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

pygame.display.set_caption("GLOAM")

if not show_opening(screen):
    pygame.quit()
    raise SystemExit

# Load the background after creating the display
background_path = Path(__file__).parent / "images" / "01map4.png"
background = pygame.image.load(str(background_path)).convert()

# Display the map at half its original size
map_scale = 0.817
original_width, original_height = background.get_size()

background = pygame.transform.scale(
    background,
    (
        round(original_width * map_scale),
        round(original_height * map_scale)
    )
)

# Use the scaled image as the world size
map_width, map_height = background.get_size()
screen_width, screen_height = screen.get_size()

# Keep both maps at exactly the same world size
normal_background = background

hard_path = Path(__file__).parent / "images" / "02map1.png"
hard_background = pygame.image.load(str(hard_path)).convert()
hard_background = pygame.transform.scale(
    hard_background, (map_width, map_height)
)

# Stage 1 is the normal encounter; stage 2 is the enraged boss
stage = 1

# Place the portal near the rune circle in the top-right clearing
portal = Portal(
    int(map_width * 0.80),
    int(map_height * 0.18)
)

world = World(map_width, map_height)
# Start on the open ground near the bottom centre
spawn_x = int(map_width * 0.50) - 20
spawn_y = int(map_height * 0.85) - 40

camera_x = 0
camera_y = 0

# Create the player with its starting attributes
player = Player(spawn_x, spawn_y)


def create_enemy_wave(wave):
    # Spawn enemies on the open ground
    if wave == 1:
        return [
            Enemy(int(map_width * 0.50), int(map_height * 0.55))
        ]

    elif wave == 2:
        small_enemy = Enemy(
            int(map_width * 0.50), int(map_height * 0.40)
        )

        elite = Enemy(
            int(map_width * 0.65), int(map_height * 0.35)
        )
        elite.health = 5
        elite.max_health = 5
        elite.size = 50

        return [small_enemy, elite]

    elif wave == 3:
        return [
            Boss(int(map_width * 0.78), int(map_height * 0.16))
        ]

    return []

# start the first wave
wave = 1
max_waves = 3
victory = False
enemies = create_enemy_wave(wave)


# Create a clock object to control the frame rate
clock = pygame.time.Clock()

# Control whether the game keeps running
running = True

# create a font object for displaying text
font = pygame.font.Font(None, 72)
hud_font = pygame.font.Font(None, 36)

# track weather theplayer is choosing an upgrade
choosing_upgrade = False

# store each upgrade's effect and display text
upgrade_pool = [
    ("damage", "Attack damage +1"),
    ("speed", "Movement speed +1"),
    ("heal", "Restore 1 health"),
    ("max_health", "Max health +1 and restore 1 health"),
    ("range", "Attack range +20")
]

upgrade_choices = []

# Match each upgrade identifier to its card image
upgrade_card_files = {
    "damage": "attack.png",
    "speed": "speed.png",
    "heal": "health.png",
    "max_health": "max_health.png",
    "range": "attack_range.png"
}

# Size three cards to fit the screen
card_gap = max(12, round(screen_width * 0.025))
card_width = min(300, (screen_width - 4 * card_gap) // 3)
card_height = round(card_width * 1.16)

# Limit height on shorter screens
if card_height > screen_height * 0.65:
    card_height = int(screen_height * 0.65)
    card_width = round(card_height / 1.16)

upgrade_card_images = {}

for upgrade_id, filename in upgrade_card_files.items():
    image_path = Path(__file__).parent / "images" / filename
    image = pygame.image.load(str(image_path)).convert_alpha()

    upgrade_card_images[upgrade_id] = pygame.transform.scale(
        image, (card_width, card_height)
    )

# Prepare a dark overlay behind the menu
upgrade_overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
upgrade_overlay.fill((0, 0, 0, 170))

card_key_font = pygame.font.Font(
    None, max(20, round(card_width * 0.12))
)

while running:

    # When user presses the escape key
    # or clicks the close button, we want to exit the game

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            # Handle upgrade selection after waves 1 and 2
            elif choosing_upgrade:
                choice_index = None

                if event.key == pygame.K_1:
                    choice_index = 0
                elif event.key == pygame.K_2:
                    choice_index = 1
                elif event.key == pygame.K_3:
                    choice_index = 2

                if choice_index is not None:
                    upgrade_id, description = upgrade_choices[choice_index]

                    if upgrade_id == "damage":
                        player.damage += 1
                    elif upgrade_id == "speed":
                        player.speed += 1
                    elif upgrade_id == "heal":
                        player.health = min(
                            player.health + 1, player.max_health
                        )
                    elif upgrade_id == "max_health":
                        player.max_health += 1
                        player.health += 1
                    elif upgrade_id == "range":
                        player.attack_range += 20

                    print("Upgrade:", description)

                    # Open the portal after the upgrade has been selected
                    choosing_upgrade = False
                    upgrade_choices = []
                    portal.activate()

            # Enter the harder stage after clearing the normal encounter
            elif event.key == pygame.K_e:
                if stage == 1 and player.health > 0 and not victory:
                    if portal.is_ready() and portal.player_nearby(player):
                        stage = 2
                        background = hard_background
                        portal.deactivate()

                        # Keep all upgrades and remaining health
                        player.x = spawn_x
                        player.y = spawn_y

                        # Clear temporary animation effects from the old stage
                        player.attack_pose_start = None
                        player.attack_animation_start = None
                        player.attack_display_frames = []
                        player.hurt_flash_end_time = 0
                        player.was_moving = False
                        player.walk_frame_index = 0

                        if player.facing == "right":
                            player.image = player.image_right
                        else:
                            player.image = player.image_left

                        # Give the player one second of protection
                        player.last_hit_time = pygame.time.get_ticks()

                        # Spawn only the enraged boss
                        enemies = [
                            Boss(
                                int(map_width * 0.78),
                                int(map_height * 0.16),
                                enraged=True
                            )
                        ]

            elif event.key == pygame.K_SPACE:
                if player.health > 0 and not victory:
                    player.attack(enemies)

            elif event.key == pygame.K_r:
                if player.health <= 0 or victory:
                    player = Player(spawn_x, spawn_y)
                    # Restart from the normal stage
                    stage = 1
                    background = normal_background
                    wave = 1
                    victory = False
                    choosing_upgrade = False
                    upgrade_choices = []
                    enemies = create_enemy_wave(wave)
                    portal.deactivate()

    # Move the player while gameplay is active
    if player.health > 0 and not victory and not choosing_upgrade:
        keys = pygame.key.get_pressed()
        player.move(keys, world)

    # Move enemies through the map collision system
    if player.health > 0 and not victory and not choosing_upgrade:
        for enemy in enemies:
            if enemy.health > 0:
                enemy.move_towards_player(
                    player.x, player.y, world
                )

    # Get the player's current collision rectangle
    player_rect = player.get_rect()

    # damage the player when touching the enemy ny checking collision
    if player.health > 0 and not victory and not choosing_upgrade:
        for enemy in enemies:
            # check if the enemy is alive and collides with the player
            if enemy.health > 0 and player_rect.colliderect(enemy.get_rect()):
                # Stop checking after damage is successfully applied
                if player.take_damage(1):
                    print("Health:", player.health)

                    if player.health <= 0:
                        print("Game Over!")

                    break

    # Handle completion separately for the normal and harder stages
    if (
        player.health > 0
        and not victory
        and not choosing_upgrade
        and not portal.active
    ):
        wave_cleared = all(enemy.health <= 0 for enemy in enemies)

        if wave_cleared:
            if stage == 2:
                # Defeating the enraged boss completes the game
                victory = True

            elif wave < max_waves:
                # Continue the normal encounter
                wave += 1
                enemies = create_enemy_wave(wave)
                player.last_hit_time = pygame.time.get_ticks()

            else:
                # Offer one upgrade before opening the portal
                choosing_upgrade = True
                upgrade_choices = random.sample(upgrade_pool, 3)

    if victory:
        # Show the defeat message before the ending image
        if not show_boss_defeated(screen):
            running = False
            break

        action = show_ending(screen)

        if action == "quit":
            running = False
            break

        if action == "menu":
            if not show_opening(screen):
                running = False
                break

        # Restart from the normal stage after R or Start Game
        player = Player(spawn_x, spawn_y)
        stage = 1
        background = normal_background
        wave = 1
        victory = False
        choosing_upgrade = False
        upgrade_choices = []
        enemies = create_enemy_wave(wave)
        portal.deactivate()

        # Begin a fresh game-loop iteration
        continue

    # Follow the player's centre without showing outside the map
    camera_x = int(max(
        0,
        min(
            player.x + player.size / 2 - screen_width / 2,
            map_width - screen_width
        )
    ))
    camera_y = int(max(
        0,
        min(
            player.y + player.size / 2 - screen_height / 2,
            map_height - screen_height
        )
    ))

    # Offset the map by the camera position
    screen.blit(background, (-camera_x, -camera_y))

    # Draw the exit relative to the camera
    portal.draw(screen, camera_x, camera_y)

    # Draw the attack animation before the player
    player.draw_attack_effect(screen, camera_x, camera_y)

    # Draw the player
    player.draw(screen, camera_x, camera_y)

    # Draw every living enemy
    for enemy in enemies:
        enemy.draw(screen, camera_x, camera_y)
        enemy.draw_health_bar(screen, camera_x, camera_y)

    # Draw the player's health bar
    pygame.draw.rect(screen, (80, 80, 80), (20, 20, 150, 20))

    # calculate the width of health bar
    health_bar_width = 150 * (player.health / player.max_health)

    # Draw the current health bar
    pygame.draw.rect(
        screen,
        (200, 60, 60),
        (20, 20, int(health_bar_width), 20)
    )

    # display the "Game Over" message in the centre of the screen
    if player.health <= 0:
        text = font.render("Game Over", True, (255, 255, 255))
        text_rect = text.get_rect(center = screen.get_rect().center)
        # Draw the text using the top-left position of text_rect
        screen.blit(text, text_rect)

    # Display the restart hint below Game Over
        hint = hud_font.render(
            "Press R to restart", True, (255, 255, 255)
        )
        hint_rect = hint.get_rect(
            midtop=(text_rect.centerx, text_rect.bottom + 20)
        )
        screen.blit(hint, hint_rect)

    if stage == 1:
        status_text = f"Wave {wave}/{max_waves}"
    else:
        status_text = "ENRAGED BOSS"

    wave_text = hud_font.render(
        status_text, True, (255, 255, 255)
    )
    screen.blit(wave_text, (20, 50))

    # Show an interaction prompt when the player approaches the open portal
    if (
        player.health > 0
        and not victory
        and not choosing_upgrade
        and portal.is_ready()
        and portal.player_nearby(player)
    ):
        prompt = hud_font.render(
            "Press E to enter", True, (255, 245, 220)
        )
        prompt_rect = prompt.get_rect(
            midbottom=(screen_width // 2, screen_height - 40)
        )
        screen.blit(prompt, prompt_rect)

    # Display three randomly selected upgrade cards
    if choosing_upgrade:
        screen.blit(upgrade_overlay, (0, 0))

        total_width = card_width * 3 + card_gap * 2
        start_x = (screen_width - total_width) // 2
        start_y = (screen_height - card_height) // 2

        # Draw the title above the cards
        title = hud_font.render(
            "Choose an upgrade", True, (255, 245, 220)
        )
        title_rect = title.get_rect(
            midbottom=(screen_width // 2, start_y - 20)
        )
        screen.blit(title, title_rect)

        button_y = start_y + round(card_height * 0.76)

        for index, upgrade in enumerate(upgrade_choices):
            upgrade_id, description = upgrade

            card_x = start_x + index * (card_width + card_gap)
            card_rect = pygame.Rect(
                card_x, start_y, card_width, card_height
            )

            # Draw the image matching the actual upgrade
            screen.blit(
                upgrade_card_images[upgrade_id],
                card_rect
            )

            # Place the correct key number in the card's empty button
            key_text = card_key_font.render(
                f"Press {index + 1}", True, (255, 245, 220)
            )

            key_rect = key_text.get_rect(
                center=(card_rect.centerx, button_y)
            )
            screen.blit(key_text, key_rect)

    # Update the display
    pygame.display.flip()

    # limit the game to 60 frames per second to conttol move speed
    clock.tick(60)

# Quit Pygame
pygame.quit()