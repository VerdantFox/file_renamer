"""file_renamer: module for renaming files"""
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from file_renamer.src.main import MainPage


class FileRenamer:
    """A class for renaming files"""

    def __init__(self, kivy_gui: "MainPage") -> None:
        """Initialize class"""
        super().__init__()

        # Attributes pulled/massaged from kivy GUI
        self.output_row = kivy_gui.row_5
        self.set_progressbar_max = kivy_gui.set_progressbar_max
        self.update_progress_bar_val = kivy_gui.update_progress_bar_val
        self.message = kivy_gui.message
        self.prepend = (
            kivy_gui.prepend_filename_input.text.strip()
            .replace(" ", "_")
            .replace("-", "_")
            .replace(".", "")
        )
        self.extensions = self.get_extensions(kivy_gui.extensions_input.text.lower())
        self.folder_loc_msg = kivy_gui.folder_loc_msg
        self.folder_loc = self.get_path(kivy_gui.folder_loc_label.text)

        # Attributes calculated by `rename_files()`
        self.relevant_files: list[Path] = []
        self.total_relevant_files = 0
        self.padding = 1

    @staticmethod
    def get_extensions(extensions_string: Optional[str]) -> list[str]:
        """Get extensions in list from string"""
        if not extensions_string:
            return []
        extensions = extensions_string.strip().split(",")
        return [f".{ext.strip(' .')}" for ext in extensions]

    def get_path(self, dir_path: str) -> Optional[Path]:
        """Get path to file"""
        if dir_path == self.folder_loc_msg:
            return None
        return Path(dir_path)

    def check_inputs(self) -> bool:
        """Check inputs are input properly, Return True if errors found"""
        errors = []
        if not self.prepend:
            errors.append("Add filename prepend!")
        if not self.extensions:
            errors.append("Add affected extensions!")
        if not self.folder_loc:
            errors.append("Select a folder!")
        if not errors:
            return False
        error_msg = " ".join(errors)
        self.message(error_msg)
        return True

    def list_relevant_files(self) -> int:
        """Create list of all paths with relevant file extensions in folder"""
        assert isinstance(self.folder_loc, Path)
        for path in self.folder_loc.iterdir():
            if any(str(path).lower().endswith(ext) for ext in self.extensions):
                self.relevant_files.append(path)
        self.relevant_files.sort()
        self.total_relevant_files = len(self.relevant_files)
        self.set_progressbar_max(self.total_relevant_files)
        return self.total_relevant_files

    def get_padding(self) -> None:
        """Get padding size from total_relevant_files count"""
        remaining_files = float(self.total_relevant_files)
        while True:
            remaining_files /= 10
            if remaining_files > 1:
                self.padding += 1
            else:
                break

    def rename_files(self) -> None:
        """Main function for renaming files"""
        if self.check_inputs():
            return
        if not self.list_relevant_files():
            self.message("No files with provided file extension(s) found in folder!")
            return
        self.get_padding()
        for file_num, path in enumerate(self.relevant_files, start=1):
            extension = path.suffix
            directory = path.parent
            file_num_str = str(file_num).zfill(self.padding)
            new_name = f"{self.prepend}_{file_num_str}{extension}"
            new_filepath = Path(directory, new_name)
            path.rename(new_filepath)
            self.update_progress_bar_val(file_num)
        self.message(f"Done! Renamed {self.total_relevant_files:,} files!")
