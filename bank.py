from _types import MEDIA


class Bank:
    def __init__(self, bank: int, data: list[list[str]]) -> None:
        self.bank: int = bank
        self._media_clips: dict[int, Media] = {}


class Media(Bank):
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
