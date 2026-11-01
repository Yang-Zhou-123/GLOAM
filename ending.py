import pygame
from pathlib import Path

def show_ending(screen):
    # Load the ending image and preserve its proportions
    image_path = Path(__file__).parent / "images" / "ending.png"
    image = pygame.image.load(str(image_path)).convert()

    screen_width, screen_height = screen.get_size()
    scale = min(
        screen_width / image.get_width(),
        screen_height / image.get_height()
    )

    image = pygame.transform.scale(
        image,
        (
            round(image.get_width() * scale),
            round(image.get_height() * scale)
        )
    )

    image_rect = image.get_rect(center=screen.get_rect().center)
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "restart"
                elif event.key == pygame.K_m:
                    return "menu"
                elif event.key == pygame.K_ESCAPE:
                    return "quit"

        # Display only the ending artwork
        screen.fill((2, 15, 30))
        screen.blit(image, image_rect)

        pygame.display.flip()
        clock.tick(60)

def show_boss_defeated(screen):
    # Keep the current game scene behind the message
    background = screen.copy()

    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 150))

    font = pygame.font.Font(None, 80)
    text = font.render(
        "BOSS DEFEATED!", True, (255, 245, 220)
    )
    text_rect = text.get_rect(center=screen.get_rect().center)

    start_time = pygame.time.get_ticks()
    clock = pygame.time.Clock()

    # Display the message for two seconds
    while pygame.time.get_ticks() - start_time < 2000:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

        screen.blit(background, (0, 0))
        screen.blit(shade, (0, 0))
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60)

    return True