from tkinter import StringVar
from typing import Any

import customtkinter as ctk
from tksheet import Sheet

from _types import Presenter


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()  # type: ignore

        self.geometry("600x500")
        self.title("Bank Manager")

    def init_ui(self, presenter: Presenter) -> None:
        MainWindow(self, presenter).pack(expand=True, fill="both")


class MainWindow(ctk.CTkFrame):
    def __init__(self, master, presenter: Presenter, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

        self._presenter = presenter
        BANKS = [str(n) for n in range(256)]
        self.media: Any = []  # change once implemented

        """
        Options
        """
        """
        Target IP
        """
        self.target_ip_var = StringVar(name="Target IP", value="127.0.0.1")
        self.target_ip_entry = ctk.CTkEntry(self, placeholder_text="Target IP")
        self.target_ip_entry.pack(side="left")

        """
        Pull Media
        """
        self.pull_media_button = ctk.CTkButton(
            self, text="Pull", command=self.pull_callback
        )
        self.pull_media_button.pack(side="left")

        """
        Bank Select
        """
        self.bank_select_entry_var = StringVar(name="Bank Select", value="0")
        self.bank_select_entry = ctk.CTkComboBox(
            self, values=BANKS, variable=self.bank_select_entry_var
        )
        self.bank_select_entry.pack(side="left")

        """
        Table Sheet
        """
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
        self.sheet.pack(expand=True, fill="both", side="bottom")

    def pull_callback(self) -> None:
        # self._presenter.set_target_ip(self.target_ip_var.get())
        # self.media_map = self._presenter.get_media_map()
        pass

    def update_sheet(self, bank_id: int) -> None:
        # self.sheet.set_sheet_data(data=formatters.parse_json(self.media))
        pass
