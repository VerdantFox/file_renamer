import pathlib

import setuptools

from file_renamer.src.__init__ import __version__

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setuptools.setup(
    name="file_renamer",
    version=__version__,
    description="Renames all files in a given folder.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/VerdantFox/file_renamer",
    author="Theodore Williams",
    author_email="theodore.f.williams@gmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    python_requires="==3.9",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=["kivy==2.0.0", "pyenchant==3.2.1"],
    entry_points={"console_scripts": ["file_renamer=file_renamer.__main__:main"]},
)
