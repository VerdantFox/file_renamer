"""main: Kivy GUI application for renaming files"""
import threading
from pathlib import Path
from typing import Optional

import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput

from file_renamer.src.__init__ import __version__
from file_renamer.src.file_renamer import FileRenamer

# ------------------------------------------------------------------------
# GLOBALS
# ------------------------------------------------------------------------
# App version
VERSION = __version__

# Paths
HOME_DIR = Path.home()

# Colors (red, green, blue, transparency) as values between 0 and 1
TEAL = (41 / 255, 241 / 255, 255 / 255, 1)
GREEN = (64 / 255, 255 / 255, 118 / 255, 1)
RED = (245 / 255, 44 / 255, 44 / 255, 1)


# ------------------------------------------------------------------------
# Setup
# ------------------------------------------------------------------------
# Kivy
kivy.require("2.0.0")
Config.set("input", "mouse", "mouse,multitouch_on_demand")
Window.size = (600, 500)
Window.minimum_width, Window.minimum_height = (600, 350)

# Kivy file for updating FileChooserListView font size
KV = """
#:kivy 2.0.0

# Set variables
#:set fs '16dp'

[FileListEntry@FloatLayout+TreeViewNode]:
    locked: False
    entries: []
    path: ctx.path
    # FIXME: is_selected is actually a read_only treeview property. In this
    # case, however, we're doing this because treeview only has single-selection
    # hardcoded in it. The fix to this would be to update treeview to allow
    # multiple selection.
    is_selected: self.path in ctx.controller().selection

    orientation: 'horizontal'
    size_hint_y: None
    height: '60dp' if dp(1) > 1 else '30dp'  # height must be big enough to hold font sized below
    # Don't allow expansion of the ../ node
    is_leaf: not ctx.isdir or ctx.name.endswith('..' + ctx.sep) or self.locked
    on_touch_down: self.collide_point(*args[1].pos) and ctx.controller().entry_touched(self, args[1])
    on_touch_up: self.collide_point(*args[1].pos) and ctx.controller().entry_released(self, args[1])
    BoxLayout:
        pos: root.pos
        size_hint_x: None
        width: root.width
        Label:
            id: filename
            font_size: fs  # adjust this font size
            size_hint_x: None
            width: root.width - sz.width  # this allows filename Label to fill width less size Label
            text_size: self.width, None
            halign: 'left'
            shorten: True
            text: ctx.name
        Label:
            id: sz
            font_size: fs  # adjust this font size
            #text_size: self.width, None
            size_hint_x: None
            width: self.texture_size[0] + dp(18)  # this makes the size Label to minimum width
            text: '{}'.format(ctx.get_nice_size())

"""


