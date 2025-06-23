from os.path import isdir
import urwid
import os
import shutil
import argparse

def main():
    # Argument parser for starting point
    starting_parser = argparse.ArgumentParser(description="Starting point for disk analysis")
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
            self.size = os.path.getsize(path) if not self.is_dir else 0
            self.size = int(self.size)

        def check_if_file(self):
            if self.type == "File":
                return
            else:
                total_size = 0
                for root, dirs, files in os.walk(self.path):
                    for file in files:
                        try:
                            full_path = os.path.join(root, file)
                            total_size += os.path.getsize(full_path)
                        except:
                            continue
                self.size = total_size

    # Create Items and widgets
    def create_array_from_path(path):
        items_data = []
        for entry in os.scandir(path):
            item = Item(entry.path)
            text_widget = urwid.Text(item.name)
            wrapped_widget = urwid.AttrMap(text_widget, None, focus_map='reversed')
            items_data.append((item, wrapped_widget))
        return items_data

    # UI setup
    title = urwid.Text("FileBeam")
    items_with_widgets = create_array_from_path(cwd)
    walker1 = urwid.SimpleFocusListWalker([w[1] for w in items_with_widgets])
    body1 = urwid.ListBox(walker1)

    # Info pane setup
    info_text = urwid.Text("Select a file or folder to see details", wrap='clip')
    info_box = urwid.LineBox(info_text, title="Details")

    columns = urwid.Columns([
        ('weight', 2, body1),
        ('weight', 3, info_box)
    ], dividechars=1)

    rows = urwid.Pile([
        (1, urwid.Filler(title, height='pack')),
        ('weight', 1, columns)  # make this stretch to fill space
    ])

    # Info updater
    def update_info_box():
        focus_position = walker1.focus
        if 0 <= focus_position < len(items_with_widgets):
            item = items_with_widgets[focus_position][0]
            if item.is_dir and item.size == 0:
                item.check_if_file()
            info_text.set_text(
                f"Name: {item.name}\n"
                f"Path: {item.path}\n"
                f"Type: {item.type}\n"
                f"Size: {item.size} bytes"
            )

    # Input handler
    def handle_input(key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

        focus_position = walker1.focus

        if key in ('down', 'ctrl n', 'j'):
            if focus_position < len(walker1) - 1:
                walker1.set_focus(focus_position + 1)
                update_info_box()

        elif key in ('up', 'ctrl p', 'k'):
            if focus_position > 0:
                walker1.set_focus(focus_position - 1)
                update_info_box()

    update_info_box()  # initialize with first item
    loop = urwid.MainLoop(rows, palette=[('reversed', 'standout', '')], unhandled_input=handle_input)
    loop.run()

main()
