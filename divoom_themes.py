#!/usr/bin/env python3
"""
Divoom Times Gate Theme Controller
CLI for applying named themes to individual screens.

Usage:
    python divoom_themes.py list
    python divoom_themes.py apply <theme> <screen>
    python divoom_themes.py apply-all
    python divoom_themes.py brightness <0-100>
"""

import sys
import os
import argparse
import time

# Ensure we can import from the same directory regardless of cwd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from divoom_erik import (
    send_command, send_to_screen, send_animation,
    make_screen_neon, make_screen_arcade, make_screen_gold,
    make_screen_matrix, make_screen_fire,
)

THEMES = {
    "synthwave": {
        "description": "Retro synthwave: neon sun, perspective grid floor, cyan/magenta glow text",
        "aliases": ["neon", "retro", "vaporwave", "80s", "grid", "outrun"],
        "animated": False,
        "make": make_screen_neon,
    },
    "nebula": {
        "description": "Cosmic nebula: colorful gas clouds, bright starfield, rainbow letters",
        "aliases": ["cosmic", "space", "galaxy", "stars", "arcade"],
        "animated": False,
        "make": make_screen_arcade,
    },
    "gold": {
        "description": "Art deco gold: sunburst rays on purple, diamond shapes, ornamental frame",
        "aliases": ["artdeco", "elegant", "royal", "fancy", "purple", "deco"],
        "animated": False,
        "make": make_screen_gold,
    },
    "matrix": {
        "description": "Matrix city: green rain, city skyline silhouette, flickering windows",
        "aliases": ["cyber", "hacker", "code", "rain", "city", "digital", "green"],
        "animated": True,
        "make": make_screen_matrix,
        "frames": 10,
        "speed_ms": 300,
    },
    "fire": {
        "description": "Volcanic fire: lava cracks, floating embers, smoke, flames",
        "aliases": ["volcano", "lava", "flames", "inferno", "volcanic", "ember"],
        "animated": True,
        "make": make_screen_fire,
        "frames": 10,
        "speed_ms": 250,
    },
}

# Default layout: which theme goes on which screen (0-4 left to right)
DEFAULT_LAYOUT = [
    ("synthwave", 0),
    ("nebula", 1),
    ("gold", 2),
    ("matrix", 3),
    ("fire", 4),
]


def resolve_theme(name):
    """Resolve a theme by name or alias. Returns canonical theme name or None."""
    name = name.lower().strip()
    if name in THEMES:
        return name
    for theme_name, info in THEMES.items():
        if name in info["aliases"]:
            return theme_name
    return None


def apply_theme(theme_name, screen_id):
    """Generate and send a theme to a specific screen."""
    info = THEMES[theme_name]
    print(f"Applying '{theme_name}' to screen {screen_id}...")

    if info["animated"]:
        frames = info["make"](num_frames=info["frames"])
        send_animation(screen_id, frames, speed_ms=info["speed_ms"])
    else:
        img = info["make"]()
        send_to_screen(screen_id, img)

    print(f"  Done! Screen {screen_id} = {theme_name}")


def cmd_list(args):
    """List all available themes."""
    print("Available Divoom Times Gate themes:\n")
    for name, info in THEMES.items():
        anim = " (animated)" if info["animated"] else ""
        aliases = ", ".join(info["aliases"])
        print(f"  {name:12s}{anim}")
        print(f"    {info['description']}")
        print(f"    aliases: {aliases}\n")
    print("Screens are numbered 0-4 (left to right).")
    print("Default layout: " + ", ".join(f"{s}={t}" for t, s in DEFAULT_LAYOUT))


def cmd_apply(args):
    """Apply a theme to a screen."""
    theme = resolve_theme(args.theme)
    if theme is None:
        print(f"Error: Unknown theme '{args.theme}'")
        print(f"Available: {', '.join(THEMES.keys())}")
        sys.exit(1)
    if not 0 <= args.screen <= 4:
        print(f"Error: Screen must be 0-4, got {args.screen}")
        sys.exit(1)

    send_command({"Command": "Draw/ResetHttpGifId"})
    time.sleep(0.3)
    apply_theme(theme, args.screen)


def cmd_apply_all(args):
    """Apply the default 5-theme layout to all screens."""
    print("Applying default layout to all 5 screens...")
    send_command({"Command": "Draw/ResetHttpGifId"})
    time.sleep(0.3)

    for theme_name, screen_id in DEFAULT_LAYOUT:
        apply_theme(theme_name, screen_id)
        time.sleep(0.3)

    print("\nAll 5 screens updated!")


def cmd_brightness(args):
    """Set display brightness."""
    level = max(0, min(100, args.level))
    print(f"Setting brightness to {level}%...")
    send_command({"Command": "Channel/SetBrightness", "Brightness": level})


def main():
    parser = argparse.ArgumentParser(
        description="Divoom Times Gate Theme Controller",
        epilog="Themes: " + ", ".join(THEMES.keys()),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    sub.add_parser("list", help="List available themes")

    # apply <theme> <screen>
    p_apply = sub.add_parser("apply", help="Apply a theme to a screen")
    p_apply.add_argument("theme", help="Theme name or alias")
    p_apply.add_argument("screen", type=int, help="Screen number (0-4)")

    # apply-all
    sub.add_parser("apply-all", help="Apply default layout to all screens")

    # brightness <level>
    p_bright = sub.add_parser("brightness", help="Set brightness (0-100)")
    p_bright.add_argument("level", type=int, help="Brightness level 0-100")

    args = parser.parse_args()

    commands = {
        "list": cmd_list,
        "apply": cmd_apply,
        "apply-all": cmd_apply_all,
        "brightness": cmd_brightness,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
