# folder-finder

A simple command-line tool for finding folders by keyword.

## Requirements

- Python 3.9+

## Usage

### Interactive mode

Run the program with no keywords to answer prompts:

```bash
python folder_finder.py
```

You will be asked for:

- the folder to search
- one or more keywords
- whether all keywords must match
- whether to search subfolders recursively

### Command-line mode

```bash
python folder_finder.py --root /path/to/search --keywords doc,project
```

### Options

| Flag | Description |
|------|-------------|
| `-r`, `--root` | Directory to search (default: current directory) |
| `-k`, `--keywords` | Keywords separated by commas or spaces |
| `--any` | Match folders that contain any keyword |
| `--no-recursive` | Search only immediate child folders |
| `-i`, `--interactive` | Force interactive prompts |

### Examples

Find folders whose names contain both `doc` and `alpha`:

```bash
python folder_finder.py -r ~/Documents -k "doc alpha"
```

Find folders that contain either `photo` or `archive`:

```bash
python folder_finder.py -r ~/Pictures --keywords photo,archive --any
```

Search only the top level of a directory:

```bash
python folder_finder.py -r ./projects --keywords code --no-recursive
```
