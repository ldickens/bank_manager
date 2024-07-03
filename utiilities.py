from csv import reader
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


SUPPORTED_FILE_TYPES = [("Video Files", ".mp4 .m2v .mov .fxr .avi")]


def open_files(multiple: bool, title: str) -> list[str]:
    if multiple:
        dirs = filedialog.askdirectory()
    else:
        dirs = filedialog.askopenfilenames(
            title=title,
            filetypes=SUPPORTED_FILE_TYPES,
        )
    return list(dirs)
