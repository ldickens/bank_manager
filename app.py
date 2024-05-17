import tkinter
import tkinter.filedialog
from re import fullmatch
from tkinter import Event, StringVar
from typing import Any

import customtkinter as ctk
from PIL import Image
from tksheet import Sheet

from _types import Presenter


class App(ctk.CTk):
    def __init__(self, presenter: Presenter) -> None:
        super().__init__()  # type: ignore

        self.geometry("1440x780")
        self.title("Bank Manager")
        self._presenter = presenter

        self.main_frame = MainWindow(self, presenter)
        self.main_frame.pack(expand=True, fill="both")


class MainWindow(ctk.CTkFrame):
    def __init__(self, master, presenter: Presenter, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

        self._presenter = presenter

        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(expand=True, fill="both")

        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.pack(fill="x")

        self.top_frame.grid_rowconfigure(0)
        self.top_frame.grid_rowconfigure(1, weight=1)
        self.top_frame.grid_rowconfigure(2)
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1)
        self.top_frame.grid_columnconfigure(2, weight=1)

        """
        Options
        """
        self.options_frame = OptionsFrame(
            self._presenter, master=self.top_frame, fg_color="transparent"
        )
        self.options_frame.grid_configure(
            column=0, columnspan=3, row=0, sticky="nsew", ipadx=20, ipady=20
        )

        """
        Import Sheet
        """
        self.import_frame = ImportSheet(self.top_frame)
        self.import_frame.grid_configure(
            column=0, row=1, sticky="nsew", ipadx=20, ipady=20
        )

        """
        Details
        """
        self.details_frame = Details(self.top_frame, width=300)
        self.details_frame.grid_configure(
            row=1, column=1, sticky="ew", ipadx=20, ipady=20
        )

        """
        Bank Sheet
        """
        self.bank_frame = BankSheet(self._presenter, master=self.top_frame)
        self.bank_frame.grid_configure(column=2, row=1, sticky="nsew")

        """
        Media Sheet
        """
        self.media_frame = MediaSheet(self.top_frame)
        self.media_frame.grid_configure(column=0, columnspan=3, row=2, sticky="ew")

        """
        Status Bar
        """
        self.status = StatusBar(presenter=presenter, master=self.status_frame)
        self.status.pack(fill="x")


