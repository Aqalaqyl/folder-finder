#!/usr/bin/env python3
"""Search folders by keyword from the command line or interactively."""

from __future__ import annotations

import argparse
import re
import shutil
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


def display_path(folder: Path, root: Path) -> Path:
    """Return a folder path relative to root when possible."""
    try:
        return folder.relative_to(root)
    except ValueError:
        return folder


def print_results(root: Path, folders: list[Path]) -> None:
    """Print matching folders relative to the search root."""
    if not folders:
        print("No matching folders found.")
        return

    print(f"Found {len(folders)} folder(s):\n")
    for index, folder in enumerate(folders, start=1):
        print(f"  {index}. {display_path(folder, root)}")


def parse_selection(raw: str, count: int) -> list[int]:
    """Parse user selection like '1,3-5' into 1-based indices."""
    if raw.strip().lower() == "all":
        return list(range(1, count + 1))

    indices: set[int] = set()
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue

        range_match = re.fullmatch(r"(\d+)\s*-\s*(\d+)", part)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2))
            if start > end:
                start, end = end, start
            for index in range(start, end + 1):
                indices.add(index)
            continue

        if not part.isdigit():
            raise ValueError(f"Invalid selection: {part}")
        indices.add(int(part))

    invalid = [index for index in indices if index < 1 or index > count]
    if invalid:
        raise ValueError(f"Selection out of range: {', '.join(map(str, sorted(invalid)))}")

    return sorted(indices)


def prune_nested_selection(folders: list[Path]) -> list[Path]:
    """Drop folders that live inside another selected folder."""
    kept: list[Path] = []
    for folder in folders:
        if any(folder != other and folder.is_relative_to(other) for other in folders):
            continue
        kept.append(folder)
    return kept


def select_folders(folders: list[Path]) -> list[Path]:
    """Prompt the user to choose which folders to organize."""
    while True:
        raw = input(
            "\nSelect folders to organize "
            "(numbers, ranges like 1-3, 'all', or Enter to skip): "
        ).strip()
        if not raw:
            return []

        try:
            indices = parse_selection(raw, len(folders))
            return [folders[index - 1] for index in indices]
        except ValueError as error:
            print(f"{error}. Try again.")


def unique_destination_path(destination: Path, filename: str) -> Path:
    """Return an unused path in destination for the given filename."""
    target = destination / filename
    if not target.exists():
        return target

    stem = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 1
    while True:
        candidate = destination / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def collect_files_from_folders(folders: list[Path]) -> list[Path]:
    """Gather every file inside the selected folders."""
    files: list[Path] = []
    for folder in prune_nested_selection(folders):
        for path in folder.rglob("*"):
            if path.is_file():
                files.append(path)
    return sorted(files)


def extract_files(selected: list[Path], destination: Path) -> list[tuple[Path, Path]]:
    """Move all files from selected folders into a single destination folder."""
    destination = destination.expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)

    if any(
        destination == folder or destination.is_relative_to(folder)
        for folder in selected
    ):
        raise ValueError("Destination cannot be inside a selected folder.")

    moved: list[tuple[Path, Path]] = []
    for file_path in collect_files_from_folders(selected):
        target = unique_destination_path(destination, file_path.name)
        shutil.move(str(file_path), str(target))
        moved.append((file_path, target))

    return moved


def prompt_organization(folders: list[Path], root: Path) -> None:
    """Let the user pick folders and extract their files into one destination."""
    selected = select_folders(folders)
    if not selected:
        print("No folders selected. Nothing to organize.")
        return

    print("\nSelected folders:")
    for folder in selected:
        print(f"  - {display_path(folder, root)}")

    while True:
        destination_raw = input(
            "\nDestination folder (all files will be moved here): "
        ).strip()
        if destination_raw:
            destination = Path(destination_raw)
            break
        print("Please enter a destination folder.")

    moved = extract_files(selected, destination)
    if not moved:
        print("No files were found in the selected folders.")
        return

    print(f"\nMoved {len(moved)} file(s) into {destination.resolve()}:")
    for original, new_path in moved:
        print(f"  {original} -> {new_path.name}")


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
    parser.add_argument(
        "--no-organize",
        action="store_true",
        help="Skip the organize step after folders are found",
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

        resolved_root = root.resolve()
        folders = find_folders(
            root,
            keywords,
            recursive=recursive,
            match_all=match_all,
        )
        print_results(resolved_root, folders)

        if folders and not args.no_organize:
            prompt_organization(folders, resolved_root)

        return 0
    except (NotADirectoryError, PermissionError, OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
