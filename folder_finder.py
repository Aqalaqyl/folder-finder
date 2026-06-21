#!/usr/bin/env python3
"""Search folders by keyword from the command line or interactively."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_keywords(raw: str) -> list[str]:
    """Split comma- or space-separated keywords and drop empties."""
    parts = raw.replace(",", " ").split()
    return [part.strip().lower() for part in parts if part.strip()]


def folder_matches(name: str, keywords: list[str], match_all: bool) -> bool:
    """Return True when folder name matches the keyword rules."""
    lowered = name.lower()
    if not keywords:
        return True
    checks = [keyword in lowered for keyword in keywords]
    return all(checks) if match_all else any(checks)


def find_folders(
    root: Path,
    keywords: list[str],
    *,
    recursive: bool = True,
    match_all: bool = True,
) -> list[Path]:
    """Collect folders under root that match the given keywords."""
    matches: list[Path] = []

    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {root}")

    iterator = root.rglob("*") if recursive else root.iterdir()
    for path in iterator:
        if not path.is_dir():
            continue
        if folder_matches(path.name, keywords, match_all):
            matches.append(path)

    return sorted(matches)


def print_results(root: Path, folders: list[Path]) -> None:
    """Print matching folders relative to the search root."""
    if not folders:
        print("No matching folders found.")
        return

    print(f"Found {len(folders)} folder(s):\n")
    for folder in folders:
        try:
            display = folder.relative_to(root)
        except ValueError:
            display = folder
        print(display)


def interactive_session(default_root: Path) -> tuple[Path, list[str], bool, bool]:
    """Prompt the user for search settings."""
    root_input = input(f"Search root [{default_root}]: ").strip()
    root = Path(root_input).expanduser() if root_input else default_root

    keywords_raw = input("Keywords (comma or space separated): ").strip()
    keywords = parse_keywords(keywords_raw)

    mode = input("Match all keywords? [Y/n]: ").strip().lower()
    match_all = mode not in {"n", "no"}

    depth = input("Search subfolders recursively? [Y/n]: ").strip().lower()
    recursive = depth not in {"n", "no"}

    return root, keywords, match_all, recursive


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Find folders whose names match one or more keywords.",
    )
    parser.add_argument(
        "-r",
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Directory to search (default: current directory)",
    )
    parser.add_argument(
        "-k",
        "--keywords",
        help="Keywords to match, separated by commas or spaces",
    )
    parser.add_argument(
        "--any",
        action="store_true",
        help="Match folders that contain any keyword (default: all keywords)",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Only search immediate child folders",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Prompt for search options instead of using flags",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.interactive or not args.keywords:
            root, keywords, match_all, recursive = interactive_session(args.root)
        else:
            root = args.root.expanduser()
            keywords = parse_keywords(args.keywords)
            match_all = not args.any
            recursive = not args.no_recursive

        folders = find_folders(
            root,
            keywords,
            recursive=recursive,
            match_all=match_all,
        )
        print_results(root.resolve(), folders)
        return 0
    except (NotADirectoryError, PermissionError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
