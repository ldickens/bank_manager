from __future__ import annotations

from threading import Thread
from time import sleep

from PIL import Image

from app import App
from app_state import AppState
from bank import MEDIA_TYPE
from rest_api import Model
from utilities import file_dirs, parse_csv


class Presenter:
    def __init__(self, model: Model) -> None:
        self.model = model
        self.view = App(presenter=self)
        self.current_ip: str = "127.0.0.1"
        self.confirm_upload: bool | None = None

    def run(self) -> None:
        self.view.mainloop()

    def init_database(self) -> bool:
        return self.model.init_database()

    def pull_media(self) -> bool:

        if self.view.main_frame.options_frame.target_ip_var.get() != self.current_ip:
            self.set_target_ip(self.view.main_frame.options_frame.target_ip_var.get())

        print("Pulling Media")
        if not self.model.init_database():
            self.show_status("Connection Error: Failed to load media")
            self.view.main_frame.bank_frame.clear_sheet()
            self.view.main_frame.media_frame.clear_sheet()
            return False
        self.show_status("Pull Complete")

        print("Updating Media sheet")
        self.update_media_sheet()

        self.get_bank()

        # checks to see if import sheet entries are in the media_library
        if data := self.view.main_frame.import_frame.sheet.get_column_data(0):
            data_list = []

            for item in data:
                data_list.append([str(item)])
            self.view.main_frame.import_frame.media_exists(data_list)

        self.get_medsys_state_change()

        return True

    def get_bank(self, bank: int | None = None) -> None:
        if not self.model.media_loaded:
            return
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
        print("Updating Bank Sheet")
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
        self.view.main_frame.status.set_status_text(msg)

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
        self.view.update_idletasks()

    def update_bank(self) -> None:
        bank_idx = self.view.main_frame.options_frame.bank_select_entry_var.get()
        media_titles = self.view.main_frame.import_frame.sheet.get_column_data(0)
        print(f"bank index: {bank_idx}\nmedia_titles: {media_titles}")

        while len(media_titles) < 256:
            media_titles.append("None")

        map_idx = int(int(bank_idx) * 256)

        if int(bank_idx) == 0:  # clip offset for bank 0
            map_idx += 1

        success = 0
        fail = 0
        removed = 0

        for title in media_titles:
            if title == "None" or title == "":

                if self.model.push_media_index(str(title), map_idx):
                    removed += 1

            if self.model.push_media_index(str(title), map_idx):
                success += 1

            else:
                fail += 1

            map_idx += 1

        self.show_status("Transfer Complete")
        print(
            f"File Transfer Complete: Success = {success}, Failure = {fail}, Removed = {removed}"
        )

    def verify_match(self) -> None:
        # Update bank sheet after changes
        bank_idx = int(self.view.main_frame.options_frame.bank_select_entry_var.get())
        bank = self.view.main_frame.bank_frame.sheet.get_column_data(0)
        csv = self.view.main_frame.import_frame.sheet.get_column_data(0)

        if bank_idx > 0:
            bank_start_idx = 0
            bank_end_idx_offset = 0
        else:
            bank_start_idx = 1
            bank_end_idx_offset = 1

        bank_slice = bank[bank_start_idx : len(csv) + bank_end_idx_offset]

        while bank_slice != csv:
            sleep(0.5)
            self.pull_media()
            self.view.update_idletasks()
            bank_slice = self.view.main_frame.bank_frame.sheet.get_column_data(0)[
                bank_start_idx : len(csv) + bank_end_idx_offset
            ]
            csv = self.view.main_frame.import_frame.sheet.get_column_data(0)
            print(f"bank data: {len(bank_slice)} Items\ncsv data: {len(csv)} Items")
        print("Sheets Synchronised")

    def search_media(self, text: str) -> None:
        if matches := self.model.search_media(text):
            self.view.main_frame.media_frame.update_sheet(matches)
            return
        self.update_media_sheet()
        self.view.main_frame.status.set_status_text("No Matches")
        self.view.update_idletasks()

    def upload_files(self, folder: bool) -> None:
        filenames = self.get_media_filenames(folder)

        if not len(filenames):  # cancel if no media selected
            return

        self.view.open_window(
            f"Do you want to upload {len(filenames)} files?", "Confirmation"
        )

        self.threaded_media_load_start(filenames)

    def get_media_filenames(self, folder: bool) -> list[str]:
        if folder:
            filenames = file_dirs(folder=True, title="Select a folder...")
        else:
            filenames = file_dirs(folder=False, title="Select files...")

        return filenames

    def threaded_media_load_start(self, filenames: list[str]):
        thread = Thread(
            target=self._threaded_media_load, args=([*filenames],), daemon=True
        )
        thread.start()

    def _threaded_media_load(self, filenames: list[str]) -> None:
        while self.confirm_upload == None:
            sleep(1)

        if self.confirm_upload:
            progress_steps = len(filenames)
            AppState._total_steps = progress_steps
            self.view.main_frame.status.create_progress_bar(progress_steps)
            self.view.main_frame.status.set_uploads_text(
                total=str(progress_steps), completed="0"
            )
            self.view.main_frame.status.set_state_working_bar(True)
            AppState._uploading = True
            for file in filenames:
                self.model.upload_file(file)

        self.confirm_upload = None

    def get_medsys_state_change(self) -> None:
        if AppState._update_system == True:
            print("Disconnecting from host")  # Disconnect from the host.
            AppState._update_system = False

        if AppState._update_media == True:

            AppState._update_media = False
            self.pull_media()  # Pull media since change

            if AppState._uploading == False:
                return

            progress = AppState._progress_steps
            self.view.main_frame.status.progress_bar_step(progress)
            self.view.main_frame.status.set_uploads_text(completed=str(progress))
            self.view.update_idletasks()

            if (
                AppState._progress_steps != 0
                and AppState._progress_steps != 0
                and AppState._progress_steps == AppState._total_steps
            ):
                AppState.reset_uploading()

        self.view.after(2000, self.get_medsys_state_change)
