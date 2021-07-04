"""test_file_renamer: tests for src/file_renamer.py"""
from pathlib import Path

import pytest

from file_renamer.src.file_renamer import FileRenamer
from file_renamer.src.gui import MainPage

from .conftest import (
    FOLDER_LOC_MSG,
    TEST_FILES,
    assert_changes,
    get_filenames,
    update_main_page,
)


@pytest.fixture
def setup(copy_files: Path) -> tuple[MainPage, Path]:
    """Set up the main page for use with FileRenamer"""
    mp = MainPage()
    mp.folder_loc_label.text = str(copy_files)
    return mp, copy_files


GOOD_PARAMS = [
    pytest.param(
        "Space period.",
        "jpg",
        ["Space_period_1.jpg", "Space_period_2.jpg", "Space_period_3.jpg"],
        ["j1.jpg", "j2.jpg", "j3.jpg"],
        id="jpg_with_complex_prepend",
    ),
    pytest.param(
        "prep",
        "png",
        ["prep_1.PNG", "prep_2.PNG", "prep_3.PNG"],
        ["p1.PNG", "p2.PNG", "p3.PNG"],
        id="png_lowercase",
    ),
    pytest.param(
        "prep",
        "png, .jpg",
        [
            "prep_1.jpg",
            "prep_2.jpg",
            "prep_3.jpg",
            "prep_4.PNG",
            "prep_5.PNG",
            "prep_6.PNG",
        ],
        ["j1.jpg", "j2.jpg", "j3.jpg", "p1.PNG", "p2.PNG", "p3.PNG"],
        id="multi_prepend",
    ),
    pytest.param(
        "prep",
        ".txt",
        [f"prep_{i:02}.txt" for i in range(1, 11)],
        [f"t{i:02}.txt" for i in range(1, 11)],
        id="padded_zeros",
    ),
    pytest.param(
        "prep",
        "missing",
        [],
        [],
        id="no_match",
    ),
]


@pytest.mark.parametrize(
    "prepend, extensions, expected_found, expected_missing", GOOD_PARAMS
)
def test_file_renamer_success(
    prepend: str,
    extensions: str,
    expected_found: list[str],
    expected_missing: list[str],
    setup: tuple[MainPage, Path],
) -> None:
    """First go at tests"""
    main_page, test_dir = setup
    assert get_filenames(test_dir) == TEST_FILES
    update_main_page(main_page, prepend, extensions)
    file_renamer = FileRenamer(main_page)
    file_renamer.rename_files()
    assert_changes(test_dir, expected_found, expected_missing)
    if get_filenames(test_dir) == TEST_FILES:
        msg = "No files with provided file extension(s) found in folder!"
    else:
        msg = f"Done! Renamed {len(expected_found)} files!"
    assert main_page.msg_label.text == msg


BAD_INPUT_PARAMS = [
    pytest.param(
        "",
        "",
        FOLDER_LOC_MSG,
        "Add filename prepend! Add affected extensions! Select a folder!",
        id="all_bad",
    ),
    pytest.param(
        "prep",
        "ext",
        FOLDER_LOC_MSG,
        "Select a folder!",
        id="bad_folder",
    ),
    pytest.param(
        "prep",
        "",
        "/some/loc",
        "Add affected extensions!",
        id="bad_ext",
    ),
    pytest.param(
        "",
        "ext",
        "/some/loc",
        "Add filename prepend!",
        id="bad_ext",
    ),
]


@pytest.mark.parametrize("prepend, extensions, folder_loc, msg", BAD_INPUT_PARAMS)
def test_file_renamer_bad_input(
    copy_files: Path, prepend: str, extensions: str, folder_loc: str, msg: str
) -> None:
    """Test file_renamer with bad inputs"""
    main_page = MainPage()
    update_main_page(main_page, prepend, extensions, folder_loc)
    file_renamer = FileRenamer(main_page)
    file_renamer.rename_files()
    assert get_filenames(copy_files) == TEST_FILES
    assert main_page.msg_label.text == msg
