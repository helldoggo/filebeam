from os.path import isdir
import urwid
import os
import shutil
import argparse

def main():
    #Class for list items
    class Item:
        def __init__(self, path):
            self.path = path
            self.name = os.path.basename(path)
            self.is_dir = os.path.isdir(path)
            self.type = "Directory" if self.is_dir else "File"
            self.size = os.path.getsize(path) if not self.is_dir else 0

            
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
                

                
   #Argument parser for starting point
    starting_parser = argparse.ArgumentParser(description="Starting point for disk analysis")
    starting_parser.add_argument("path", nargs="?", default="/", help="Starting folder")
    args = starting_parser.parse_args()
    print(f"Starting at: {args.path}")

    cwd = args.path
   
    entries = os.listdir(cwd)
    
    items = []

    #Object initialization
    for entry in entries:
        full_path = os.path.join(cwd, entry)
        if os.path.exists(full_path):
            item = Item(full_path)
            items.append(item)

    for i in items:
        i.check_if_file()
        if i.size > 1024:
            i.size = i.size / (1024 ** 2)
        print(f"{i.name}, {i.type},{round(i.size,2)} megabytes")
    



    
main()

    
