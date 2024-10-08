from __future__ import annotations

import collections
from re import A
from typing import OrderedDict

from PIL import Image

MEDIA_TYPE = dict[str, int | str | bool | list[str]]


class Bank:
    def __init__(self, bank: int) -> None:
        self.bank: int = bank
        self._media_clips: OrderedDict[int, Media | None] = collections.OrderedDict()

        for num in range(0, 256):
            self._media_clips[num] = None

    def add_clip(self, media: Media, slot: int) -> None:
        self._media_clips.update({slot: media})

    def __repr__(self) -> str:
        output = ""
        for idx, media in self._media_clips.items():
            if media != None:
                output += f"Slot: {idx} -- {str(repr(media))}\n"

        return output

    def get_media_clip(self, idx: int) -> Media | None:
        if media := self._media_clips[idx]:
            return media

    @property
    def media_clips(self) -> list[MEDIA_TYPE]:
        media_data = []
        for media in self._media_clips.values():
            if isinstance(media, Media):
                media_data.append(media.data)
            else:
                media_data.append({"0": 0})

        return media_data


class Media:
    def __init__(
        self,
        aspectRatio: int = 0,
        audioChannels: int = 0,
        audioSampleRate: int = 0,
        canBeDeleted: bool = True,
        duration: int = 0,
        durationFrames: int = 0,
        fileName: str = "",
        fileSize: int = 0,
        fileType: str = "",
        fps: int = 0,
        hasAlpha: bool = True,
        height: int = 0,
        iD: str = "",
        mapIndexes: list[str] = [],
        timeUploaded: str = "",
        width: int = 0,
        thumbnail: bytearray | None = None,
    ) -> None:

        self.aspectRatio: int = aspectRatio
        self.audioChannels: int = audioChannels
        self.audioSampleRate: int = audioSampleRate
        self.canBeDeleted: bool = canBeDeleted
        self.duration: int = duration
        self.durationFrames: int = durationFrames
        self.fileName: str = fileName
        self.fileSize: int = fileSize
        self.fileType: str = fileType
        self.fps: int = fps
        self.hasAlpha: bool = hasAlpha
        self.height: int = height
        self.iD: str = iD
        self.mapIndexes: list[str] = mapIndexes
        self.timeUploaded: str = timeUploaded
        self.width: int = width
        self._thumbnail: Image.Image | None = None

        self._data: MEDIA_TYPE = {}

    @property
    def data(self, *args) -> MEDIA_TYPE:
        for key in args:
            print(key)
        return {
            "aspectRatio": self.aspectRatio,
            "audioChannels": self.audioChannels,
            "audioSampleRate": self.audioSampleRate,
            "canBeDeleted": self.canBeDeleted,
            "duration": self.duration,
            "durationFrames": self.durationFrames,
            "fileName": self.fileName,
            "fileSize": self.fileSize,
            "fileType": self.fileType,
            "hasAlpha": self.hasAlpha,
            "height": self.height,
            "iD": self.iD,
            "mapIndexes": self.mapIndexes,
            "timeUploaded": self.timeUploaded,
            "width": self.width,
        }

    @property
    def thumbnail(self) -> Image.Image | None:
        return self._thumbnail

    @thumbnail.setter
    def thumbnail(self, img: Image.Image) -> None:
        self._thumbnail = img

    def __repr__(self) -> str:
        return str(self.data)
