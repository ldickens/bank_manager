import customtkinter as ctk
from tksheet import Sheet

import formatters
from _types import Presenter


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()  # type: ignore

        self._presenter: Presenter

        self.geometry("600x500")
        self.title("Bank Manager")

        HEADERS = ["Index", "MediaID", "Name"]

        self.sheet = Sheet(
            self,
            name="Bank_Data",
            show_top_left=False,
            headers=HEADERS,  # type: ignore
            show_x_scrollbar=False,
            total_columns=3,
            align="c",
            show_vertical_grid=False,
            empty_horizontal=0,
            empty_vertical=0,
            auto_resize_columns=50,
            displayed_columns=[0, 2],  # Hide the MediaID Column
            all_columns_displayed=False,
            auto_resize_row_index=True,
        )

        self.sheet.enable_bindings()
        self.get_media()
        self.sheet.pack(expand=True, fill="both")

    def init_ui(self, presenter: Presenter) -> None:
        self._presenter = presenter

    def get_media(self) -> None:
        media_map = self._presenter.get_media_map()
        if media_map != None:
            self.sheet.set_sheet_data(data=formatters.parse_json(media_map))
