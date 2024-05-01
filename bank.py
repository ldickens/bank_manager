from __future__ import annotations

import collections
from typing import OrderedDict

MEDIA_TYPE = list[int | str | bool | list[str]]

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

    @property
    def media_clips(self, *args):
        



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

        self._data: MEDIA_TYPE = []

    @property
    def data(self, *args) -> MEDIA_TYPE:
        for key in args:
            print(key)
        return [
            self.aspectRatio,
            self.audioChannels,
            self.audioSampleRate,
            self.canBeDeleted,
            self.duration,
            self.durationFrames,
            self.fileName,
            self.fileSize,
            self.fileType,
            self.hasAlpha,
            self.height,
            self.iD,
            self.mapIndexes,
            self.timeUploaded,
            self.width,
        ]

    def __repr__(self) -> str:
        return str(self.data)
