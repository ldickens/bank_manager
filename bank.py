from __future__ import annotations

from _types import MEDIA


class Bank:
    def __init__(self, bank: int) -> None:
        self.bank: int = bank
        self._media_clips: dict[int, Media] = {}

    def add_clip(self, media: Media, slot: int) -> None:
        self._media_clips.update({slot: media})

    def __repr__(self) -> str:
        output = ""
        for idx, media in self._media_clips.items():
            output += f"Slot: {idx} -- {str(repr(media))}"

        return output

    def __str__(self) -> str:
        pass


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
        mapIndexes: list[int] = [],
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
        self.mapIndexes: list[int] = mapIndexes
        self.timeUploaded: str = timeUploaded
        self.width: int = width

        self._data: list[int | str | bool | list[int]] = []

    @property
    def data(self) -> MEDIA:
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
            self.fps,
            self.hasAlpha,
            self.height,
            self.iD,
            self.mapIndexes,
            self.timeUploaded,
            self.width,
        ]

    def get_converted_idx(self) -> list[tuple[int, int]]:
        banks = []
        for idx in self.mapIndexes:
            bank_slot = divmod(idx, 256)
            banks.append(bank_slot)

        return banks

    def __repr__(self) -> list[int | str | bool | list[int]]:
        return self.data

    def __str__(self) -> str:
        pass