# ------------------------------------------------------------------------
# Classes
# ------------------------------------------------------------------------
class MainPage(GridLayout):
    """Main page"""

    # runs on initialization
    def __init__(self, **kwargs) -> None:
        """Initialize all attributes, add row widgets"""
        super().__init__(**kwargs)

        self.app = App.get_running_app()
        # cols attr needed for GridLayout class
        self.cols = 1
        self.worker_thread = threading.Thread()

        # Row 1: Prepend filename input ----------------------------------
        self.prepend_filename_input = TextInput(multiline=False, font_size=18)
        label_text = (
            "Filename prepend:\n(prepend renamed files with this)\n(example: cool_pic)"
        )
        self.prepend_filename_label = Label(
            text=label_text, font_size=18, halign="center", valign="center"
        )
        self.row_1 = GridLayout(cols=2)
        self.row_1.add_widget(self.prepend_filename_label)
        self.row_1.add_widget(self.prepend_filename_input)
        self.add_widget(self.row_1)

        # Row 2: Extensions filename input -------------------------------
        self.extensions_input = TextInput(multiline=False, font_size=18)
        label_text = (
            "Affected extensions:\n(comma separate if multiple)\n(example: jpg,png)"
        )
        self.extensions_label = Label(
            text=label_text, font_size=18, halign="center", valign="center"
        )
        self.row_2 = GridLayout(cols=2)
        self.row_2.add_widget(self.extensions_label)
        self.row_2.add_widget(self.extensions_input)
        self.add_widget(self.row_2)

        # Row 3: Folder location selector --------------------------------
        btn_txt = (
            "       Select folder with\n          "
            "files to rename\n(or drop folder to screen)"
        )
        self.folder_loc_btn = Button(text=btn_txt, font_size=18, background_color=TEAL)
        self.folder_loc_btn.bind(on_press=self.pick_folder)
        self.folder_loc_msg = "<-- Please select"  # Also used in folder_renamer.py
        self.folder_loc_label = Label(
            text=self.folder_loc_msg, halign="center", valign="middle", font_size=18
        )
        self.row_3 = GridLayout(cols=2)
        self.row_3.add_widget(self.folder_loc_btn)
        self.row_3.add_widget(self.folder_loc_label)
        self.add_widget(self.row_3)

        # Row 4: Submit button -------------------------------------------
        btn_text = (
            "                    Rename Files\n(cool_pic_1.jpg, cool_pic_2.jpg, ...)"
        )
        self.submit_btn = Button(text=btn_text, font_size=18, background_color=GREEN)
        self.submit_btn.bind(on_press=self.rename_files)
        self.row_4 = GridLayout(cols=1)
        self.row_4.add_widget(self.submit_btn)
        self.add_widget(self.row_4)

        # Row 5: Output row ----------------------------------------------
        self.progress_bar = ProgressBar()
        self.default_msg = "Fill out the form and hit the green button to rename files!"
        self.msg_label = Label(
            text=self.default_msg, halign="center", valign="middle", font_size=18
        )
        self.row_5 = GridLayout(cols=1)
        self.row_5.add_widget(self.msg_label)
        self.add_widget(self.row_5)

    def reset_progress_bar(self) -> None:
        """Reset progress bar"""
        self.update_progress_bar_val(0)
        self.row_5.clear_widgets()
        self.row_5.add_widget(self.progress_bar)

    def set_progressbar_max(self, max_size: int) -> None:
        """Set progressbar max value"""
        self.progress_bar.max = max_size

    def update_progress_bar_val(self, value: int) -> None:
        """Update the progress bar to new value"""
        self.progress_bar.value = value

    def message(self, msg: str) -> None:
        """Show a message to the output row"""
        self.msg_label.text = msg
        self.row_5.clear_widgets()
        self.row_5.add_widget(self.msg_label)

    def pick_folder(self, _instance) -> None:
        """Open folder selector for our selected button"""
        self.app.screen_manager.transition.direction = "left"
        self.app.folder_selector_page.folder_select.selection = []
        self.app.folder_selector_page.selected_label.text = ""
        self.app.screen_manager.current = "FolderSelect"

    def rename_files(self, _instance) -> None:
        """Renames files in a folder

        This is the main function of this app
        """
        if self.worker_thread.is_alive():
            return  # Don't run if already running
        file_renamer = FileRenamer(self)
        self.reset_progress_bar()
        self.worker_thread = threading.Thread(target=file_renamer.rename_files)
        self.worker_thread.start()


