"""__main__: main module for running file_renamer"""
import sys
from file_renamer.src.gui import FileRenamerApp

is_windows = sys.platform.lower().startswith("win")


def main():
    """Main function for running Kivy GUI"""
    if is_windows:
        # Hide console
        import ctypes
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 0)

    app = FileRenamerApp()
    app.run()
    sys.exit()
