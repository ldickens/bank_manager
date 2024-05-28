from io import BytesIO
from typing import Literal, TypedDict

import requests
from PIL import Image

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


# class MediaThumb(TypedDict):  # Probably not needed anymore seperated the method away from make_request
#     image: str


# class MediaThumbTag(MediaThumb):
#     tag: Literal["MediaThumbType"]


valid_tag_types = MediaFileTypeTag | MediaMapTypeTag | MediaTypeTag

"""
END OF DEFINITIONS
"""


class Model:
    def __init__(self) -> None:
        self.media: list[Media] = []
        self.banks: dict[int, Bank] = {}

        self._BASE_URL: str = "http://127.0.0.1:40512"
        self.media_loaded: bool = False

        # debugging
        # self.debug_banks()
        # self.debug_media()

        self.create_banks()

    @property
    def BASE_URL(self) -> str:
        return self._BASE_URL

    @BASE_URL.setter
    def BASE_URL(self, new_ip: str) -> None:
        self._BASE_URL = new_ip

    def validate_endpoint(
        self, endpoint: Endpoints, media_idx: str = "", map_idx: int = 0
    ) -> tuple[str, str]:
        match endpoint:
            case Endpoints.GET_MEDIA:
                return (endpoint.value, "MediaFileType")

            case Endpoints.GET_MEDIA_MAP:
                return (endpoint.value, "MediaMapType")

            case Endpoints.GET_MEDIA_DATA:
                endpoint_url = endpoint.value + f"{media_idx}"
                return (endpoint_url, "MediaType")

            case Endpoints.GET_THUMB:
                endpoint_url = endpoint.value + f"{media_idx}"
                return (endpoint_url, "")

            case Endpoints.PUT_ENTRY:
                endpoint_url = endpoint.value + f"{map_idx}" + "/" + f"{media_idx}"
                return (endpoint_url, "")

            case Endpoints.DEL_ENTRY:
                endpoint_url = endpoint.value + f"{map_idx}"
                return (endpoint_url, "")

            case _:
                raise NotImplementedError("Endpoint not implemented")

    def make_request(self, endpoint: str, tag: str) -> valid_tag_types | None:
        """
        Includes the REST code and replies with a generic valid type or None.
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

    def thumbnail_request(self, endpoint: str) -> Image.Image | None:

        try:
            full_URL = self.BASE_URL + endpoint
            response = requests.get(full_URL)

            if (
                response.status_code == 200
                and "image/png" in response.headers["Content-Type"]
            ):
                return Image.open(BytesIO(response.content))

            raise ValueError("Response Error")

        except ValueError as e:
            print(f"Error {e}: {response.status_code}-{response.text}")

        except requests.ConnectionError as e:
            print(f"Error: {e}: Could not connect to the target host")

        except OSError as e:
            print(f"Failed to load image: {e}")

    def put_media_entry_request(self, endpoint: str) -> bool | None:

        try:
            full_URL = self.BASE_URL + endpoint
            response = requests.put(full_URL)

            if response.status_code == 200:
                return True

            if response.status_code == 400:
                raise ValueError(response.text)

            if response.status_code == 404:
                raise ValueError(response.text)

            raise requests.ConnectionError(response.status_code, "\n", response.text)

        except requests.ConnectionError as e:
            print(f"Error: {e}: Could not connect to the target host")

        except ValueError as e:
            print(f"Error: {e}")

    def delete_media_entry_request(self, endpoint: str) -> bool | None:
        try:
            full_URL = self.BASE_URL + endpoint
            response = requests.delete(full_URL)

            if response.status_code == 200:
                return True

            if response.status_code == 400:
                raise ValueError(response.text)

            if response.status_code == 404:
                raise ValueError(response.text)

            raise requests.ConnectionError(response.status_code, "\n", response.text)

        except requests.ConnectionError as e:
            print(f"Error: {e}: Could not connect to the target host")

        except ValueError as e:
            print(f"Error: {e}")

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

    def create_banks(self) -> None:
        for x in range(0, 256):
            bank = Bank(x)
            self.banks.update({x: bank})

    def create_media(self, data: MediaTypeTag) -> Media:
        props = []
        sorted_data = [(k, v) for k, v in sorted(data.items())]
        for key, value in sorted_data:
            if key != "tag":
                props.append(value)

        return Media(*props)

    def delete_media(self) -> None:
        self.media = []

    def init_database(self) -> bool:
        if self.media_loaded:
            self.media = []
            self.banks = {}

        if self.init_media():
            return self.init_banks()
        return False

    def init_media(
        self,
    ) -> bool:  # Should inverse the if statements for less indentation
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
                            clip_data = self.make_request(*endpoint)

                        if clip_data != None:
                            valid_clip = self.validate_media_type(clip_data)

                        else:
                            raise AttributeError(f"Failed to get data for {media_id}")

                        if valid_clip != None:
                            self.media.append(self.create_media(valid_clip))
                    self.media_loaded = True
                    return True
        return False

    def init_banks(self) -> bool:
        if len(self.banks) == 0:
            self.create_banks()

        for media in self.media:
            for idx in media.mapIndexes:
                bank, slot = self.calculate_index(idx)
                self.banks[bank].add_clip(media, slot)
        return True

    def get_bank_thumbnail(self, bank: int) -> None:
        for media in self.banks[bank]._media_clips.values():
            if media:
                idx = str(media.iD)
                endpoint = self.validate_endpoint(Endpoints.GET_THUMB, media_idx=idx)
                if endpoint:
                    thumbnail = self.thumbnail_request(endpoint[0])
                    if thumbnail:
                        media.thumbnail = thumbnail

    def push_media_index(self, filename: str, map_idx: int) -> bool:
        media_idx = ""
        for media in self.media:
            # No filename in the import list.
            if filename == "" or filename == "None":
                if not self.banks[map_idx // 256].get_media_clip(map_idx % 256):
                    print(f"Map Entry {map_idx}: Empty")
                    return True

                url = self.validate_endpoint(Endpoints.DEL_ENTRY, map_idx=map_idx)[0]

                if self.delete_media_entry_request(url):
                    print(f"Update Map Entry {map_idx}: Remove Entry Success")
                    return True

            # search for filename in media library stored in local memory
            if filename == media.fileName:
                media_idx = media.iD
                url = self.validate_endpoint(
                    Endpoints.PUT_ENTRY, media_idx=media_idx, map_idx=map_idx
                )[0]

                if self.put_media_entry_request(url):
                    print(f"Update Map Entry {map_idx}: Change Media Success")
                    return True

        print(f"Map Entry {map_idx} - Media not found: {filename}")

        return False

    def calculate_index(self, index: str) -> tuple[int, int]:
        bank, slot = divmod(int(index), 256)
        return (bank, slot)

    def debug_banks(self) -> None:
        for num, bank in self.banks.items():
            print(f"{num}: {bank}\n")

    def debug_media(self) -> None:
        for med in self.media:
            print(f"{med} \n")
