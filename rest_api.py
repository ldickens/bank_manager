from typing import Literal, TypedDict

import requests

from bank import Bank, Media
from endpoint_enums import Endpoints

"""
TYPE DEFINITIONS: 

JSON responses from the Hippo REST API
"""


class MediaType(TypedDict):
    aspectRatio: int
    audioChannels: int
    audioSampleRate: int
    canBeDeleted: bool
    duration: int
    durationFrames: int
    fileName: str
    fileSize: int
    fileType: str
    fps: int
    hasAlpha: bool
    height: int
    iD: str
    mapIndexes: list[str]
    timeUploaded: str
    width: int


class MediaTypeTag(MediaType):
    tag: Literal["MediaType"]


class MapType(TypedDict):
    index: int
    mediaID: str
    name: str


class MediaMapType(TypedDict):
    entries: list[MapType]


class MediaMapTypeTag(MediaMapType):
    tag: Literal["MediaMapType"]


class FileType(TypedDict):
    folderPath: str
    mediaID: str
    name: str


class MediaFileType(TypedDict):
    mediaFiles: list[FileType]


class MediaFileTypeTag(MediaFileType):
    tag: Literal["MediaFileType"]


valid_tag_types = MediaFileTypeTag | MediaMapTypeTag | MediaTypeTag

"""
END OF DEFINITIONS
"""


class Model:
    def __init__(self) -> None:
        self.media: list[Media] = []
        self.banks: dict[int, Bank] = {}

        for x in range(0, 256):
            bank = Bank(x)
            self.banks.update({x: bank})

        self._BASE_URL: str = "http://localhost:40512"
        self.media_loaded: bool = False

        self.media_loaded = self.init_media()
        if self.media_loaded:
            self.init_banks()

        # debugging
        # self.debug_banks()
        # self.debug_media()

    @property
    def BASE_URL(self) -> str:
        return self._BASE_URL

    # Add an IP address regex filter or look for a means of validating an IP address.
    @BASE_URL.setter
    def BASE_URL(self, new_ip: str) -> None:
        self._BASE_URL = new_ip

    def validate_endpoint(self, endpoint: Endpoints, idx: str = "") -> tuple[str, str]:
        match endpoint:
            case Endpoints.GET_MEDIA:
                return (endpoint.value, "MediaFileType")

            case Endpoints.GET_MEDIA_MAP:
                return (endpoint.value, "MediaMapType")

            case Endpoints.GET_MEDIA_DATA:
                endpoint_url = endpoint.value + f"/{idx}"
                return (endpoint_url, "MediaType")

            case _:
                raise NotImplementedError("Endpoint not implemented")

        # method below is experiment

    def make_request(self, endpoint: str, tag: str) -> valid_tag_types | None:
        """
        Includes the REST code and replies with a generic dict
        """
        try:
            full_URL = self.BASE_URL + endpoint
            response = requests.get(full_URL)

            if (
                response.status_code == 200
                and "application/json" in response.headers["Content-Type"]
            ):
                d_obj = response.json()
                d_obj.update({"tag": tag})
                return d_obj

            raise ValueError("Response Error")

        except ValueError as e:
            print(f"Error {e}: {response.status_code}-{response.text}")

        except requests.ConnectionError as e:
            print(f"Error: {e}: Could not connect to the target host")

    def validate_media_type(self, data: valid_tag_types) -> MediaTypeTag | None:
        if data["tag"] == "MediaType":
            return data

    def validate_media_map_type(self, data: valid_tag_types) -> MediaMapTypeTag | None:
        if data["tag"] == "MediaMapType":
            return data

    def validate_media_file_type(
        self, data: valid_tag_types
    ) -> MediaFileTypeTag | None:
        if data["tag"] == "MediaFileType":
            return data

    def create_media(self, data: MediaTypeTag) -> Media:
        props = []
        sorted_data = [(k, v) for k, v in sorted(data.items())]
        for key, value in sorted_data:
            if key != "tag":
                props.append(value)

        return Media(*props)

    def delete_media(self) -> None:
        self.media = []

    def init_media(self) -> bool:
        endpoint = self.validate_endpoint(Endpoints.GET_MEDIA)
        if endpoint != None:
            media_data = self.make_request(*endpoint)

            if media_data != None:
                valid_media = self.validate_media_file_type(media_data)

                if valid_media != None:
                    for file in valid_media["mediaFiles"]:
                        media_id = file["mediaID"]
                        endpoint = self.validate_endpoint(
                            Endpoints.GET_MEDIA_DATA, media_id
                        )

                        if endpoint != None:
                            media_data = self.make_request(*endpoint)

                        if media_data != None:
                            valid_clip = self.validate_media_type(media_data)

                        else:
                            raise Exception(f"Failed to get data for {media_id}")

                        if valid_clip != None:
                            self.media.append(self.create_media(valid_clip))
                            return True
        return False

    def init_banks(self) -> None:
        for media in self.media:
            for idx in media.mapIndexes:
                bank, slot = self.calculate_index(idx)
                self.banks[bank].add_clip(media, slot)

    def calculate_index(self, index: str) -> tuple[int, int]:
        bank, slot = divmod(int(index), 256)
        return (bank, slot)

    def debug_banks(self) -> None:
        for num, bank in self.banks.items():
            print(f"{num}: {bank}\n")

    def debug_media(self) -> None:
        for med in self.media:
            print(f"{med} \n")

    def get_bank_data(self, **kwargs) -> 