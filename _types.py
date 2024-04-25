# type definitions
from __future__ import annotations

from abc import ABC, abstractmethod, abstractproperty

from endpoint_enums import Endpoints


class Presenter(ABC):
    @abstractmethod
    def run(self) -> None: ...

    @abstractmethod
    def get_media_map(self) -> None: ...


class App(ABC): ...


class Model:

    @abstractmethod
    def rest_request(self, endpoint: Endpoints) -> MEDIA_MAP | None: ...


MEDIA_DATA = dict[str, int | bool | str | list[int]]
"""
{
    "aspectRatio": 0,
    "audioChannels": 0,
    "audioSampleRate": 0,
    "canBeDeleted": true,
    "duration": 0,
    "durationFrames": 0,
    "fileName": "string",
    "fileSize": 0,
    "fileType": "string",
    "fps": 0,
    "hasAlpha": true,
    "height": 0,
    "iD": "string",
    "mapIndexes": [
        0
    ],
    "timeUploaded": "string",
    "width": 0
}
"""

MEDIA_MAP = dict[str, list[dict[str, str | int]]]
"""
{
    "entries": [
        {
        "index": 0,
        "mediaID": "string",
        "name": "string"
        }
    ]
}
"""

MEDIA_FILE = list[str]
"""
{
    "mediaFiles": [
        {
        "folderPath": "string",
        "mediaID": "string",
        "name": "string"
        }
    ]
}
"""

MEDIA_MAP_ENTRY = list[str | int]
"""
[
    "index": 0,
    "mediaID": "string",
    "name": "string"
]
"""
