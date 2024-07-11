# type definitions
from typing import Protocol


class Presenter(Protocol):
    confirm_upload: bool | None

    def run(self) -> None: ...
    def set_target_ip(self, target_ip: str) -> None: ...
    def pull_media(self) -> bool: ...
    def get_bank(self, bank: int | None) -> None: ...
    def show_status(self, msg: str) -> None: ...
    def import_csv(self, file_name: str) -> None: ...
    def populate_import_sheet(self, data: list[list[str]]) -> None: ...
    def get_thumb(self): ...
    def get_media_details(self, row_idx: int) -> None: ...
    def media_in_library(self, media_title: str) -> bool: ...
    def update_bank(self) -> None: ...
    def verify_match(self) -> None: ...
    def search_media(self, text: str) -> None: ...
    def upload_files(self, folder: bool) -> None: ...


class AppState(Protocol):
    _update_media: bool
    _update_system: bool
