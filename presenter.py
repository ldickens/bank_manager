from __future__ import annotations

from typing import NewType

from PIL import Image

from app import App
from bank import MEDIA_TYPE
from csv_import import parse_csv
from endpoint_enums import Endpoints
from rest_api import Model


class Presenter:
    def __init__(self, model: Model) -> None:
        self.model = model
        self.view = App(presenter=self)
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
                self.show_status("Failed to load media")
        self.update_media_sheet()
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
        self.update_bank_sheet(media_name)

    def update_bank_sheet(self, data: list[list[str]]) -> None:
        self.view.main_frame.bank_frame.update_sheet(data)

    def update_media_sheet(self) -> None:
        all_titles = []
        for media in self.model.media:
            all_titles.append([media.fileName])
        self.view.main_frame.media_frame.update_sheet(all_titles)

    def set_target_ip(self, target_ip: str) -> None:
        self.current_ip = target_ip
        new_url = "http://" + target_ip + ":40512"
        self.model._BASE_URL = new_url

    def show_status(self, msg: str) -> None:
        self.view.main_frame.status.status_var.set(msg)

    def import_csv(self, file_name: str) -> None:
        try:
            data = parse_csv(file_name)
            if len(data) == 0:
                raise ValueError("No Entries Found")
            name_data = []
            for entry in data:
                name_data.append([entry[0]])
            self.populate_import_sheet(name_data)
        except IndexError as e:
            self.show_status("Failed to load file")
        except ValueError as e:
            self.show_status(str(e))
        except TypeError as e:
            self.show_status(str(e))

    def populate_import_sheet(self, data: list[list[str]]) -> None:
        try:
            self.view.main_frame.import_frame.update_sheet(data)
        except TypeError as e:
            self.show_status("Cancelled Load File")

    def media_in_library(self, media_title: str) -> bool:
        for media in self.model.media:
            if media_title == media.fileName:
                return True

        return False

    def get_thumb(self) -> None:
        self.model.get_bank_thumbnail(
            int(self.view.main_frame.options_frame.bank_select_entry_var.get())
        )

    def get_media_details(self, row_idx: int) -> None:
        bank = int(self.view.main_frame.options_frame.bank_select_entry_var.get())
        clip = int(row_idx)
        if media := self.model.banks[bank].get_media_clip(clip):
            if img := media.thumbnail:
                self.set_UI_media_props(img, media.data)

    def set_UI_media_props(
        self, thumbnail: Image.Image, properties: MEDIA_TYPE
    ) -> None:
        formatted_properties = [
            str(properties["fileName"]),
            str(properties["fileSize"]),
            str(properties["fileType"]),
            str(properties["aspectRatio"]),
            str(properties["audioChannels"]),
            str(properties["audioSampleRate"]),
            str(properties["duration"]),
            str(properties["durationFrames"]),
            "frames TBD",
            str(properties["hasAlpha"]),
            str(properties["height"]),
            str(properties["width"]),
            str(properties["mapIndexes"]),
        ]
        self.view.main_frame.details_frame.set_thumbnail(thumbnail)
        self.view.main_frame.details_frame.set_properties(formatted_properties)
