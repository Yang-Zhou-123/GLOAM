import pygame
from pathlib import Path

class Player:
    def __init__(self, x, y):
        # Set the starting position, size and movement speed
        self.x = x
        self.y = y
        self.size = 40
        self.speed = 5

        # Set health and the damage cooldown
        self.max_health = 3
        self.health = self.max_health
        self.hit_cooldown = 1000
        self.last_hit_time = pygame.time.get_ticks() - self.hit_cooldown

        # Set attack damage and range
        self.damage = 1
        self.attack_range = 150

        # Store the attack effect's position, radius and end time
        self.attack_center = (0, 0)
        self.attack_effect_radius = self.attack_range
        self.attack_effect_end_time = 0

        # Track the visible flashing effect separately from damage protection
        self.hurt_flash_end_time = 0

        # Load the walking sprite sheet
        walk_path = Path(__file__).parent / "images" / "main_character_walk_iceblue.png"
        sheet = pygame.image.load(str(walk_path)).convert_alpha()

        columns = 4
        rows = 2
        frame_width = sheet.get_width() // columns
        frame_height = sheet.get_height() // rows

        # Apply the same scale to every frame to preserve relative sizes
        display_height = 100
        display_width = max(
            1, round(frame_width * display_height / frame_height)
        )

        self.walk_right = []
        self.walk_left = []

        for row in range(rows):
            for column in range(columns):
                frame_rect = pygame.Rect(
                    column * frame_width,
                    row * frame_height,
                    frame_width,
                    frame_height
                )
                frame = sheet.subsurface(frame_rect).copy()
                frame = pygame.transform.scale(
                    frame, (display_width, display_height)
                )

                if row == 0:
                    self.walk_right.append(frame)
                else:
                    self.walk_left.append(frame)

        # Use the first walking frame as the idle image
        self.image_right = self.walk_right[0]
        self.image_left = self.walk_left[0]
        self.image = self.image_right

        # Track animation direction, frame and timing
        self.facing = "right"
        self.walk_frame_index = 0
        self.walk_frame_duration = 120
        self.last_frame_time = pygame.time.get_ticks()
        self.was_moving = False

        # Load the attack sprite sheet
        effect_path = (
            Path(__file__).parent / "images" / "attack_effect2.png"
        )
        sheet = pygame.image.load(str(effect_path)).convert_alpha()

        frame_width = sheet.get_width() // 4
        frame_height = sheet.get_height() // 2

        self.attack_frames = []

        # Read the top row first, then the bottom row
        for row in range(2):
            for column in range(4):
                rect = pygame.Rect(
                    column * frame_width,
                    row * frame_height,
                    frame_width,
                    frame_height
                )
                frame = sheet.subsurface(rect).copy()
                self.attack_frames.append(frame)

        # Set animation timing
        self.attack_frame_duration = 60
        self.attack_animation_start = None
        self.attack_display_frames = []

        # Load six character attack poses separately from the spell effect
        pose_path = Path(__file__).parent / "images" / "player_attack.png"
        pose_sheet = pygame.image.load(str(pose_path)).convert_alpha()
        pose_width = pose_sheet.get_width() // 3
        pose_height = pose_sheet.get_height() // 2
        pose_display_height = 100
        pose_display_width = max(
            1, round(pose_width * pose_display_height / pose_height)
        )
        self.attack_pose_right = []
        self.attack_pose_left = []

        for row in range(2):
            for column in range(3):
                rect = pygame.Rect(
                    column * pose_width, row * pose_height,
                    pose_width, pose_height
                )
                frame = pose_sheet.subsurface(rect).copy()
                frame = pygame.transform.scale(
                    frame, (pose_display_width, pose_display_height)
                )
                self.attack_pose_right.append(frame)
                self.attack_pose_left.append(
                    pygame.transform.flip(frame, True, False)
                )

        # Lock the facing direction for the duration of an attack
        self.attack_pose_start = None
        self.attack_pose_duration = 80
        self.attack_facing = "right"

    def is_attacking(self):
        if self.attack_pose_start is None:
            return False
        elapsed_time = pygame.time.get_ticks() - self.attack_pose_start
        return elapsed_time < (
            len(self.attack_pose_right) * self.attack_pose_duration
        )

    def move(self, keys, world):
        # Move only while the player is alive
        if self.health <= 0:
            return

        # Stay still until the attack action finishes
        if self.is_attacking():
            self.was_moving = False
            return

        old_x = self.x
        old_y = self.y

        dx = 0
        dy = 0

        # Calculate movement without changing the position directly
        if keys[pygame.K_w]:
            dy -= self.speed
        if keys[pygame.K_s]:
            dy += self.speed
        if keys[pygame.K_a]:
            dx -= self.speed
            self.facing = "left"
        if keys[pygame.K_d]:
            dx += self.speed
            self.facing = "right"

        # Let the world check collisions before changing the position
        world.move(self, dx, dy)

        # Keep your existing animation code below this line
        moving = self.x != old_x or self.y != old_y

        current_time = pygame.time.get_ticks()

        if moving:
            # Start from the first frame when movement begins
            if not self.was_moving:
                self.walk_frame_index = 0
                self.last_frame_time = current_time

            # Advance the animation every 120 milliseconds
            elif current_time - self.last_frame_time >= self.walk_frame_duration:
                self.walk_frame_index = (
                    self.walk_frame_index + 1
                ) % len(self.walk_right)
                self.last_frame_time = current_time

            if self.facing == "right":
                self.image = self.walk_right[self.walk_frame_index]
            else:
                self.image = self.walk_left[self.walk_frame_index]

        else:
            # Return to the standing image when movement stops
            if self.facing == "right":
                self.image = self.image_right
            else:
                self.image = self.image_left

        self.was_moving = moving

    def get_rect(self):
        # Return a rectangle at the player's current position
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def draw(self, screen, camera_x=0, camera_y=0):
        current_time = pygame.time.get_ticks()

        # Alternate between visible and hidden every 100 milliseconds
        if self.health > 0 and current_time < self.hurt_flash_end_time:
            elapsed_time = current_time - self.last_hit_time

            if (elapsed_time // 100) % 2 == 1:
                return

        # Give attack poses priority over the walk and idle image
        image = self.image
        if self.health > 0 and self.is_attacking():
            elapsed_time = current_time - self.attack_pose_start
            frame_index = elapsed_time // self.attack_pose_duration
            if self.attack_facing == "right":
                image = self.attack_pose_right[frame_index]
            else:
                image = self.attack_pose_left[frame_index]

        # Keep the same foot anchor for every animation
        screen_rect = self.get_rect().move(-camera_x, -camera_y)
        image_rect = image.get_rect(midbottom=screen_rect.midbottom)
        screen.blit(image, image_rect)

    def take_damage(self, damage):
        # Ignore damage if the player is already dead
        if self.health <= 0:
            return False

        current_time = pygame.time.get_ticks()

        # Allow damage only after the cooldown has ended
        if current_time - self.last_hit_time >= self.hit_cooldown:
            self.health = max(0, self.health - damage)
            self.last_hit_time = current_time

            # Flash during the damage protection period
            self.hurt_flash_end_time = current_time + self.hit_cooldown

            return True

        return False

    def attack(self, enemies):
        # Apply damage only once per completed attack action
        if self.health <= 0 or self.is_attacking():
            return

        self.attack_pose_start = pygame.time.get_ticks()
        self.attack_facing = self.facing
        if self.facing == "right":
            self.image = self.image_right
        else:
            self.image = self.image_left

        # Store the attack effect at the player's current centre
        self.attack_center = (
            self.x + self.size / 2,
            self.y + self.size / 2
        )
        self.attack_effect_radius = self.attack_range
        # Start the animation and size it to the current attack range
        self.attack_animation_start = pygame.time.get_ticks()

        diameter = round(self.attack_range * 2)
        self.attack_display_frames = []

        for frame in self.attack_frames:
            resized_frame = pygame.transform.scale(
                frame, (diameter, diameter)
            )
            self.attack_display_frames.append(resized_frame)

        # Hit enemies when their collision box overlaps the attack range
        for enemy in enemies:
            if enemy.health > 0:
                enemy_rect = enemy.get_rect()

                # Find the point on the enemy closest to the attack centre
                closest_x = max(
                    enemy_rect.left,
                    min(self.attack_center[0], enemy_rect.right)
                )
                closest_y = max(
                    enemy_rect.top,
                    min(self.attack_center[1], enemy_rect.bottom)
                )

                distance_squared = (
                    (closest_x - self.attack_center[0]) ** 2
                    + (closest_y - self.attack_center[1]) ** 2
                )

                if distance_squared <= self.attack_range ** 2:
                    enemy.take_damage(self.damage)

    def draw_attack_effect(self, screen, camera_x=0, camera_y=0):
        if self.attack_animation_start is None:
            return

        # Calculate which frame to display
        elapsed_time = (
            pygame.time.get_ticks() - self.attack_animation_start
        )
        frame_index = elapsed_time // self.attack_frame_duration

        # Stop after all frames have played once
        if frame_index >= len(self.attack_display_frames):
            self.attack_animation_start = None
            return

        frame = self.attack_display_frames[frame_index]

        # Convert the attack position from map to screen coordinates
        effect_rect = frame.get_rect(
            center=(
                round(self.attack_center[0] - camera_x),
                round(self.attack_center[1] - camera_y)
            )
        )
        screen.blit(frame, effect_rect)
    