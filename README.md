📁 FileBeam

FileBeam — an interactive terminal file browser.
Browse, inspect, and manage your files with ease.


---

✨ Features

✅ Interactive file & folder browser
✅ Displays file size, disk usage, and a 20×20 visual grid
✅ Configurable keybindings and default open command
✅ Supports navigation, deletion (with & without confirmation), and opening files
✅ Threaded folder size calculation
✅ Supports hidden files (-H)
✅ Clean, responsive TUI powered by urwid


---

🚀 Installation

Requires Python 3 and the urwid, pyyaml libraries:

pip install urwid pyyaml

Download filebeam.py and make it executable:

chmod +x filebeam.py

Or just run it:

python3 filebeam.py


---

📄 Usage

python3 filebeam.py [options] [path]

Options:

Flag	Description

-H, --hidden	Show hidden dotfiles
path	Starting folder (default: /)



---

🎹 Keybindings

📁 Navigation

Key(s) (default)	Action

↑ / k / Ctrl+P	Move up
↓ / j / Ctrl+N	Move down
Enter / l / Ctrl+F	Enter directory
← / h / Backspace	Go to parent directory
q	Quit



---

🗑️ Deletion

Key(s) (default)	Action

Ctrl+D	Delete file/folder (confirm)
Alt+D	Delete file/folder (no prompt)



---

🚀 Open file with program

Key(s) (default)	Action

Ctrl+O	Prompt for program & arguments to open file


When prompted, enter the program and optional arguments to open the selected file.
If you include {} in your command, it will be replaced with the file path.
If you don’t, the file path is appended at the end.

Examples:

Input in prompt	What runs

nvim	nvim "path/to/file"
nvim {}	nvim "path/to/file"
less {}	less "path/to/file"



---

🔧 Configuration

On first run, FileBeam creates a config file at:

~/.filebeam/config.yaml

You can edit this file to change keybindings or the default open command.

Default config.yaml:

keybindings:
  move_up: [up, k, ctrl p]
  move_down: [down, j, ctrl n]
  enter_dir: [enter, l, ctrl f]
  parent_dir: [left, h, backspace]
  quit: [q]
  delete_confirm: [ctrl d]
  delete_immediate: [alt d]
  open_prompt: [ctrl o]

defaults:
  open_command: nvim {}

You can replace or add key combinations to any action.
For example:

delete_immediate: [alt d, ctrl shift x]


---

📊 Visuals

📄 Info panel shows:

Name, Path, Type

Disk, Disk Size, File Size

Usage % and a 20×20 grid



---

📦 License

GNU — use it, share it, improve it!
