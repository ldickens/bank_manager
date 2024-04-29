# type definitions
from typing import Protocol

from rest_api import MediaMapType


class Presenter(Protocol):
    def run(self) -> None: ...
    def get_media_map(self) -> MediaMapType | None: ...
    def set_target_ip(self, target_ip: str) -> None: ...