class OptionsFrame(ctk.CTkFrame):
    def __init__(self, presenter: Presenter, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._presenter: Presenter = presenter

        self.validate_pre_edit: str = ""
        self.validate_bank_pre_edit: str = ""

        """
        Import CSV
        """
        self.import_csv_button = ctk.CTkButton(
            self, text="Import CSV", command=self.import_csv_callback
        )
        self.import_csv_button.pack(side="left", pady=5, padx=5)

        """
        Target IP
        """
        self.target_ip_var = StringVar(name="Target IP", value="127.0.0.1")
        self.target_ip_entry = ctk.CTkEntry(
            self,
            textvariable=self.target_ip_var,
        )
        self.target_ip_entry.pack(side="left", pady=5, padx=5)

        self.target_ip_entry.bind("<FocusIn>", self.validate_ip_input_focusin)
        self.target_ip_entry.bind("<FocusOut>", self.validate_ip_input_focusout)
        self.target_ip_entry.bind("<Return>", self.lose_focus_callback)

        """
        Bank Select
        """
        self.bank_select_entry_var = StringVar(name="Bank Select", value="0")
        self.bank_select_entry = ctk.CTkEntry(
            self,
            textvariable=self.bank_select_entry_var,
            validate="key",
            validatecommand=(
                self.register(self.validate_bank_select_entry_keypress),
                "%P",
            ),
        )
        self.bank_select_entry.pack(side="left", pady=5, padx=5)

        self.bank_select_entry.bind(
            "<FocusOut>", self.validate_bank_select_entry_focusout
        )
        self.bank_select_entry.bind(
            "<FocusIn>", self.validate_bank_select_entry_focusin
        )
        self.bank_select_entry.bind("<Return>", self.lose_focus_callback)

        """
        Pull Media
        """
        self.pull_media_button = ctk.CTkButton(
            self, text="Pull", command=self.pull_callback
        )
        self.pull_media_button.pack(side="left", pady=5, padx=5)

    def import_csv_callback(self) -> None:
        self._presenter.import_csv(str(tkinter.filedialog.askopenfilename()))

    def pull_callback(self) -> None:
        self._presenter.pull_media()
        self._presenter.get_thumb()

    def validate_ip_input_focusin(self, event: Event) -> None:
        self.validate_pre_edit = self.target_ip_var.get()

    def validate_ip_input_focusout(self, event: Event) -> None:
        ipv4_pattern = "^(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"

        if not fullmatch(ipv4_pattern, self.target_ip_var.get()):
            self.target_ip_var.set(self.validate_pre_edit)
            self._presenter.show_status("IP not valid")

    def lose_focus_callback(self, event: Event) -> None:
        self.focus()

    def bank_select_entry_callback(self, bank: int) -> None:
        self._presenter.get_bank(bank)

    def validate_bank_select_entry_keypress(self, edit: str) -> bool:
        if not edit.isdigit():
            return False
        return True

    def validate_bank_select_entry_focusin(self, event: Event) -> None:
        self.validate_bank_pre_edit = self.bank_select_entry_var.get()

    def validate_bank_select_entry_focusout(self, event: Event) -> None:
        entry = int(self.bank_select_entry_var.get())
        if entry > 256 or entry < 0:
            self.bank_select_entry_var.set(self.validate_bank_pre_edit)
            self._presenter.show_status("Bank number not valid")
        bank_idx = int(self.bank_select_entry_var.get())
        self._presenter.get_bank(bank_idx)
        self._presenter.get_thumb()


class BankSheet(ctk.CTkFrame):
    def __init__(self, presenter: Presenter, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """
        Bank Sheet
        """
        self._presenter = presenter

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

        self.sheet.enable_bindings(
            "single_select", "arrowkeys", "right_click_popup_menu"
        )
        self.sheet.row_index([x for x in range(256)])

        """
        Bindings
        """

        self.sheet.extra_bindings("all_select_events", func=self.select_event_callback)

        self.sheet.pack(expand=True, fill="both", padx=20, pady=20)

    def select_event_callback(self, _: Event):
        if selected := self.sheet.get_currently_selected():
            row = selected[0]
            self._presenter.get_media_details(row)

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


class Details(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.thumbnail_property = ctk.CTkLabel(
            self, text="", width=128, height=128, fg_color="black"
        )
        self.text_properties = [
            ctk.CTkLabel(self, text="File Name:"),
            ctk.CTkLabel(self, text="File Size:"),
            ctk.CTkLabel(self, text="File Type:"),
            ctk.CTkLabel(self, text="Aspect Ratio:"),
            ctk.CTkLabel(self, text="Audio Channels:"),
            ctk.CTkLabel(self, text="Sample Rate:"),
            ctk.CTkLabel(self, text="Duration:"),
            ctk.CTkLabel(self, text="Frames:"),
            ctk.CTkLabel(self, text="Framerate:"),
            ctk.CTkLabel(self, text="Alpha:"),
            ctk.CTkLabel(self, text="Height:"),
            ctk.CTkLabel(self, text="Width:"),
            ctk.CTkLabel(self, text="Map Indexes:"),
        ]

        self.thumbnail_property.pack()
        self.pack_labels()

    def pack_labels(self) -> None:
        for label in self.text_properties:
            label.pack()

    def set_thumbnail(self, img: Image.Image) -> None:
        thumbnail = ctk.CTkImage(light_image=img, size=(128, 128))
        self.thumbnail_property.configure(image=thumbnail, require_redraw=True)

    def set_properties(self, properties: list[str]) -> None:
        for label, text in zip(self.text_properties, properties):
            new_text = label.cget("text").split(":")[0]
            label.configure(text=new_text + ": " + text, require_redraw=True)

        # self.fileName = ctk.CTkLabel(self, text='File Name:')
        # self.fileSize = ctk.CTkLabel(self, text='File Size:')
        # self.fileType = ctk.CTkLabel(self, text='File Type:')
        # self.aspectRatio = ctk.CTkLabel(self, text='Aspect Ratio:')
        # self.audioChannels = ctk.CTkLabel(self, text='Audio Channels:')
        # self.audioSampleRate = ctk.CTkLabel(self, text='Sample Rate:')
        # self.duration = ctk.CTkLabel(self, text='Duration:')
        # self.durationFrames = ctk.CTkLabel(self, text='Frames:')
        # self.fps = ctk.CTkLabel(self, text='Framerate:')
        # self.hasAlpha = ctk.CTkLabel(self, text='Alpha:')
        # self.height = ctk.CTkLabel(self, text='Height:')
        # self.iD = ctk.CTkLabel(self, text='ID:')
        # self.mapIndexes = ctk.CTkLabel(self, text='Map Indexes:')
        # self.width = ctk.CTkLabel(self, text='Width:')


class ImportSheet(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """
        Import Sheet
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
            displayed_columns=[0],
            all_columns_displayed=False,
            auto_resize_row_index=True,
        )

        self.sheet.enable_bindings()
        self.sheet.row_index([x for x in range(256)])

        self.sheet.pack(expand=True, fill="both", padx=20, pady=20)

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


class MediaSheet(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """
        Import Sheet
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
            show_row_index=False,
            show_vertical_grid=False,
            empty_horizontal=0,
            empty_vertical=0,
            auto_resize_columns=80,
            displayed_columns=[0],
            all_columns_displayed=False,
            auto_resize_row_index=True,
            height=150,
        )

        self.sheet.enable_bindings()
        self.sheet.pack(expand=True, fill="both", padx=20, pady=20)

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
    def __init__(self, presenter: Presenter, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._presenter = presenter
        self.status_var = StringVar()
        self.status = ctk.CTkLabel(self, textvariable=self.status_var)
        self.status.pack(side="right")

    #     # debug buttons
    #     self.button = ctk.CTkButton(self, command=self.get_thumb)
    #     self.button.pack()

    # def get_thumb(self):
    #     self._presenter.get_thumb(
    #         "648c69e2-3879-4971-b3dd-f4c3dc5bf7d0:777b1d6abf7616f1817fa80fc7f8fa4d"
    #    )
