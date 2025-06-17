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

   #Argument parser for starting point
    starting_parser = argparse.ArgumentParser(description="Starting point for disk analysis")
    starting_parser.add_argument("path", nargs="?", default="/", help="Starting folder")

    args = starting_parser.parse_args()

    print(f"Starting at: {args.path}")
    

    os.chdir(args.path)

    print(os.path.curdir)

main()

    
