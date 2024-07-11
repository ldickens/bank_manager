import os
import pathlib
from csv import reader
from tkinter import filedialog

from psutil import net_if_addrs


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


def file_dirs(folder: bool, title: str) -> list[str]:
    dirs_list = []
    if folder:
        dir = filedialog.askdirectory(title=title)
        if not dir:
            return []

        for filename in os.listdir(dir):
            print(filename)
            if pathlib.Path(filename).suffix in SUPPORTED_FILE_TYPES[0][1].split():
                dirs_list.append(os.path.join(dir, filename))
    else:
        dirs = filedialog.askopenfilenames(
            title=title,
            filetypes=SUPPORTED_FILE_TYPES,
        )
        if isinstance(dirs, tuple):
            for dir in dirs:
                dirs_list.append(dir)

    return dirs_list


def get_nic_addrs() -> list[str]:
    addrs = net_if_addrs()
    ip_list = []
    for entry in addrs:
        for interface in addrs[entry]:
            print(interface.family)
            if interface.family == "<AddressFamily.AF_INET: 2>":
                ip_list.append(interface.address)
    return ip_list
