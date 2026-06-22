# folder-finder

A simple command-line tool for finding folders by keyword and gathering their files into one place.

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

After folders are found, you can:

- select which matches to organize (by number, range, or `all`)
- choose a single destination folder where all files from those folders will be moved

### Command-line mode

```bash
python folder_finder.py --root /path/to/search --keywords doc,project
```

When matches are found, the program still prompts you to select folders and choose a destination unless you pass `--no-organize`.

### Options

| Flag | Description |
|------|-------------|
| `-r`, `--root` | Directory to search (default: current directory) |
| `-k`, `--keywords` | Keywords separated by commas or spaces |
| `--any` | Match folders that contain any keyword |
| `--no-recursive` | Search only immediate child folders |
| `-i`, `--interactive` | Force interactive prompts |
| `--no-organize` | Find folders only; skip selection and move step |

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

Search without organizing:

```bash
python folder_finder.py -r ./projects --keywords code --no-organize
```

### Extracting files

After a search, you will see a numbered list like:

```text
Found 3 folder(s):

  1. projects/alpha-docs
  2. projects/beta-code
  3. archive/old-photos
```

You can then enter:

- `1,3` to extract files from folders 1 and 3
- `1-3` to extract files from folders 1 through 3
- `all` to extract files from every match
- Enter with no input to skip organizing

All files inside the selected folders (including subfolders) are moved into the destination folder you provide. If two files share the same name, the program adds a numeric suffix (for example, `report_1.pdf`). If one selected folder is inside another, files are only collected once from the parent folder.
