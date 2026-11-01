import pygame
from pathlib import Path

class Enemy:
    # Share decoded and resized sprites between enemies
    _source_frames = None
    _sprite_cache = {}

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 2
        self.health= 3
        self.max_health = self.health
        self.size = 40
        # store when the damage flash should end
        self.flash_end_time = 0
        # Store a temporary direction for moving around obstacles
        self.detour_direction = pygame.Vector2(0, 0)
        self.detour_end_time = 0

        # Advance walking frames only when the enemy actually moves
        self.facing = "left"
        self.walk_frame_index = 0
        self.walk_frame_duration = 120
        self.last_frame_time = pygame.time.get_ticks()
        self.last_draw_position = (self.x, self.y)
        self.was_moving = False

    def move_towards_player(self, player_x, player_y, world):
        if self.health <= 0:
            return

        current_time = pygame.time.get_ticks()

        # Temporarily move sideways after hitting an obstacle
        if current_time < self.detour_end_time:
            old_x = self.x
            old_y = self.y

            world.move(
                self,
                self.detour_direction.x * self.speed,
                self.detour_direction.y * self.speed
            )

            # Try the opposite direction if this side is also blocked
            if self.x == old_x and self.y == old_y:
                self.detour_direction = -self.detour_direction

                world.move(
                    self,
                    self.detour_direction.x * self.speed,
                    self.detour_direction.y * self.speed
                )

            return

        # Find the direction towards the player
        direction = pygame.Vector2(
            player_x - self.x,
            player_y - self.y
        )

        if direction.length() == 0:
            return

        direction = direction.normalize()

        old_x = self.x
        old_y = self.y

        # Try moving directly towards the player
        world.move(
            self,
            direction.x * self.speed,
            direction.y * self.speed
        )

        movement = pygame.Vector2(self.x - old_x, self.y - old_y)

        # If movement is mostly blocked, move sideways for 0.7 seconds
        if movement.length() < self.speed * 0.5:
            self.detour_direction = pygame.Vector2(
                -direction.y,
                direction.x
            )
            self.detour_end_time = current_time + 700

    def get_rect(self):
        # return a rectangale at the enemy's current position
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def take_damage(self, damage):
        # apply damage and briefly flash white
        if self.health > 0:
            self.health -= damage
            self.flash_end_time = pygame.time.get_ticks() + 120 # 0.12 seconds

    def get_sprite_frames(self):
        # The supplied sheet contains four left-facing poses in one row
        if Enemy._source_frames is None:
            path = Path(__file__).parent / "images" / "enemy_walk1.png"
            sheet = pygame.image.load(str(path)).convert_alpha()
            frame_width = sheet.get_width() // 4
            Enemy._source_frames = [
                sheet.subsurface(pygame.Rect(
                    index * frame_width, 0, frame_width, sheet.get_height()
                )).copy()
                for index in range(4)
            ]

        # Keep the elite visually larger without changing collision sizes
        display_height = round(self.size * 2.5)
        if display_height not in Enemy._sprite_cache:
            original = Enemy._source_frames[0]
            display_width = max(1, round(
                original.get_width() * display_height / original.get_height()
            ))
            left_frames = []
            right_frames = []
            white_left = []
            white_right = []
            for source in Enemy._source_frames:
                left = pygame.transform.scale(
                    source, (display_width, display_height)
                )
                right = pygame.transform.flip(left, True, False)
                flash = left.copy()
                # Make RGB white while preserving the original transparency
                flash.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_MAX)
                left_frames.append(left)
                right_frames.append(right)
                white_left.append(flash)
                white_right.append(pygame.transform.flip(flash, True, False))
            Enemy._sprite_cache[display_height] = (
                left_frames, right_frames, white_left, white_right
            )
        return Enemy._sprite_cache[display_height]

    def draw(self, screen, camera_x=0, camera_y=0):
        if self.health <= 0:
            return

        current_time = pygame.time.get_ticks()
        dx = self.x - self.last_draw_position[0]
        dy = self.y - self.last_draw_position[1]
        moving = abs(dx) > 0.001 or abs(dy) > 0.001
        if dx < -0.001:
            self.facing = "left"
        elif dx > 0.001:
            self.facing = "right"

        if moving:
            if not self.was_moving:
                self.last_frame_time = current_time
            elif current_time - self.last_frame_time >= self.walk_frame_duration:
                self.walk_frame_index = (self.walk_frame_index + 1) % 4
                self.last_frame_time = current_time
        else:
            self.walk_frame_index = 0

        self.last_draw_position = (self.x, self.y)
        self.was_moving = moving

        left, right, white_left, white_right = self.get_sprite_frames()
        flashing = current_time < self.flash_end_time
        if self.facing == "left":
            frames = white_left if flashing else left
        else:
            frames = white_right if flashing else right
        image = frames[self.walk_frame_index]

        # Use the same foot anchor as the original collision box
        rect = image.get_rect(midbottom=self.get_rect().midbottom)
        self.sprite_top = rect.top
        screen.blit(image, rect.move(-camera_x, -camera_y))

    def draw_health_bar(self, screen, camera_x=0, camera_y=0):
        if self.health <= 0:
            return

        # Position the health bar above the enemy
        bar_x = int(self.x - camera_x)
        bar_y = int(getattr(self, "sprite_top", self.y) - camera_y) - 10
        bar_width = self.size
        bar_height = 5

        # Draw the background
        pygame.draw.rect(
            screen,
            (70, 70, 70),
            (bar_x, bar_y, bar_width, bar_height)
        )

        # Draw the remaining health
        health_ratio = max(0, min(self.health / self.max_health, 1))
        pygame.draw.rect(
            screen,
            (200, 60, 60),
            (bar_x, bar_y, int(bar_width * health_ratio), bar_height)
        )

