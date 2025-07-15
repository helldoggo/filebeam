FileBeam

FileBeam is an interactive terminal file browser for Linux.
Navigate, inspect, and manage files and directories from a curses-based UI.


---

Features

TUI file browser using urwid

Displays file size, disk usage, and a 20×20 usage grid

Configurable keybindings and default open command

Supports navigation, deletion (with and without confirmation), moving, copying, renaming

Multi-select support

Supports hidden files (-H)

Threaded folder size calculation

Works as a standalone binary (when built with PyInstaller)



---

Installation

You can either use the precompiled binary located in the dist/ directory or run the Python script directly.

Option 1: Precompiled binary

A statically-built binary is provided in dist/filebeam.
You can copy it to /usr/bin/ or anywhere in your PATH:

sudo cp dist/filebeam /usr/bin/
filebeam

Option 2: Run as a Python script

Ensure filebeam.py (or main.py) has the shebang:

#!/usr/bin/env python3

and is executable:

chmod +x filebeam.py
./filebeam.py

Both methods provide identical functionality.


---

Usage

filebeam [options] [path]

Options

Option	Description

-H, --hidden	Show hidden dotfiles
path	Starting folder (default: /)



---

Default Keybindings

Navigation

Keys	Action

↑ / k / ctrl p	Move up
↓ / j / ctrl n	Move down
enter / l / ctrl f	Enter directory
← / h / backspace	Go to parent directory
q	Quit
space	Toggle selection


Deletion

Keys	Action

ctrl d	Delete selected (confirmation)
meta d	Delete selected (no confirmation)


Opening

Keys	Action

ctrl o	Prompt for program and arguments to open file(s)


Move / Copy / Rename

Keys	Action

ctrl x / meta m / ctrl w	Move
meta c / alt c / alt w	Copy
f2 / alt r / ctrl y / alt y	Rename



---

Configuration

On first run, a configuration file is created at ~/.filebeam/config.yaml.
You can edit it to change keybindings or default open command.

Default configuration:

keybindings:
  move_up:        ['up', 'k', 'ctrl p']
  move_down:      ['down', 'j', 'ctrl n']
  enter_dir:      ['enter', 'l', 'ctrl f']
  parent_dir:     ['left', 'h', 'backspace']
  quit:           ['q']
  delete_confirm: ['ctrl d']
  delete_immediate: ['meta d']
  open_prompt:    ['ctrl o']
  move:           ['ctrl x', 'meta m', 'ctrl w']
  copy:           ['meta c', 'alt c', 'alt w']
  rename:         ['f2', 'alt r', 'ctrl y', 'alt y']
  toggle_select:  ['space']
defaults:
  open_command:   'nvim {}'


---

Notes

rename applies only to the focused item, even if multiple are selected.

delete, move, and copy act on all selected items if any, or just the focused item otherwise.

Multi-select is toggled with space and indicated in the file list with [*].



---

Requirements

If running as a Python script, you need the following dependencies installed:

PyYAML==6.0.2
urwid==3.0.2

You can install them with:

pip install -r requirements.txt

requirements.txt

PyYAML==6.0.2
urwid==3.0.2

