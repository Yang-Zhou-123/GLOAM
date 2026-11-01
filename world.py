import math
from pathlib import Path
import pygame


class World:
    def __init__(self, width, height):
        # Load the mask: white is walkable, black is blocked
        mask_path = (
            Path(__file__).parent
            / "images"
            / "walkable_mask2.png"
        )
        image = pygame.image.load(str(mask_path)).convert()

        # Match the mask to the displayed map size
        self.walkable = pygame.transform.scale(image, (width, height))

        # Store white pixels as walkable areas
        self.mask = pygame.mask.from_threshold(
            self.walkable,
            (255, 255, 255),
            (1, 1, 1, 255)
        )

    def can_stand(self, actor, x, y):
        # Check a small rectangle near the actor's feet
        foot_width = max(8, round(actor.size * 0.5))
        foot_height = max(6, round(actor.size * 0.2))

        feet = pygame.Rect(
            round(x + (actor.size - foot_width) / 2),
            round(y + actor.size - foot_height),
            foot_width,
            foot_height
        )

        # Block positions outside the map
        if not self.walkable.get_rect().contains(feet):
            return False

        # Every pixel under the feet must be walkable
        for px in range(feet.left, feet.right):
            for py in range(feet.top, feet.bottom):
                if not self.mask.get_at((px, py)):
                    return False

        return True

    def move(self, actor, dx, dy):
        # Use small steps to prevent fast movement through obstacles
        steps = max(1, math.ceil(max(abs(dx), abs(dy))))
        step_x = dx / steps
        step_y = dy / steps

        for _ in range(steps):
            # Check horizontal and vertical movement separately
            if self.can_stand(actor, actor.x + step_x, actor.y):
                actor.x += step_x

            if self.can_stand(actor, actor.x, actor.y + step_y):
                actor.y += step_y