class Boss(Enemy):
    def __init__(self, x, y, enraged=False):
        # initialise the attributes inherited from Enemy
        super().__init__(x, y)

        self.health = 10
        self.max_health = self.health
        self.size = 80
        self.speed = 1

        # track the current behaviour and when it started
        self.state = "chase"
        self.state_start_time = pygame.time.get_ticks()

        # set the duration of each behaviour in millisecond
        self.chase_duraton = 3000
        self.warning_duration = 600
        self.dash_duration = 400

        # store the locked dash direction and movement speed
        self.dash_direction = pygame.Vector2(0, 0)
        self.dash_speed = 12

        # Configure the harder version before loading its animation frames
        self.enraged = enraged
        self.display_height = 180

        if self.enraged:
            self.health = 20
            self.max_health = 20
            self.speed = 1.5
            self.chase_duraton = 2000
            self.dash_speed = 15
            self.display_height = 270

        # Choose attack sprites for the normal or enraged boss
        if self.enraged:
            attack_filename = "boss2_attack.png"
        else:
            attack_filename = "boss1_attack.png"

        pose_path = Path(__file__).parent / "images" / attack_filename

        sheet = pygame.image.load(str(pose_path)).convert_alpha()
        frame_width = sheet.get_width() // 4
        frame_height = sheet.get_height() // 2
        self.boss_left = []
        self.boss_right = []
        self.boss_white_left = []
        self.boss_white_right = []
        display_height = self.display_height
        display_width = max(1, round(
            frame_width * display_height / frame_height
        ))

        for row in range(2):
            for column in range(4):
                rect = pygame.Rect(
                    column * frame_width, row * frame_height,
                    frame_width, frame_height
                )
                frame = sheet.subsurface(rect).copy()
                frame = pygame.transform.scale(
                    frame, (display_width, display_height)
                )
                flash = frame.copy()
                flash.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_MAX)
                self.boss_left.append(frame)
                self.boss_right.append(pygame.transform.flip(frame, True, False))
                self.boss_white_left.append(flash)
                self.boss_white_right.append(
                    pygame.transform.flip(flash, True, False)
                )

        # Choose walking sprites for the normal or enraged boss
        if self.enraged:
            walk_filename = "boss2_walk.png"
        else:
            walk_filename = "boss1_walk.png"

        walk_path = Path(__file__).parent / "images" / walk_filename
        
        walk_sheet = pygame.image.load(str(walk_path)).convert_alpha()

        frame_width = walk_sheet.get_width() // 4
        frame_height = walk_sheet.get_height() // 2

        self.boss_walk_left = []
        self.boss_walk_right = []
        self.boss_walk_white_left = []
        self.boss_walk_white_right = []

        display_height = self.display_height
        display_width = max(
            1, round(frame_width * display_height / frame_height)
        )

        for row in range(2):
            for column in range(4):
                rect = pygame.Rect(
                    column * frame_width,
                    row * frame_height,
                    frame_width,
                    frame_height
                )
                frame = walk_sheet.subsurface(rect).copy()
                frame = pygame.transform.scale(
                    frame, (display_width, display_height)
                )

                # Create a white version while preserving transparency
                flash = frame.copy()
                flash.fill(
                    (255, 255, 255),
                    special_flags=pygame.BLEND_RGB_MAX
                )

                if row == 0:
                    self.boss_walk_left.append(frame)
                    self.boss_walk_white_left.append(flash)
                else:
                    self.boss_walk_right.append(frame)
                    self.boss_walk_white_right.append(flash)

        self.boss_walk_index = 0
        self.boss_walk_last_time = pygame.time.get_ticks()
        self.boss_walk_last_position = (self.x, self.y)
        self.boss_was_walking = False


    def move_towards_player(self, player_x, player_y, world):
        if self.health <= 0:
            return

        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.state_start_time

        if self.state == "chase":
            # Follow the player's side until the warning locks the direction
            if player_x < self.x:
                self.facing = "left"
            elif player_x > self.x:
                self.facing = "right"

            # use the normal enemy's chasing behaviour
            super().move_towards_player(player_x, player_y, world)

            if elapsed_time >= self.chase_duraton:
                # lock the direction towards the player's current centre
                boss_center = pygame.Vector2(
                    self.x + self.size / 2,
                    self.y + self.size / 2
                )
                player_center = pygame.Vector2(
                    player_x + 20,
                    player_y + 20
                )

                direction = player_center - boss_center

                # use the direction towards the player, or default to right if their centres overlap
                if direction.length() > 0:
                    # Keep the direction but set its length to 1 so distance does not affect dash speed
                    self.dash_direction = direction.normalize()
                else:
                    self.dash_direction = pygame.Vector2(1, 0)

                self.state = "warning"
                self.state_start_time = current_time

        elif self.state == "warning":
            # stay still while warning the player
            if elapsed_time >= self.warning_duration:
                self.state = "dash"
                self.state_start_time = current_time

        elif self.state == "dash":
            if elapsed_time < self.dash_duration:
                # Keep the dash direction locked and check map collision
                world.move(
                    self,
                    self.dash_direction.x * self.dash_speed,
                    self.dash_direction.y * self.dash_speed
                )
            else:
                self.state = "chase"
                self.state_start_time = current_time

    def draw(self, screen, camera_x=0, camera_y=0):
        if self.health <= 0:
            return

        current_time = pygame.time.get_ticks()
        elapsed_time = max(0, current_time - self.state_start_time)
        flashing = current_time < self.flash_end_time

        # Detect actual movement, including sideways detours
        dx = self.x - self.boss_walk_last_position[0]
        dy = self.y - self.boss_walk_last_position[1]
        moving = abs(dx) > 0.001 or abs(dy) > 0.001

        if self.state == "chase":
            # Face the direction of movement while chasing
            if dx < -0.001:
                self.facing = "left"
            elif dx > 0.001:
                self.facing = "right"

            if moving:
                if not self.boss_was_walking:
                    self.boss_walk_index = 0
                    self.boss_walk_last_time = current_time
                elif current_time - self.boss_walk_last_time >= 120:
                    self.boss_walk_index = (
                        self.boss_walk_index + 1
                    ) % 4
                    self.boss_walk_last_time = current_time
            else:
                self.boss_walk_index = 0

            if self.facing == "left":
                frames = (
                    self.boss_walk_white_left
                    if flashing else self.boss_walk_left
                )
            else:
                frames = (
                    self.boss_walk_white_right
                    if flashing else self.boss_walk_right
                )

            image = frames[self.boss_walk_index]

        else:
            # Keep the existing charge and dash poses
            if self.state == "warning":
                frame_index = 1
            else:
                frame_index = 2 + min(
                    5, int(elapsed_time * 6 / self.dash_duration)
                )

            if self.facing == "left":
                frames = (
                    self.boss_white_left
                    if flashing else self.boss_left
                )
            else:
                frames = (
                    self.boss_white_right
                    if flashing else self.boss_right
                )

            image = frames[frame_index]

        self.boss_walk_last_position = (self.x, self.y)
        self.boss_was_walking = moving and self.state == "chase"

        # Align walking and attacking images to the same foot position
        screen_rect = self.get_rect().move(-camera_x, -camera_y)
        image_rect = image.get_rect(midbottom=screen_rect.midbottom)
        self.sprite_top = image_rect.top + camera_y

        screen.blit(image, image_rect)
