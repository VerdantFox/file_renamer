"""__main__: main module for running file_renamer"""
from file_renamer.src.gui import FileRenamerApp


def main():
    """Main function for running Kivy GUI"""
    app = FileRenamerApp()
    app.run()
