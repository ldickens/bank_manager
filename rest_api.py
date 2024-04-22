from enum import Enum
from typing import NewType

import requests

from _types import MEDIA_MAP

_BASE_URL = "http://localhost:40512"


class Model:
    def rest_request(self, endpoint: Enum) -> MEDIA_MAP | None:
        try:
            full_URL = _BASE_URL + endpoint.value
            response = requests.get(full_URL)

            if (
                response.status_code == 200
                and "application/json" in response.headers["Content-Type"]
            ):
                return response.json()

            print(f"Error: {response.status_code}-{response.text}")

        except ConnectionError as e:
            print(f"Error: {e}")
