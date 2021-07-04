# file_renamer

GUI that renames all files in a given folder with a prefix followed by a sequential number.

## How to use

Start up Kivy GUI by double clicking executable file (or `python cli.py` in dev).
Fill out `Filename prepend` input with a name you want all renamed files
to start with. Fill out `Affected extensions` input with the file extension(s)
you want to be affected by the rename (comma separate extesnsions if there
are files with multiple extensions in folder to rename).
`Selet folder with files to rename` with button to folder selector page or
by dropping a folder to the screen. Hit `Rename Files` button to rename all
files in the given folder with the given extension(s).

## Creator

This application was developed by Theodore (Teddy) Williams. Check out my
website at `verdantfox.com` or my linked in at
`https://www.linkedin.com/in/theodore-f-williams/`. Feel free to message me
there if you have any questions.

## Licensing

The application and its containg code is open source under the MIT license
and is free for use by those interested.

## Tests and linting

Automated `pytest` functional tests are found in `tests` directory and can
be run with `pytest .`. Linters include `black`, `mypy`, `flake8` and
and some miscelaneous `pre-commit` checkers. Linters can be run with their
respective `name .`. Convenience scripts for running tests and linters can be
found in `utils/` directory.

## Packaging

Detailed instructions for packaging the GUI app for each OS can be found in
the file `pyinstaller_instructions.md`.
