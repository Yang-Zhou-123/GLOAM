import pygame
from pathlib import Path

def show_opening(screen):
    images_path = Path(__file__).parent / "images"
    screen_width, screen_height = screen.get_size()

    # Load and proportionally resize the opening background
    background = pygame.image.load(
        str(images_path / "opening2.png")
    ).convert()

    # Fill the screen while preserving the image proportion
    scale = max(
        screen_width / background.get_width(),
        screen_height / background.get_height()
    )

    background = pygame.transform.scale(
        background,
        (
            round(background.get_width() * scale),
            round(background.get_height() * scale)
        )
    )

    background_rect = background.get_rect(
        center=screen.get_rect().center
    )

    # Position buttons relative to the background artwork
    art_width, art_height = background.get_size()
    button_width = round(art_width * 0.25)

    button_files = [
        ("start_game1.png", "start_game2.png"),
        ("how_to_play1.png", "how_to_play2.png"),
        ("exit1.png", "exit2.png")
    ]

    buttons = []

    # Load normal and hover images once
    for index, filenames in enumerate(button_files):
        normal = pygame.image.load(
            str(images_path / filenames[0])
        ).convert_alpha()

        hover = pygame.image.load(
            str(images_path / filenames[1])
        ).convert_alpha()

        button_height = max(
            1,
            round(normal.get_height() * button_width / normal.get_width())
        )
        button_size = (button_width, button_height)

        normal = pygame.transform.scale(normal, button_size)
        hover = pygame.transform.scale(hover, button_size)

        rect = normal.get_rect(
            center=(
                background_rect.left + round(art_width * 0.23),
                background_rect.top
                + round(art_height * (0.58 + index * 0.10))
            )
        )

        buttons.append((normal, hover, rect))

    # Load the instructions image once and fit it within the screen
    how_to_play_image = pygame.image.load(
        str(images_path / "how_to_play_image.png")
    ).convert_alpha()

    help_scale = min(
        screen_width * 0.9 / how_to_play_image.get_width(),
        screen_height * 0.9 / how_to_play_image.get_height()
    )

    how_to_play_image = pygame.transform.scale(
        how_to_play_image,
        (
            max(1, round(how_to_play_image.get_width() * help_scale)),
            max(1, round(how_to_play_image.get_height() * help_scale))
        )
    )

    help_rect = how_to_play_image.get_rect(
        center=screen.get_rect().center
    )

    page = "menu"
    clock = pygame.time.Clock()

    # Create a font for the return hint
    hint_font = pygame.font.Font(None, 40)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if page == "how_to_play":
                        page = "menu"
                    else:
                        return False

                elif event.key == pygame.K_RETURN and page == "menu":
                    return True

            # Only menu buttons respond to mouse clicks
            if page == "menu":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for index, button in enumerate(buttons):
                            normal, hover, rect = button

                            if rect.collidepoint(event.pos):
                                if index == 0:
                                    return True
                                elif index == 1:
                                    page = "how_to_play"
                                else:
                                    return False
                                break

        # The how-to-play page is entirely black for now
        screen.fill((0, 0, 0))

        if page == "menu":
            screen.blit(background, background_rect)
            mouse_position = pygame.mouse.get_pos()

            for normal, hover, rect in buttons:
                # Blue while hovering; yellow otherwise
                if rect.collidepoint(mouse_position):
                    screen.blit(hover, rect)
                else:
                    screen.blit(normal, rect)

        elif page == "how_to_play":
            screen.blit(how_to_play_image, help_rect)

            # Show how to return to the main menu
            hint = hint_font.render(
                "Press ESC to return to menu",
                True,
                (255, 245, 220)
            )
            hint_rect = hint.get_rect(
                midbottom=(screen_width // 2, screen_height - 60)
            )
            screen.blit(hint, hint_rect)

        pygame.display.flip()
        clock.tick(60)