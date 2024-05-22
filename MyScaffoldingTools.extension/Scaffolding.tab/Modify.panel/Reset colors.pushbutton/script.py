import sys
import os

current_dir = os.path.dirname(__file__)
color_code_dir = os.path.join(current_dir, "../Color code.pushbutton/src")
sys.path.append(color_code_dir)

from color_code_scaffolding import reset_graphic_overrides


def main():
    reset_graphic_overrides()

if __name__ == "__main__":
    main()

