# Instructions for running pyinstaller

## On windows

### Run command to create spec (not needed if spec already exists)

```bash
python -m PyInstaller cli.py --name file_renamer --onefile --hidden-import pkg_resources.py2_warn --hidden-import win32timezone --icon new_file.ico
```

### Update spec (`file_renamer.spec`) with the following lines

`from kivy_deps import sdl2, glew` at top of file

`*[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],` after `a.datas,` in `exe = EXE`

## Final build run (start here if spec already exists)

Then run:

```bash
python -m PyInstaller file_renamer.spec
```

## On linux

### Run to create spec (and final product)

```bash
python -m PyInstaller cli.py --name file_renamer --onefile
```

Note: The hidden import was found when trying to run the produced executable

### If spec already exists

```bash
python -m PyInstaller file_renamer.spec
```
