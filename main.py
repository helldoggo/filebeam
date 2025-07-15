import os
import urwid
import argparse
import threading
import shutil
import subprocess
import yaml

def main():
    parser = argparse.ArgumentParser(
        description="""
FileBeam — interactive terminal file browser.
Browse, inspect, and manage your files with ease.
""",
        epilog="""
KEYBINDINGS:
  MOVEMENT:
    ↑ / k / Ctrl+P      - Move up
    ↓ / j / Ctrl+N      - Move down
    Enter / l / Ctrl+F  - Enter directory
    ← / h / Backspace   - Go to parent directory
    q                   - Quit

  DELETION:
    Ctrl+D              - Delete selected file/folder (confirmation)
    Alt+D               - Delete selected file/folder (no confirmation)

  OPENING:
    Ctrl+O              - Prompt for program & arguments to open file with
                          Example: nvim {} or less {}

FLAGS:
  -H / --hidden         - Show hidden dotfiles
  path                  - Starting folder (default: /)
"""
    )
    parser.add_argument("path", nargs="?", default="/", help="Starting folder")
    parser.add_argument("-H", "--hidden", action="store_true", help="Show hidden files (dotfiles)")
    args = parser.parse_args()
    cwd = os.path.abspath(args.path)
    show_hidden = args.hidden

    # Load or create config
    config_path = os.path.expanduser("~/.filebeam/config.yaml")
    default_config = {
        'keybindings': {
            'move_up': ['up', 'k', 'ctrl p'],
            'move_down': ['down', 'j', 'ctrl n'],
            'enter_dir': ['enter', 'l', 'ctrl f'],
            'parent_dir': ['left', 'h', 'backspace'],
            'quit': ['q'],
            'delete_confirm': ['ctrl d'],
            'delete_immediate': ['alt d'],
            'open_prompt': ['ctrl o']
        },
        'defaults': {
            'open_command': 'nvim {}'
        }
    }

    if not os.path.exists(config_path):
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    keybindings = config.get('keybindings', default_config['keybindings'])
    defaults = config.get('defaults', default_config['defaults'])

    disks = {}

    def format_size(size):
        if size < 1024:
            return f"{size} B"
        elif size < 1024 ** 2:
            return f"{size/1024:.1f} KB"
        elif size < 1024 ** 3:
            return f"{size/(1024**2):.1f} MB"
        else:
            return f"{size/(1024**3):.1f} GB"

    def get_disk_and_size(path):
        st = os.statvfs(path)
        disk = os.path.abspath(os.path.realpath(path))
        while not os.path.ismount(disk) and os.path.dirname(disk) != disk:
            disk = os.path.dirname(disk)
        if disk not in disks:
            disks[disk] = st.f_blocks * st.f_frsize
        return disk

    def build_usage_grid(usage_ratio):
        filled_char = '■'
        empty_char = '□'
        grid_size = 20 * 20
        filled_count = int(round(usage_ratio * grid_size))
        grid_lines = []
        for row in range(20):
            line = ''
            for col in range(20):
                index = row * 20 + col
                if index < filled_count:
                    line += filled_char + ' '
                else:
                    line += empty_char + ' '
            grid_lines.append(line.rstrip())
        return '\n'.join(grid_lines)

    class Item:
        def __init__(self, path):
            self.path = path
            if os.path.islink(self.path):
                real = os.path.realpath(self.path)
                if not os.path.exists(real):
                    raise FileNotFoundError(f"Broken symlink: {self.path}")
                self.path = real
            self.name = os.path.basename(self.path)
            self.is_dir = os.path.isdir(self.path)
            self.type = "Directory" if self.is_dir else "File"
            try:
                self.size = os.path.getsize(self.path) if not self.is_dir else 0
            except:
                self.size = 0
            self.size_known = not self.is_dir
            self.disk = get_disk_and_size(self.path)

        def calculate_size_async(self, callback):
            def worker():
                total_size = 0
                for root, _, files in os.walk(self.path):
                    for file in files:
                        try:
                            full_path = os.path.join(root, file)
                            if os.path.islink(full_path):
                                continue
                            total_size += os.path.getsize(full_path)
                        except:
                            continue
                self.size = total_size
                self.size_known = True
                callback(self)
            threading.Thread(target=worker, daemon=True).start()

    walker1 = None
    items_with_widgets = None
    info_text = urwid.Text("")
    loop = None

    def create_array_from_path(path):
        data = []
        if os.path.dirname(path) != path:
            up_item = Item(path)
            up_item.name = ".."
            up_item.path = os.path.dirname(path)
            up_item.is_dir = True
            up_item.type = "Parent Directory"
            data.append((up_item, urwid.AttrMap(urwid.Text(".."), None, focus_map='reversed')))
        for entry in os.scandir(path):
            if not show_hidden and os.path.basename(entry.path).startswith('.'):
                continue
            try:
                item = Item(entry.path)
            except FileNotFoundError:
                continue
            data.append((item, urwid.AttrMap(urwid.Text(item.name), None, focus_map='reversed')))
        data_except_up = data[1:] if data and data[0][0].name == ".." else data
        data_except_up.sort(key=lambda x: x[0].name.lower())
        if data and data[0][0].name == "..":
            return [data[0]] + data_except_up
        return data_except_up

    def update_ui(path):
        nonlocal cwd, items_with_widgets, walker1, body1
        cwd = path
        items_with_widgets = create_array_from_path(cwd)
        walker1[:] = [w[1] for w in items_with_widgets]
        update_info_box()

    def update_info_box():
        focus_position = walker1.focus
        if 0 <= focus_position < len(items_with_widgets):
            item = items_with_widgets[focus_position][0]

            def display():
                disk_size = disks.get(item.disk, 1)
                usage_ratio = item.size / disk_size if disk_size else 0
                percent = usage_ratio * 100
                grid = build_usage_grid(usage_ratio)
                disk_size_str = format_size(disk_size)
                info_text.set_text(
                    f"Name: {item.name}\n"
                    f"Path: {item.path}\n"
                    f"Type: {item.type}\n"
                    f"Disk: {item.disk}\n"
                    f"Disk Size: {disk_size_str}\n"
                    f"Size: {format_size(item.size)}\n"
                    f"Usage: {percent:.2f}%\n\n"
                    f"{grid}"
                )

            if item.is_dir and not item.size_known:
                info_text.set_text(
                    f"Name: {item.name}\n"
                    f"Path: {item.path}\n"
                    f"Type: {item.type}\n"
                    f"Disk: {item.disk}\n"
                    f"Size: calculating..."
                )
                item.calculate_size_async(lambda i: loop.draw_screen())
            else:
                display()

    def delete_item(item):
        try:
            if item.is_dir:
                shutil.rmtree(item.path)
            else:
                os.remove(item.path)
        except Exception as e:
            info_text.set_text(f"Failed to delete {item.name}: {e}")
            return
        update_ui(cwd)

    def confirm_delete_popup(item):
        disk_size = disks.get(item.disk, 1)
        usage_ratio = item.size / disk_size if disk_size else 0
        percent = usage_ratio * 100

        body = urwid.Text((
            f"Delete the following?\n\n"
            f"Name: {item.name}\n"
            f"Size: {format_size(item.size)}\n"
            f"Disk Usage: {percent:.2f}%\n\n"
            f"Press 'y' to confirm, 'n' to cancel."
        ))
        fill = urwid.Filler(body, valign='middle')
        box = urwid.LineBox(fill)
        overlay = urwid.Overlay(box, loop.widget,
                                align='center', width=('relative', 50),
                                valign='middle', height=('relative', 30))

        def popup_input(key):
            if key in ('y', 'Y'):
                delete_item(item)
                loop.widget = rows
                loop.unhandled_input = handle_input
            elif key in ('n', 'N', 'esc'):
                loop.widget = rows
                loop.unhandled_input = handle_input

        loop.widget = overlay
        loop.draw_screen()
        loop.unhandled_input = popup_input

    def prompt_open_program(item):
        edit = urwid.Edit("Enter program and [optional] arguments to open with:\n")
        fill = urwid.Filler(edit, valign='middle')
        box = urwid.LineBox(fill)
        overlay = urwid.Overlay(box, loop.widget,
                                align='center', width=('relative', 50),
                                valign='middle', height=('relative', 30))

        def handle_open_input(key):
            if key == 'enter':
                cmd_template = edit.edit_text.strip()
                if cmd_template == '':
                    cmd_template = defaults.get('open_command', 'nvim {}')
                if '{}' in cmd_template:
                    cmd = cmd_template.replace("{}", f'"{item.path}"')
                else:
                    cmd = f'{cmd_template} "{item.path}"'
                try:
                    os.execlp("/bin/sh", "sh", "-c", cmd)
                except Exception as e:
                    info_text.set_text(f"Failed to run: {e}")
                    loop.widget = rows
                    loop.unhandled_input = handle_input
            elif key in ('esc',):
                loop.widget = rows
                loop.unhandled_input = handle_input

        loop.widget = overlay
        loop.draw_screen()
        loop.unhandled_input = handle_open_input

    def handle_input(key):
        nonlocal loop
        if key in keybindings['quit']:
            raise urwid.ExitMainLoop()
        focus_position = walker1.focus

        if key in keybindings['move_down']:
            if focus_position < len(walker1) - 1:
                walker1.set_focus(focus_position + 1)
                update_info_box()

        elif key in keybindings['move_up']:
            if focus_position > 0:
                walker1.set_focus(focus_position - 1)
                update_info_box()

        elif key in keybindings['enter_dir']:
            item = items_with_widgets[walker1.focus][0]
            if item.is_dir:
                update_ui(item.path)

        elif key in keybindings['parent_dir']:
            if cwd != '/':
                parent = os.path.dirname(cwd)
                update_ui(parent)

        elif key in keybindings['delete_confirm']:
            item = items_with_widgets[walker1.focus][0]
            confirm_delete_popup(item)

        elif key in keybindings['delete_immediate']:
            item = items_with_widgets[walker1.focus][0]
            delete_item(item)

        elif key in keybindings['open_prompt']:
            item = items_with_widgets[walker1.focus][0]
            prompt_open_program(item)

    def refresh(loop_, user_data):
        update_info_box()
        loop.set_alarm_in(0.5, refresh)

    title = urwid.Text("FileBeam", align='center')
    title_row = ('pack', urwid.Filler(title, height='pack'))

    items_with_widgets = create_array_from_path(cwd)
    walker1 = urwid.SimpleFocusListWalker([w[1] for w in items_with_widgets])
    body1 = urwid.ListBox(walker1)

    info_text.set_text("Select a file or folder to see details")
    info_text_filled = urwid.Filler(info_text, valign='top')
    info_box = urwid.LineBox(info_text_filled, title="Details")

    columns = urwid.Columns([
        ('weight', 2, body1),
        ('weight', 3, info_box)
    ], dividechars=1)

    rows = urwid.Pile([
        title_row,
        ('weight', 1, columns)
    ])

    loop = urwid.MainLoop(rows, palette=[('reversed', 'standout', '')], unhandled_input=handle_input)
    update_info_box()
    loop.set_alarm_in(0.5, refresh)
    loop.run()


main()
