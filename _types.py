from queue import Queue
from typing import Protocol

from Enums.ticket_enums import UIUpdateReason


class Presenter(Protocol):
    confirm_upload: bool | None
    replacement_filename: str
    update_ui: Queue

    def run(self) -> None: ...
    def set_target_ip(self, target_ip: str) -> None: ...
    def pull_media(self) -> None: ...

    def _request_get_media(self) -> None: ...
    def get_bank(self, bank: int | None = None) -> list[list[str]] | None: ...

    def show_status(self, msg: str) -> None: ...
    def import_csv(self, file_name: str) -> None: ...
    def populate_import_sheet(self, data: list[list[str]]) -> None: ...
    def start_thumb_request(self) -> None: ...
    def get_thumb(self, bank_idx: int): ...
    def get_media_details(self, row_idx: int) -> None: ...
    def media_in_library(self, media_title: str) -> bool: ...
    def update_bank(self) -> None: ...
    def verify_match(self) -> None: ...
    def search_media(
        self, text: str, find_replace: bool = False
    ) -> list[list[str]] | None: ...
    def upload_files(self, folder: bool) -> None: ...
    def update_ui_state(self, state: str) -> None: ...
    def disconnect(self) -> None: ...
    def find_and_replace(self, target_title: str) -> None: ...

    def check_queue(self) -> None: ...
    def create_update_bank_sheet_ticket(self) -> None: ...


class AppState(Protocol):
    _update_media: bool
    _update_system: bool

    _uploading: bool = False
    _progress_steps: int = 0
    _total_steps: int = 0

    @staticmethod
    def reset_uploading() -> None: ...


class UITicket:
    def __init__(self, ticket_type: UIUpdateReason, ticket_value: str = ""):

        self.ticket_type: UIUpdateReason = ticket_type
        self.ticket_value: str

        if ticket_value:
            self.ticket_value = ticket_value
