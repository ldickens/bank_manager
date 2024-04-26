import requests

from _types import MEDIA_DATA, MEDIA_FILE, MEDIA_MAP, MEDIA_MAP_ENTRY
from endpoint_enums import Endpoints


class Model:
    def __init__(self) -> None:
        self.media: MEDIA_FILE = []
        self.media_map: MEDIA_MAP = []

        self._BASE_URL: str = "http://localhost:40512"

    def rest_request(
        self, endpoint: Endpoints, idx: int = 0
    ) -> MEDIA_MAP | MEDIA_DATA | MEDIA_FILE | None:
        if endpoint is Endpoints.GET_MEDIA_DATA:
            endpoint_url = endpoint.value + f"/{idx}"
        else:
            endpoint_url = endpoint.value

        try:
            full_URL = self.BASE_URL + endpoint_url
            response = requests.get(full_URL)

            if (
                response.status_code == 200
                and "application/json" in response.headers["Content-Type"]
            ):
                return response.json()

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

    def init_media(self) -> None:
        for med in self.media:
            self.rest_request(Endpoints.GET_MEDIA)
