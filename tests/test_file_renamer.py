"""test_file_renamer: tests for src/file_renamer.py"""

import shutil
from pathlib import Path

import pytest

from file_renamer.src.file_renamer import FileRenamer
from file_renamer.src.main import MainPage

TEST_DATA_DIR = Path(__file__).parents[1].joinpath("test_data")
TEST_FILES = sorted([path.name for path in TEST_DATA_DIR.iterdir()])


@pytest.fixture
def copy_files(tmp_path):
    """Copy files to tmp folder"""
    test_folder = tmp_path.joinpath("test_folder_files")
    test_folder.mkdir()
    for path in TEST_DATA_DIR.iterdir():
        new_path = Path(test_folder, path.name)
        shutil.copy(path, new_path)
    return test_folder


@pytest.fixture
def setup(copy_files):
    """Set up the main page for use with FileRenamer"""
    mp = MainPage()
    mp.folder_loc_label.text = str(copy_files)
    return mp, copy_files


def update_main_page(main_page, prepend, extensions, folder_loc=None):
    """Make updates to main page"""
    main_page.prepend_filename_input.text = prepend
    main_page.extensions_input.text = extensions
    if folder_loc:
        main_page.folder_loc_label.text = folder_loc


def get_filenames(test_dir):
    """Get filenames from dir"""
    return sorted([path.name for path in test_dir.iterdir()])


def assert_changes(test_dir, expected_found, expected_missing):
    """Assert changes are as expected"""
    file_names = get_filenames(test_dir)
    for name in expected_found:
        assert name in file_names
    for name in expected_missing:
        assert name not in file_names
    assert len(file_names) == len(TEST_FILES)
    return file_names


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
    prepend, extensions, expected_found, expected_missing, setup
):
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


FOLDER_LOC_MSG = "<-- Please select"
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
def test_file_renamer_bad_input(copy_files, prepend, extensions, folder_loc, msg):
    """Test file_renamer with bad inputs"""
    main_page = MainPage()
    update_main_page(main_page, prepend, extensions, folder_loc)
    file_renamer = FileRenamer(main_page)
    file_renamer.rename_files()
    assert get_filenames(copy_files) == TEST_FILES
    assert main_page.msg_label.text == msg
