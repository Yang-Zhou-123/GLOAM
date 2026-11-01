# GLOAM

GLOAM is a single-player, top-down pixel-art action game made with Python and Pygame for a COMP9001 project. Explore a mysterious forest, defeat waves of creatures, choose an upgrade, and cross a portal to challenge an enlarged, enraged boss.

## Requirements

- Python 3. The game was developed and run on macOS with Python 3.9.6.
- Pygame 2.6.1, the only external Python library required.
- A keyboard and mouse.

VSCode is optional. The game runs in full-screen mode and can be started from a terminal.

## Installation and launch

1. Download or extract the complete project, including the `images` folder.
2. Install Python 3 if it is not already installed.
3. Open a terminal in the project folder containing `main.py`.
4. Install Pygame and run the game using the commands below.

### macOS / Linux

```bash
python3 -m pip install pygame==2.6.1
python3 main.py
```

### Windows

```powershell
py -m pip install pygame==2.6.1
py main.py
```

If your Python command is `python`, use it in both commands instead. Install Pygame and launch the game with the same Python interpreter. Pygame only needs to be installed once for that interpreter; after installation, run `main.py` to play again.

All other imported modules, such as `pathlib`, `random` and `math`, are included with Python. The game does not require a network connection once Python, Pygame and the project files are available locally.

## Controls

| Input | Action |
| --- | --- |
| Mouse | Hover over and click main-menu buttons |
| Enter | Start the game from the main menu |
| W / A / S / D | Move up / left / down / right |
| Space | Attack nearby enemies |
| 1 / 2 / 3 | Choose the corresponding upgrade when the selection screen appears |
| E | Enter an activated portal when standing nearby |
| R | Restart after defeat or from the demo-complete screen |
| M | Return to the main menu from the demo-complete screen |
| Esc | Return from How to Play; otherwise exit the game |

The player briefly stops moving during an attack. Another attack can begin after the current attack action finishes. Taking damage grants a short protection period, indicated by flashing.

## Game progression

1. Select **Start Game**, or view the controls using **How to Play**.
2. Defeat three consecutive waves: a small enemy, a mixed wave including an elite, and a boss.
3. After all three waves are cleared, choose one of three randomly offered upgrades.
4. The portal opens after the upgrade is selected. Approach it and press **E**.
5. Enter the black-and-red forest and defeat the enlarged, enraged boss.
6. The demo-complete screen appears. Press **R** to play again, **M** for the main menu, or **Esc** to exit.

The upgrade pool includes attack damage, movement speed, health restoration, maximum health, and attack range. Upgrades and remaining health carry into the enraged-boss encounter. Restarting resets the player and progression.

The water-world artwork on the ending screen is a preview of a possible future area; it is not a playable level in this demo.

## Project structure

```text
GLOAM/
├── main.py       # Main loop, combat progression, upgrades and stage changes
├── player.py     # Player movement, attacks, health and animation
├── enemy.py      # Enemies, obstacle avoidance and boss behaviour
├── world.py      # Walkable-mask loading and movement collision checks
├── portal.py     # Portal activation, animation and interaction distance
├── opening.py    # Main menu and How to Play screen
├── ending.py     # Demo-complete screen and navigation choices
├── images/       # Backgrounds, sprites, masks and interface artwork
└── README.md
```

## Current limitations

- Enemies use simple sideways obstacle avoidance rather than full pathfinding and may become stuck around complex boundaries.
- Visual sprites and collision rectangles have different sizes; collision does not follow every visible pixel of a character.
- Music and sound effects are not included in the current version documented here.

## Troubleshooting

- **`ModuleNotFoundError: No module named 'pygame'`**: install Pygame using the Python interpreter that runs the game. In VSCode, check the selected Python interpreter.
- **`FileNotFoundError`**: check that the complete `images` folder is present and that the missing file's name, extension and capitalisation match the code.
- **The window opens and immediately closes**: launch `python3 main.py` on macOS/Linux or `py main.py` on Windows from a terminal to see the error message.
- **Movement or attacks appear paused**: choose an upgrade if the selection screen is open. Movement is also temporarily paused during attack animations and after defeat.
