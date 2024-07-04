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


def file_dirs(multiple: bool, title: str) -> tuple[str, ...]:
    if multiple:
        dirs = tuple(filedialog.askdirectory(title=title))
    else:
        dirs = filedialog.askopenfilenames(
            title=title,
            filetypes=SUPPORTED_FILE_TYPES,
        )
        if not isinstance(dirs, tuple):
            dirs = tuple(dirs)
    return dirs


def file_to_binary(dir: str) -> BufferedReader:
    with open(dir, "rb") as file:
        return file
