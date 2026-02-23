---
name: divoom-themes
description: Apply visual themes to the Divoom Times Gate 5-screen display
---

# Divoom Times Gate Theme Controller

Control the **Divoom Times Gate** display — 5 individual 128×128 LCD screens (numbered **0–4**, left to right) at IP `10.0.0.21`.

All commands use the CLI tool:
```
python "D:/My Documents/PlatformIO/DivoomDirectControl/divoom_themes.py" <command> [args]
```

## Themes

| Theme | Aliases | Description |
|-------|---------|-------------|
| **synthwave** | neon, retro, vaporwave, 80s, grid, outrun | Retro synthwave sunset, perspective grid floor, cyan/magenta neon glow |
| **nebula** | cosmic, space, galaxy, stars, arcade | Cosmic nebula gas clouds, colorful starfield, rainbow letters |
| **gold** | artdeco, elegant, royal, fancy, purple, deco | Art deco sunburst on purple, gold ornamental frame, script font |
| **matrix** | cyber, hacker, code, rain, city, digital, green | Matrix green rain, city skyline with flickering windows (animated) |
| **fire** | volcano, lava, flames, inferno, volcanic, ember | Volcanic fire, lava cracks, floating embers (animated) |

## Commands

**Apply a theme to one screen:**
```
python "D:/My Documents/PlatformIO/DivoomDirectControl/divoom_themes.py" apply <theme> <screen>
```
`<theme>` — any theme name or alias from the table above.
`<screen>` — screen number 0–4 (left to right).

**Apply the default layout to all 5 screens:**
```
python "D:/My Documents/PlatformIO/DivoomDirectControl/divoom_themes.py" apply-all
```
Default: 0=synthwave, 1=nebula, 2=gold, 3=matrix, 4=fire.

**Set brightness:**
```
python "D:/My Documents/PlatformIO/DivoomDirectControl/divoom_themes.py" brightness <0-100>
```

**List themes:**
```
python "D:/My Documents/PlatformIO/DivoomDirectControl/divoom_themes.py" list
```

## Examples

- "Put the fire theme on screen 2" → `apply fire 2`
- "Make all screens synthwave" → run `apply synthwave 0`, then `apply synthwave 1`, etc.
- "Set up the default display" → `apply-all`
- "Switch screen 0 to the space theme" → `apply nebula 0`
- "Dim the display to 30%" → `brightness 30`
