"""test_main: tests for src/main.py"""
from pathlib import Path

import pytest
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.button import Button

from file_renamer.src.gui import FileRenamerApp

from .conftest import FOLDER_LOC_MSG, assert_changes

setup_type = tuple[FileRenamerApp, str, str]


@pytest.fixture
def setup(copy_files: Path) -> setup_type:
    """Set up a FileRenamerApp"""
    test_folder = str(copy_files)
    test_file = str(list(copy_files.iterdir())[0])
    app = FileRenamerApp()
    app.build()
    Clock.tick()
    return app, test_folder, test_file


def press_button(button: Button) -> None:
    """Press the given button"""
    button.dispatch("on_press")
    Clock.tick()
    button.dispatch("on_release")
    Clock.tick()


def reset_folder_selection(app: FileRenamerApp) -> None:
    """Resets folder selection to original value"""
    app.folder_selector_page.folder_select.selection = []
    app.folder_selector_page.selected_label.text = ""
    app.main_page.folder_loc_label.text = FOLDER_LOC_MSG
    Clock.tick()


def btn_to_folder_select(app: FileRenamerApp) -> None:
    """Press button to go to main page and assert there"""
    press_button(app.main_page.folder_loc_btn)
    assert app.screen_manager.current == "FolderSelect"


def test_rename_succeeds(setup: setup_type) -> None:
    """Test running filerenamer through GUI"""
    app, test_folder, test_file = setup
    app.main_page.folder_loc_label.text = test_folder
    app.main_page.prepend_filename_input.text = "foo bar"
    app.main_page.extensions_input.text = "jpg"
    press_button(app.main_page.submit_btn)
    # Test that button doesn't work while already running
    press_button(app.main_page.submit_btn)
    Clock.tick()
    assert app.main_page.msg_label.text == "Done! Renamed 3 files!"
    assert_changes(
        test_dir=Path(test_folder),
        expected_found=["foo_bar_1.jpg", "foo_bar_2.jpg", "foo_bar_3.jpg"],
        expected_missing=["j1.jpg", "j2.jpg", "j3.jpg"],
    )


def test_folder_selector(setup: setup_type) -> None:
    """Test the app folder selector page"""
    app, test_folder, test_file = setup
    # Click Button to go to FolderSelectPage
    btn_to_folder_select(app)
    # Hit back button
    press_button(app.folder_selector_page.back_btn)
    assert app.screen_manager.current == "Main"
    # Go to FolderSelectPage again
    btn_to_folder_select(app)
    # Confirm selection with no folder/file selected should do nothing
    press_button(app.folder_selector_page.select_btn)
    assert app.screen_manager.current == "FolderSelect"
    assert app.main_page.folder_loc_label.text == FOLDER_LOC_MSG
    # Set selection to dir and ensure selection updates properly
    app.folder_selector_page.folder_select.selection = [test_folder]
    Clock.tick()
    assert app.folder_selector_page.selected_label.text == test_folder
    # Confirm selection with button
    press_button(app.folder_selector_page.select_btn)
    assert app.screen_manager.current == "Main"
    assert app.main_page.folder_loc_label.text == test_folder
    # Reset folder selection
    reset_folder_selection(app)
    btn_to_folder_select(app)
    # Set selection to file and ensure selection updates properly
    app.folder_selector_page.folder_select.selection = [test_file]
    Clock.tick()
    assert app.folder_selector_page.selected_label.text == test_file
    # Confirm selection with button (should convert file to parent folder)
    press_button(app.folder_selector_page.select_btn)
    assert app.screen_manager.current == "Main"
    assert app.main_page.folder_loc_label.text == test_folder


def test_filedrop(setup: setup_type) -> None:
    """Test the app folder selector page"""
    app, test_folder, test_file = setup

    # Drop file on main page
    assert app.screen_manager.current == "Main"
    # With folder
    Window.dispatch("on_dropfile", test_folder.encode("utf-8"))
    assert app.main_page.folder_loc_label.text == test_folder
    # With file (updates to folder)
    Window.dispatch("on_dropfile", test_file.encode("utf-8"))
    assert app.main_page.folder_loc_label.text == test_folder

    # On Filechooser page
    btn_to_folder_select(app)
    # With folder
    Window.dispatch("on_dropfile", test_folder.encode("utf-8"))
    assert app.folder_selector_page.selected_label.text == test_folder
    assert app.folder_selector_page.folder_select.selection == [test_folder]
    # With file
    reset_folder_selection(app)
    Window.dispatch("on_dropfile", test_file.encode("utf-8"))
    assert app.folder_selector_page.selected_label.text == test_folder
    assert app.folder_selector_page.folder_select.selection == [test_folder]
