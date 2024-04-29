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

        """
        Options
        """
        options_frame = OptionsFrame(self._presenter, self, fg_color="transparent")
        options_frame.pack()

        """
        Sheet
        """
        bank_frame = BankSheet(self)
        bank_frame.pack(expand=True, fill="both")


class OptionsFrame(ctk.CTkFrame):
    def __init__(self, presenter: Presenter, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._presenter: Presenter = presenter

        """
        Target IP
        """
        self.target_ip_var = StringVar(name="Target IP", value="127.0.0.1")
        self.target_ip_entry = ctk.CTkEntry(self, placeholder_text="Target IP")
        self.target_ip_entry.pack(side="left", pady=5, padx=5)

        """
        Bank Select
        """
        self.bank_select_entry_var = StringVar(name="Bank Select", value="0")
        self.bank_select_entry = ctk.CTkComboBox(
            self,
            variable=self.bank_select_entry_var,
            values=[str(num) for num in range(0, 256)],
        )
        self.bank_select_entry.pack(side="left", pady=5, padx=5)

        """
        Pull Media
        """
        self.pull_media_button = ctk.CTkButton(
            self, text="Pull", command=self.pull_callback
        )
        self.pull_media_button.pack(side="left", pady=5, padx=5)

    # def validate_entry_bank_entry_callback(self, input: str) -> bool:
    #     if input.isnumeric():
    #         if 0 <= int(input) < 256:
    #             return True
    #     return False

    def pull_callback(self) -> None:
        self._presenter.set_target_ip(self.target_ip_var.get())
        # self._presenter.get_media_map() #solution is to possible inject the class above into here for access to the props and methods


class BankSheet(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
            auto_resize_columns=80,
            displayed_columns=[0, 2],  # Hide the MediaID Column
            all_columns_displayed=False,
            auto_resize_row_index=True,
        )

        self.sheet.enable_bindings()
        self.sheet.pack(expand=True, fill="both", side="bottom")

    def update_sheet(self, bank_id: int) -> None:
        # self.sheet.set_sheet_data(data=formatters.parse_json(self.media))
        pass
