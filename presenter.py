from __future__ import annotations

from app import App
from csv_import import parse_csv
from endpoint_enums import Endpoints
from rest_api import Model


class Presenter:
    def __init__(self, model: Model) -> None:
        self.model = model
        self.view = App(self)
        self.current_ip: str = "127.0.0.1"

    def run(self) -> None:
        self.view.mainloop()

    def init_database(self) -> bool:
        return self.model.init_database()

    def pull_media(self) -> None:
        if self.view.main_frame.options_frame.target_ip_var.get() != self.current_ip:
            self.set_target_ip(self.view.main_frame.options_frame.target_ip_var.get())
        if not self.model.media_loaded:
            if not self.model.init_database():
                self.view.main_frame.status_frame.status_var.set("Failed to load media")
        self.get_bank()

    def get_bank(self, bank: int | None = None) -> None:
        if bank == None:
            idx = int(self.view.main_frame.options_frame.bank_select_entry_var.get())
        else:
            idx = bank

        bank_data = self.model.banks[idx].media_clips

        media_name = []
        for media in bank_data:
            if "0" in media.keys():
                media_name.append(["None"])
            else:
                media_name.append([media["fileName"]])
        self.update_sheet(media_name)

    def update_sheet(self, data: list[list[str]]) -> None:
        self.view.main_frame.bank_frame.update_sheet(data)

    def set_target_ip(self, target_ip: str) -> None:
        self.current_ip = target_ip
        new_url = "http://" + target_ip + ":40512"
        self.model._BASE_URL = new_url

    def show_status(self, msg: str) -> None:
        self.view.main_frame.status.status_var.set(msg)

    def import_csv(self, file_name: str) -> None:
        data = parse_csv(file_name)
        name_data = []
        for entry in data:
            name_data.append([entry[0]])
        self.populate_import_sheet(name_data)

    def populate_import_sheet(self, data: list[list[str]]) -> None:
        try:
            self.view.main_frame.import_frame.update_sheet(data)
        except TypeError as e:
            self.show_status("Cancelled Load File")
