#!/usr/bin/env python3
"""CLI for color picker."""

import argparse
import sys
from pathlib import Path

from .base import load_themes, write_theme


def cmd_list(args: argparse.Namespace) -> None:
    """List available themes."""
    themes = load_themes()
    for category, colors in themes.items():
        print(f"\n{category.upper()}")
        for name, hex_color in colors.items():
            print(f"  {name}: {hex_color}")


def cmd_apply(args: argparse.Namespace) -> None:
    """Apply a theme."""
    workspace = Path(args.workspace).resolve()

    if args.color:
        # Direct hex color
        write_theme(args.color, workspace)
        print(f"Applied {args.color} to {workspace}")
        return

    if not args.theme:
        raise ValueError("Must specify --theme or --color")

    # Find theme by name
    themes = load_themes()
    for category, colors in themes.items():
        if args.theme in colors:
            write_theme(colors[args.theme], workspace)
            print(f"Applied {args.theme} ({colors[args.theme]}) to {workspace}")
            return

    raise ValueError(f"Theme '{args.theme}' not found. Use 'list' to see available themes.")


def main() -> None:
    parser = argparse.ArgumentParser(description="VS Code workspace color picker")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list command
    subparsers.add_parser("list", help="List available themes")

    # apply command
    apply_parser = subparsers.add_parser("apply", help="Apply a theme")
    apply_parser.add_argument("--theme", "-t", help="Theme name")
    apply_parser.add_argument("--color", "-c", help="Hex color (e.g. #ff5500)")
    apply_parser.add_argument("--workspace", "-w", default=".", help="Workspace path (default: current dir)")

    args = parser.parse_args()

    if args.command == "list":
        cmd_list(args)
    elif args.command == "apply":
        cmd_apply(args)


if __name__ == "__main__":
    main()