class FolderSelectorPage(GridLayout):
    """Page for choosing folder"""

    def __init__(self, **kwargs) -> None:
        """Initialize all attributes, add row widgets"""
        super().__init__(**kwargs)

        self.app = App.get_running_app()
        # cols attr needed for GridLayout class
        self.cols = 1

        # Row 1: Back and select buttons ---------------------------------
        self.back_btn = Button(text="Back", font_size=18, background_color=RED)
        self.back_btn.bind(on_press=self.go_back)
        self.select_btn = Button(text="Select", font_size=18, background_color=TEAL)
        self.select_btn.bind(on_press=self.confirm_selection)
        self.row_1 = GridLayout(cols=2, size_hint_y=None)
        self.row_1.add_widget(self.back_btn)
        self.row_1.add_widget(self.select_btn)
        self.add_widget(self.row_1)

        # Row 2: Describing label ----------------------------------------
        self.describing_label_text = (
            "Drag desired folder to window OR use folderchooser below\n"
            "to select desired folder, then click select.\n"
            'Can double-click "../" to go to parent folder.'
        )
        self.describing_label = Label(
            text=self.describing_label_text,
            halign="center",
            valign="middle",
            font_size=18,
        )
        self.add_widget(self.describing_label)

        # Row 3: Label for current selected folder -----------------------
        self.selected_label = Label(
            text=str(HOME_DIR), halign="center", valign="middle", font_size=18
        )
        self.add_widget(self.selected_label)

        # Row 4: File chooser list view ----------------------------------
        self.folder_select = FileChooserListView(
            path=str(HOME_DIR),
            dirselect=True,
            size_hint_y=None,
        )
        self.add_widget(self.folder_select)

        Clock.schedule_interval(self.update_selected_label, 0)

    def update_selected_label(self, _) -> None:
        """frequently update self.selected_label"""
        if self.app.screen_manager.current != "FolderSelect":
            return
        if len(self.folder_select.selection) == 1:
            file_path = self.folder_select.selection[0]
            self.folder_select.selection = [file_path]
            self.selected_label.text = file_path

    def confirm_selection(self, _) -> None:
        """Called by button, confirms folder selection and returns to main screen"""
        if len(self.folder_select.selection) != 1:
            return
        selection = self.selected_label.text
        self.describing_label.text = self.describing_label_text
        path = Path(selection)
        if path.is_dir():
            self.app.main_page.folder_loc_label.text = selection
        else:
            self.app.main_page.folder_loc_label.text = str(path.parent)
        self.app.screen_manager.transition.direction = "right"
        self.app.screen_manager.current = "Main"
        self.folder_select.selection = []
        self.folder_select.path = selection
        self.selected_label.text = ""

    def go_back(self, _instance) -> None:
        """Called by button, returns to main screen"""
        self.app.screen_manager.transition.direction = "right"
        self.app.screen_manager.current = "Main"


class FileRenamerApp(App):
    """The main application"""

    def build(self) -> ScreenManager:
        """Build the sceen manager's pages"""
        # Title of App in top bar of GUI
        self.title = f"File Renamer (V{VERSION})"
        # Load KV string for updating FileChooserListView font size
        self.root = Builder.load_string(KV)

        # Use screen manager to easily change between screens
        self.screen_manager = ScreenManager()

        # Initial, Main screen (we use passed in name to activate screen)
        self.main_page = MainPage()
        self.screen1 = Screen(name="Main")
        self.screen1.add_widget(self.main_page)
        self.screen_manager.add_widget(self.screen1)

        # File selector page
        self.folder_selector_page = FolderSelectorPage()
        self.screen2 = Screen(name="FolderSelect")
        self.screen2.add_widget(self.folder_selector_page)
        self.screen_manager.add_widget(self.screen2)

        Window.bind(on_resize=self.on_resize)
        Window.bind(on_maximize=self.on_resize)
        Window.bind(on_restore=self.on_resize)
        Window.bind(on_dropfile=self.on_file_drop)
        self.on_resize()
        return self.screen_manager

    def on_file_drop(self, _window, file_path: bytes) -> None:
        """Called on dropfile to get file path"""
        file_path_str = file_path.decode("utf-8")
        path = Path(file_path_str)
        if path.is_file():
            file_path_str = str(path.parent)

        self.folder_selector_page.selected_label.text = file_path_str
        self.folder_selector_page.folder_select.path = file_path_str
        self.folder_selector_page.folder_select.selection = [file_path_str]
        if self.screen_manager.current == "Main":
            self.main_page.folder_loc_label.text = file_path_str

    def on_resize(
        self, _=None, width: Optional[int] = None, height: Optional[int] = None
    ):
        """Called when window is resized, updates sizing of widgets"""
        if width is None:
            width = Window.width
        if height is None:
            height = Window.height

        # Resizing for file selector
        self.folder_selector_page.selected_label.text_size = [width * 0.98, 50]
        self.folder_selector_page.row_1.height = 50
        self.folder_selector_page.folder_select.height = height - 180

        # Make labels wrap at half window size
        label_width, label_height = width * 0.48, height / 5  # 5 rows
        self.main_page.folder_loc_label.text_size = [label_width, label_height]
