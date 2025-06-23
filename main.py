from os.path import isdir
import urwid
import os
import shutil
import argparse


def main():
    # Argument parser for starting point
    starting_parser = argparse.ArgumentParser(
        description="Starting point for disk analysis"
    )
    starting_parser.add_argument("path", nargs="?", default="/", help="Starting folder")
    args = starting_parser.parse_args()
    print(f"Starting at: {args.path}")
    cwd = args.path

    # Class for list items
    class Item:
        def __init__(self, path):
            self.path = path
            self.name = os.path.basename(path)
            self.is_dir = os.path.isdir(path)
            self.type = "Directory" if self.is_dir else "File"
            # Add visual indicators to folders
            self.display_name = f"📁 {self.name}" if self.is_dir else f"  {self.name}"
            # Handle file size with error checking
            try:
                if not self.is_dir:
                    if os.path.lexists(
                        path
                    ):  # Check if path exists (including broken links)
                        if os.path.exists(path):  # Check if it's not a broken link
                            self.size = os.path.getsize(path)
                        else:
                            self.size = 0  # Broken link
                    else:
                        self.size = 0  # Non-existent file
                else:
                    self.size = 0  # Directory
            except (OSError, PermissionError) as e:
                self.size = 0  # Fallback for any other errors
                self.error = str(e)
            self.size = int(self.size)

        def check_if_file(self):
            if not self.is_dir:
                return

            total_size = 0
            for root, dirs, files in os.walk(self.path):
                for file in files:
                    try:
                        full_path = os.path.join(root, file)
                        total_size += os.path.getsize(full_path)
                    except:
                        continue
            self.size = total_size

    def create_array_from_path(path):
        def return_dir(path):
            files = []
            try:
                for entry in os.scandir(path):
                    try:
                        item = Item(entry.path)
                        files.append(item)
                    except PermissionError:
                        # Skip files we can't access
                        continue
            except PermissionError:
                # Return empty list with access error message
                return []
            return files

        def urwid_init(array):
            items = []
            if not array:  # Empty array means permission denied
                message = urwid.Text(
                    ("error", "⚠️ Permission denied - cannot access directory")
                )
                widget = urwid.AttrMap(message, "error", focus_map="reversed")
                items.append(widget)
            else:
                for item in array:
                    # Use the display_name with folder indicator
                    text = urwid.Text(item.display_name)
                    # Apply different colors to folders and files
                    color = "folder" if item.is_dir else "file"
                    widget = urwid.AttrMap(text, color, focus_map="reversed")
                    items.append(widget)
            return items

        return urwid_init(return_dir(path))

    # Define the color palette with all needed attributes
    palette = [
        ("reversed", "standout", ""),
        ("error", "white", "dark red"),
        ("folder", "light cyan", ""),
        ("file", "white", ""),
    ]

    title = urwid.Text(f"FileBeam - {cwd}")
    walker1 = urwid.SimpleFocusListWalker(create_array_from_path(cwd))
    body1 = urwid.ListBox(walker1)
    columns = urwid.Columns([body1], dividechars=1)
    rows = urwid.Pile([("pack", title), columns])

    def update_gui_seen_path(new_path):
        nonlocal cwd, title, walker1
        cwd = new_path
        title.set_text(f"FileBeam - {cwd}")
        walker1[:] = create_array_from_path(cwd)
        walker1.set_focus(0)  # Reset focus to top

    def handle_input(key):
        if len(walker1) == 0:
            return

        # Get the currently focused widget and its position
        focus_widget, pos = walker1.get_focus()

        if key in ("q", "Q"):
            raise urwid.ExitMainLoop()
        elif key in ("down", "ctrl n", "j"):
            if pos < len(walker1) - 1:
                walker1.set_focus(pos + 1)
        elif key in ("up", "ctrl p", "k"):
            if pos > 0:
                walker1.set_focus(pos - 1)
        elif key == "enter":
            # Get the text from the focused widget
            widget_text = focus_widget.original_widget.text
            # Extract the actual filename (remove folder icon if present)
            item_name = widget_text.split(" ", 1)[-1].strip()
            item_path = os.path.join(cwd, item_name)
            if os.path.isdir(item_path):
                update_gui_seen_path(item_path)
        elif key == "backspace":
            parent_dir = os.path.dirname(cwd)
            if parent_dir != cwd:
                update_gui_seen_path(parent_dir)

    loop = urwid.MainLoop(rows, palette=palette, unhandled_input=handle_input)
    loop.run()


if __name__ == "__main__":
    main()
