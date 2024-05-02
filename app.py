from re import fullmatch
from tkinter import StringVar
from typing import Any

import customtkinter as ctk
from tksheet import Sheet

from _types import Presenter


class App(ctk.CTk):
    def __init__(self, presenter: Presenter) -> None:
        super().__init__()  # type: ignore

        self.geometry("600x500")
        self.title("Bank Manager")
        self._presenter = presenter

        self.main_frame = MainWindow(self, presenter)
        self.main_frame.pack(expand=True, fill="both")


class MainWindow(ctk.CTkFrame):
    def __init__(self, master, presenter: Presenter, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

        self._presenter = presenter

        """
        Options
        """
        self.options_frame = OptionsFrame(
            self._presenter, master=self, fg_color="transparent"
        )
        self.options_frame.pack()

        """
        Sheet
        """
        self.bank_frame = BankSheet(self)
        self.bank_frame.pack(expand=True, fill="both")

        """
        Status Bar
        """
        self.status = StatusBar(self)
        self.status.pack(side="bottom", fill="x")


class OptionsFrame(ctk.CTkFrame):
    def __init__(self, presenter: Presenter, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._presenter: Presenter = presenter

        """
        Target IP
        """
        self.target_ip_var = StringVar(name="Target IP", value="127.0.0.1")
        self.target_ip_entry = ctk.CTkEntry(
            self,
            textvariable=self.target_ip_var,
            validate="focusout",
            validatecommand=(self.register(self.validate_ip_input), "%P", "%s"),
        )
        self.target_ip_entry.pack(side="left", pady=5, padx=5)

        """
        Bank Select
        """
        self.bank_select_entry_var = StringVar(name="Bank Select", value="0")
        self.bank_select_entry = ctk.CTkComboBox(
            self,
            variable=self.bank_select_entry_var,
            values=[str(num) for num in range(0, 256)],
            command=lambda bank: self.bank_select_entry_callback(int(bank)),
        )
        self.bank_select_entry.pack(side="left", pady=5, padx=5)

        """
        Pull Media
        """
        self.pull_media_button = ctk.CTkButton(
            self, text="Pull", command=self.pull_callback
        )
        self.pull_media_button.pack(side="left", pady=5, padx=5)

    def pull_callback(self) -> None:
        self._presenter.pull_media()

    def validate_ip_input(self, edit: str, pre: str) -> bool:
        print("got here")
        if not fullmatch(
            r"\b(?:(?:2(?:[0-4][0-9]|5[0-5])|[0-1]?[0-9]?[0-9])\.){3}(?:(?:2([0-4][0-9]|5[0-5])|[0-1]?[0-9]?[0-9]))\b/ig",
            edit,
        ):
            if pre != "":  # handles startup case where there is no pre-edit
                print("got inside here")
                self.target_ip_var.set(pre)
            return False

        # self._presenter.set_target_ip(self.target_ip_var.get())
        return True

    def bank_select_entry_callback(self, bank: int) -> None:
        self._presenter.get_bank(bank)


class BankSheet(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """
        Table Sheet
        """
        HEADERS = ["File Name"]

        self.sheet = Sheet(
            self,
            name="Bank_Data",
            show_top_left=True,
            headers=HEADERS,  # type: ignore
            show_x_scrollbar=False,
            total_columns=1,
            align="c",
            show_vertical_grid=False,
            empty_horizontal=0,
            empty_vertical=0,
            auto_resize_columns=80,
            displayed_columns=[0],  # Hide the MediaID Column
            all_columns_displayed=False,
            auto_resize_row_index=True,
        )

        self.sheet.enable_bindings()
        self.sheet.pack(expand=True, fill="both", side="bottom")

    def update_sheet(self, data) -> None:
        self.sheet.set_sheet_data(
            data=data,
            reset_col_positions=True,
            reset_row_positions=True,
            redraw=True,
            verify=False,
            reset_highlights=True,
            keep_formatting=False,
            delete_options=True,
        )


class StatusBar(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_var = StringVar()
        self.status = ctk.CTkLabel(self, textvariable=self.status_var)
        self.status.pack(side="right")
