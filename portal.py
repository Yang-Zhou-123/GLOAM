import pygame
from pathlib import Path


class Portal:
    def __init__(self, x, y):
        # Store the ground position of the portal
        self.x = x
        self.y = y
        self.active = False
        self.start_time = 0
        self.frame_duration = 120

        image_path = Path(__file__).parent / "images" / "portal.png"
        sheet = pygame.image.load(str(image_path)).convert_alpha()

        frame_width = sheet.get_width() // 4
        frame_height = sheet.get_height() // 2

        # Keep the same canvas size for every frame
        display_width = 400
        display_height = round(
            frame_height * display_width / frame_width
        )

        self.frames = []

        for row in range(2):
            for column in range(4):
                rect = pygame.Rect(
                    column * frame_width,
                    row * frame_height,
                    frame_width,
                    frame_height
                )
                frame = sheet.subsurface(rect).copy()
                frame = pygame.transform.scale(
                    frame, (display_width, display_height)
                )
                self.frames.append(frame)

    def activate(self):
        # Start opening only once
        if not self.active:
            self.active = True
            self.start_time = pygame.time.get_ticks()

    def deactivate(self):
        self.active = False

    def is_ready(self):
        # Allow entry after all eight opening frames have played
        return (
            self.active
            and pygame.time.get_ticks() - self.start_time
            >= len(self.frames) * self.frame_duration
        )

    def player_nearby(self, player):
        # Measure distance from the player's feet to the portal's ground centre
        feet = pygame.Vector2(player.get_rect().midbottom)
        return feet.distance_to((self.x, self.y)) <= 100

    def draw(self, screen, camera_x=0, camera_y=0):
        if not self.active:
            return

        elapsed_time = pygame.time.get_ticks() - self.start_time
        frame_number = elapsed_time // self.frame_duration

        if frame_number < len(self.frames):
            frame_index = frame_number
        else:
            # Loop the four fully opened frames
            frame_index = 4 + (frame_number - 8) % 4

        image = self.frames[frame_index]

        # The ground circle sits near the lower part of each frame
        rect = image.get_rect(
            midbottom=(
                round(self.x - camera_x),
                round(self.y - camera_y + image.get_height() * 0.25)
            )
        )
        screen.blit(image, rect)