import os
import pathlib
from csv import reader
from io import BufferedReader, BytesIO
from tkinter import filedialog


def parse_csv(file: str) -> list[list[str]]:
    data = []
    if not file:
        raise TypeError("No file selected")
    with open(file, newline="", mode="r") as f:
        parse = reader(f, dialect="excel")
        for line in parse:
            data.append(line)

    return data


SUPPORTED_FILE_TYPES = [
    ("Media Files", ".mp4 .m2v .mov .fxr .avi .tiff .png .jpg .tga"),
    ("Video Files", ".mp4 .m2v .mov .fxr .avi"),
    ("Image Files", ".tiff .png .jpg .tga"),
]


def file_dirs(multiple: bool, title: str) -> list[str]:
    if multiple:
        dirs = []
        folder = filedialog.askdirectory(title=title)
        for filename in os.listdir(folder):
            print(filename)
            if (
                suffix := pathlib.Path(filename).suffix
                in SUPPORTED_FILE_TYPES[0][1].split()
            ):
                dirs.append(os.path.join(folder, filename))
        print(dirs)
    else:
        dirs = filedialog.askopenfilenames(
            title=title,
            filetypes=SUPPORTED_FILE_TYPES,
        )
        if isinstance(dirs, tuple):
            dirs = list(*dirs)
        else:
            dirs = []
    return dirs
