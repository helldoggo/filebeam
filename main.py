from os.path import isdir
import urwid
import os
import shutil
import argparse

def main():
   #Argument parser for starting point
    starting_parser = argparse.ArgumentParser(description="Starting point for disk analysis")
    starting_parser.add_argument("path", nargs="?", default="/", help="Starting folder")
    args = starting_parser.parse_args()
    print(f"Starting at: {args.path}")
    cwd = args.path


    #Class for list items
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
                pass
            else:
                total_size = 0
                for root, dirs, files in os.walk(self.path):
                    for file in files:
                        try:
                            full_path = os.path.join(root,file)
                            total_size += os.path.getsize(full_path)
                        except:
                            continue
                self.size = total_size

    #Object Initialization

    def create_array_from_path(path):

        def return_dir(path):
            files = []
            for i in os.scandir(path):
                Item(i)
                files.append(i)
            return files
        
        def urwid_init(array):
            items = []
            for item in array:
                name = urwid.Text(item.name)
                widget = urwid.AttrMap(name, None, focus_map='reversed')
                items.append(widget)
            return items

        return urwid_init(return_dir(path))



    
        
                
    #Urwid nav functions

    title = urwid.Text("FileBeam")
    walker1 = urwid.SimpleFocusListWalker(create_array_from_path(cwd))
    body1 = urwid.ListBox(walker1)
    columns = urwid.Columns([body1],dividechars=1)
    rows = urwid.Pile([('pack',title),columns])
    
    
    def handle_input(key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

        focus_position = walker1.focus

        if key in ('down', 'ctrl n', 'j'):
            if focus_position < len(walker1) - 1:
                walker1.set_focus(focus_position + 1)

        elif key in ('up', 'ctrl p', 'k'):
            if focus_position > 0:
                walker1.set_focus(focus_position - 1)


    loop = urwid.MainLoop(rows, palette=[('reversed', 'standout', '')], unhandled_input=handle_input)
    loop.run()
    
main()
