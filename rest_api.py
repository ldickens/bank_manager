import requests

from _types import MEDIA_DATA, MEDIA_FILE, MEDIA_MAP, MEDIA_MAP_ENTRY
from bank import Bank, Media
from endpoint_enums import Endpoints


class Model:
    def __init__(self) -> None:
        self.media: MEDIA_FILE = []
        self.banks: dict[int, Bank] = {}

        for x in range(0, 256):
            bank = Bank(x)
            self.banks.update({x: bank})

        self._BASE_URL: str = "http://localhost:40512"

        self.init_media()

        # debugging
        self.debug_banks()

    def rest_request(
        self, endpoint: Endpoints, idx: str = ""
    ) -> list[dict[str, str | int | list[int]]] | None:
        match endpoint:
            case Endpoints.GET_MEDIA | Endpoints.GET_MEDIA_MAP:
                return self.get_media(endpoint.value)
            case Endpoints.GET_MEDIA_DATA:
                endpoint_url = endpoint.value + f"/{idx}"
                return self.get_media_data(endpoint_url)
            case _:
                raise ValueError("Invalid Endpoint")

    def get_media(
        self, endpoint_url: str
    ) -> list[dict[str, str | int | list[int]]] | None:
        try:
            full_URL = self.BASE_URL + endpoint_url
            response = requests.get(full_URL)

            if (
                response.status_code == 200
                and "application/json" in response.headers["Content-Type"]
            ):
                return response.json()[0]

            print(f"Error: {response.status_code}-{response.text}")

        except requests.ConnectionError as e:
            print(f"Error: {e}: Could not connect to the target host")

    def get_media_data(
        self, endpoint_url: str
    ) -> list[dict[str, str | int | list[int]]] | None:
        try:
            full_URL = self.BASE_URL + endpoint_url
            response = requests.get(full_URL)

            if (
                response.status_code == 200
                and "application/json" in response.headers["Content-Type"]
            ):
                return [response.json()]

            print(f"Error: {response.status_code}-{response.text}")

        except requests.ConnectionError as e:
            print(f"Error: {e}: Could not connect to the target host")

    # Is this required
    @property
    def BASE_URL(self) -> str:
        return self._BASE_URL

    # Add an IP address regex filter or look for a means of validating an IP address.
    @BASE_URL.setter
    def BASE_URL(self, new_ip: str) -> None:
        self._BASE_URL = new_ip

    def delete_media(self) -> None:
        self.media = []

    def init_media(self) -> None:
        media_library = self.rest_request(Endpoints.GET_MEDIA)
        if media_library != None:
            for entry in media_library:
                data = self.rest_request(
                    Endpoints.GET_MEDIA_DATA, str(entry["mediaID"])
                )
                if data != None:
                    new_media = Media(**data[0])  # Here is the type safety issue

                    for bank, slot in new_media.get_converted_idx():
                        self.banks[bank].add_clip(new_media, slot)

    def debug_banks(self) -> None:
        for bank in self.banks.values():
            print(bank)
