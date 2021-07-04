"""conftest: pytest setup file"""
import shutil
from pathlib import Path
from typing import Optional

import pytest

from file_renamer.src.gui import MainPage

TEST_DATA_DIR = Path(__file__).parents[1].joinpath("test_data")
TEST_FILES = sorted([path.name for path in TEST_DATA_DIR.iterdir()])
FOLDER_LOC_MSG = "<-- Please select"


@pytest.fixture
def copy_files(tmp_path: Path) -> Path:
    """Copy files to tmp folder"""
    test_folder = tmp_path.joinpath("test_folder_files")
    test_folder.mkdir()
    for path in TEST_DATA_DIR.iterdir():
        new_path = Path(test_folder, path.name)
        shutil.copy(path, new_path)
    return test_folder


def update_main_page(
    main_page: MainPage,
    prepend: str,
    extensions: str,
    folder_loc: Optional[str] = None,
) -> None:
    """Make updates to main page"""
    main_page.prepend_filename_input.text = prepend
    main_page.extensions_input.text = extensions
    if folder_loc:
        main_page.folder_loc_label.text = folder_loc


def get_filenames(test_dir: Path) -> list[str]:
    """Get filenames from dir"""
    return sorted([path.name for path in test_dir.iterdir()])


def assert_changes(
    test_dir: Path, expected_found: list[str], expected_missing: list[str]
) -> list[str]:
    """Assert changes are as expected"""
    file_names = get_filenames(test_dir)
    for name in expected_found:
        assert name in file_names
    for name in expected_missing:
        assert name not in file_names
    assert len(file_names) == len(TEST_FILES)
    return file_names
