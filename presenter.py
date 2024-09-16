from __future__ import annotations

from queue import Empty, Full, Queue
from threading import Thread
from time import sleep
from typing import Callable

from PIL import Image

from _types import UITicket
from app import App
from app_state import AppState
from bank import MEDIA_TYPE
from Enums.ticket_enums import UIUpdateReason
from rest_api import Model
from utilities import file_dirs, parse_csv


class Presenter:
    def __init__(self, model: Model) -> None:
        self.model = model
        self.view = App(presenter=self)
        self.current_ip: str = "127.0.0.1"
        self.confirm_upload: bool | None = None
        self.replacement_filename: str = ""
        self.update_ui = Queue()

    def run(self) -> None:
        self.view.mainloop()
        self.get_medsys_state_change()

    def check_queue(self) -> None:
        try:
            ticket: UITicket
            ticket = self.update_ui.get(block=False, timeout=3)

            if ticket.ticket_type == UIUpdateReason.UPDATE_MEDIA_SHEET:
                print("Updating Media sheet")
                self.view.main_frame.media_frame.update_sheet(self.get_media_titles())

            elif ticket.ticket_type == UIUpdateReason.UPDATE_BANK_SHEET:
                print("Updating Bank Sheet")
                if data := self.get_bank():
                    self.update_bank_sheet(data)

            elif ticket.ticket_type == UIUpdateReason.UPDATE_IMPORT_SHEET:
                NotImplementedError()

            elif ticket.ticket_type == UIUpdateReason.UPDATE_STATUS:
                self.view.main_frame.status.set_status_text(ticket.ticket_value)

            elif ticket.ticket_type == UIUpdateReason.UI_STATE:
                self.update_ui_state(ticket.ticket_value)

            elif ticket.ticket_type == UIUpdateReason.DISCONNECT:
                self.disconnect()

            elif ticket.ticket_type == UIUpdateReason.VERIFY_IMPORT_SHEET:
                # checks to see if import sheet entries are in the media_library
                if data := self.view.main_frame.import_frame.sheet.get_column_data(0):
                    data_list = []

                    for item in data:
                        data_list.append([str(item)])
                    self.view.main_frame.import_frame.media_exists(data_list)

            elif ticket.ticket_type == UIUpdateReason.CREATE_UPLOAD_PROGRESS_BAR:
                self.view.main_frame.status.create_progress_bar(
                    int(ticket.ticket_value)
                )
                self.view.main_frame.status.set_uploads_text(
                    total=str(ticket.ticket_value), completed="0"
                )

            elif ticket.ticket_type == UIUpdateReason.SET_WORKING_BAR:
                self.view.main_frame.status.set_state_working_bar(
                    bool(int(ticket.ticket_value))
                )

        except Full:
            self.disconnect()
        except Empty:
            self.disconnect()

    def create_update_bank_sheet_ticket(self) -> None:
        self.ui_ticket_handler(UITicket(UIUpdateReason.UPDATE_BANK_SHEET))

    def init_database(self) -> bool:
        return self.model.init_database()

    def start_threaded_function(self, func: Callable) -> None:
        Thread(target=func, daemon=True).start()

    def pull_media(self) -> None:
        self.start_threaded_function(self._request_get_media)

        # Removed because the run now starts the get_medsys_state_change loop
        self.get_medsys_state_change()

    def _request_get_media(self) -> None:
        if self.view.main_frame.options_frame.target_ip_var.get() != self.current_ip:

            self.set_target_ip(self.view.main_frame.options_frame.target_ip_var.get())

        print("Trying to pull Media")

        self.ui_ticket_handler(UITicket(UIUpdateReason.SET_WORKING_BAR, "1"))

        # This is the main call to the rest_api
        if not self.model.init_database():

            self.ui_ticket_handler(
                UITicket(
                    UIUpdateReason.UPDATE_STATUS, "Failed to connect to remote host"
                )
            )

            self.ui_ticket_handler(UITicket(UIUpdateReason.DISCONNECT))
            return

        # Rest request to get the thumbnails for each media entry
        self.start_thumb_request()

        # Update all the UI elements via the queue
        self.ui_ticket_handler(
            UITicket(UIUpdateReason.UPDATE_STATUS, "Media data retrieved")
        )
        self.ui_ticket_handler(UITicket(UIUpdateReason.UPDATE_MEDIA_SHEET))
        self.ui_ticket_handler(UITicket(UIUpdateReason.UPDATE_BANK_SHEET))
        self.ui_ticket_handler(UITicket(UIUpdateReason.VERIFY_IMPORT_SHEET))
        self.ui_ticket_handler(UITicket(UIUpdateReason.UI_STATE, "connected"))
        self.ui_ticket_handler(UITicket(UIUpdateReason.SET_WORKING_BAR, "0"))

    def ui_ticket_handler(self, ticket: UITicket) -> None:
        self.update_ui.put(ticket)
        self.view.event_generate("<<CheckQueue>>", when="tail")

    def disconnect(self) -> None:
        self.view.main_frame.bank_frame.clear_sheet()
        self.view.main_frame.media_frame.clear_sheet()
        self.view.main_frame.details_frame.clear_properties()
        self.view.main_frame.status.set_state_working_bar(False)
        self.view.main_frame.status.complete_progress()
        self.model.stop_event_listeners()
        self.update_ui_state("disconnected")

    def update_ui_state(self, state: str) -> None:
        if state == "connected":
            self.view.main_frame.bank_frame.toggle_bindings(True)
            self.view.main_frame.media_frame.toggle_bindings(True)
            self.view.main_frame.import_frame.toggle_bindings(True)
            self.view.main_frame.options_frame.state_change(True)
            self.view.main_frame.search_frame.state_change(True)

        elif state == "disconnected":
            self.view.main_frame.bank_frame.toggle_bindings(False)
            self.view.main_frame.media_frame.toggle_bindings(False)
            self.view.main_frame.import_frame.toggle_bindings(False)
            self.view.main_frame.options_frame.state_change(False)
            self.view.main_frame.search_frame.state_change(False)

        else:
            print(f"UI state {state} is not recognised")

    def get_bank(self, bank: int | None = None) -> list[list[str]] | None:
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

        return media_name

    def update_bank_sheet(self, data: list[list[str]]) -> None:
        self.view.main_frame.bank_frame.update_sheet(data)

    def get_media_titles(self) -> list[list[str]]:
        all_titles = []

        for media in self.model.media:
            all_titles.append([media.fileName])

        return all_titles

    def find_and_replace(self, target_title: str) -> None:
        all_titles: list[list[str]] = []
        target_map_indexes: list[str] = []

        for media in self.model.media:
            all_titles.append([media.fileName])
            if media.fileName == target_title:
                target_map_indexes = media.mapIndexes

        print(f"{target_map_indexes=}")

        self.view.create_confirmation_window(
            f"Select a file to replace {target_title}?",
            "Find and replace",
            find_replace=True,
            title_data=all_titles,
        )

        self.threaded_find_and_replace_start(target_map_indexes)

    def threaded_find_and_replace_start(self, target_map_idxs: list[str]) -> None:
        thread = Thread(
            target=self.__threaded_push_media_index_updates,
            args=([*target_map_idxs],),
            daemon=True,
        )
        thread.start()

    def __threaded_push_media_index_updates(self, target_map_idxs: list[str]) -> None:
        while self.confirm_upload == None and self.view.top_level_window:
            sleep(1)

        if self.confirm_upload:
            confirmed = 0

            for map_idx in target_map_idxs:
                if self.model.push_media_index(self.replacement_filename, int(map_idx)):
                    confirmed += 1

            self.view.main_frame.status.set_status_text(
                f"{confirmed} / {len(target_map_idxs)} files changed"
            )

        self.confirm_upload = None

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

    def start_thumb_request(self) -> None:
        bank_idx = int(self.view.main_frame.options_frame.bank_select_entry_var.get())
        Thread(target=self.get_thumb, args=(bank_idx,), daemon=True)

    def get_thumb(self, bank_idx: int) -> None:
        """
        This is a threaded process to retrieve the thumbnails
        TODO: Thread this process
        """
        if not self.model.get_bank_thumbnail(bank_idx):
            self.disconnect()

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
        bank_idx = int(self.view.main_frame.options_frame.bank_select_entry_var.get())
        media_titles = self.view.main_frame.import_frame.sheet.get_column_data(0)

        Thread(
            target=self.push_media_from_csv, args=[bank_idx, media_titles], daemon=True
        ).start()
        self.view.update_idletasks()

    def push_media_from_csv(self, bank_idx: int, media_titles: list[str]) -> None:
        # Start the working progress bar
        self.ui_ticket_handler(UITicket(UIUpdateReason.SET_WORKING_BAR, "1"))

        # Start enumerating through the csv import list and updating the remote
        # media manager with each title.
        # print(f"bank index: {bank_idx}\nmedia_titles: {media_titles}")

        while len(media_titles) < 256:
            media_titles.append("None")

        map_idx = bank_idx * 256

        if bank_idx == 0:  # clip offset for bank 0
            map_idx += 1

        success = 0
        fail = 0
        removed = 0

        for title in media_titles:
            if title == "None" or title == "":

                if self.model.push_media_index(str(title), map_idx):
                    removed += 1

            elif self.model.push_media_index(str(title), map_idx):
                success += 1

            else:
                fail += 1

            map_idx += 1

        # Notify user of status
        self.ui_ticket_handler(
            UITicket(
                UIUpdateReason.UPDATE_STATUS,
                f"File Transfer Complete: Success = {success}, Failure = {fail}, Removed = {removed}",
            )
        )
        self.ui_ticket_handler(
            UITicket(UIUpdateReason.UPDATE_STATUS, f"Transfer Complete")
        )

        # Cancel the working progress bar
        self.ui_ticket_handler(UITicket(UIUpdateReason.SET_WORKING_BAR, "0"))

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
            # self.pull_media()
            # self.get_medsys_state_change()
            self.view.update_idletasks()
            bank_slice = self.view.main_frame.bank_frame.sheet.get_column_data(0)[
                bank_start_idx : len(csv) + bank_end_idx_offset
            ]
            csv = self.view.main_frame.import_frame.sheet.get_column_data(0)
            print(f"bank data: {len(bank_slice)} Items\ncsv data: {len(csv)} Items")
        print("Sheets Synchronised")

    def search_media(
        self, text: str, find_replace: bool = False
    ) -> list[list[str]] | None:
        if not text:
            self.get_media_titles()

        matches = self.model.search_media(text)

        if find_replace:
            return matches

        else:
            self.view.main_frame.status.set_status_text("No Matches")
            self.view.main_frame.media_frame.update_sheet(matches)
            self.view.update_idletasks()

        # if matches := self.model.search_media(text):
        #     self.view.main_frame.media_frame.update_sheet(matches)
        # else:
        #     matches = [[]]
        #     self.view.main_frame.status.set_status_text("No Matches")
        #     self.view.main_frame.media_frame.update_sheet(matches)
        #     self.view.update_idletasks()

    def upload_files(self, folder: bool) -> None:
        filenames = self.get_media_filenames(folder)

        if not len(filenames):  # cancel if no media selected
            return

        self.view.create_confirmation_window(
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
        while self.confirm_upload == None and self.view.top_level_window:
            sleep(1)

        if self.confirm_upload:
            progress_steps = len(filenames)
            AppState._total_steps = progress_steps
            self.ui_ticket_handler(
                UITicket(UIUpdateReason.CREATE_UPLOAD_PROGRESS_BAR, str(progress_steps))
            )
            self.ui_ticket_handler(UITicket(UIUpdateReason.SET_WORKING_BAR, "1"))
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
