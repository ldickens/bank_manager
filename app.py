import tkinter
import tkinter.filedialog
from os import getcwd
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
        ctk.set_default_color_theme("\\".join([getcwd(), "theme.json"]))

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
        self.top_frame.grid_rowconfigure(2, weight=1)
        self.top_frame.grid_rowconfigure(3)
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1)
        self.top_frame.grid_columnconfigure(2, weight=1)

        """
        Options
        """
        self.options_frame = OptionsFrame(
            self._presenter, master=self.top_frame, fg_color="transparent"
        )
        self.options_frame.grid_configure(column=0, columnspan=3, row=0, sticky="ns")

        """
        Import Sheet
        """
        self.import_frame = ImportSheet(presenter=presenter, master=self.top_frame)
        self.import_frame.grid_configure(
            column=0, row=1, sticky="nsew", ipadx=20, ipady=20
        )

        """
        Details
        """
        self.details_frame = Details(self.top_frame)
        self.details_frame.grid_configure(
            row=1, column=1, sticky="nsew", ipadx=20, ipady=20
        )

        """
        Bank Sheet
        """
        self.bank_frame = BankSheet(self._presenter, master=self.top_frame)
        self.bank_frame.grid_configure(
            column=2, row=1, sticky="nsew", ipadx=20, ipady=20
        )

        """
        Media Sheet
        """
        self.media_frame = MediaSheet(self.top_frame)
        self.media_frame.grid_configure(column=0, columnspan=3, row=2, sticky="nsew")

        """
        Status Bar
        """
        self.status = StatusBar(presenter=presenter, master=self.status_frame)
        self.status.grid_configure(column=0, columnspan=3, row=3, sticky="ew")


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
        Push Media 
        """
        self.update_bank_button = ctk.CTkButton(
            self, text="Push", command=self.push_media_callback
        )
        self.update_bank_button.pack(side="left", pady=5, padx=5)

        """
        Target IP
        """
        self.target_ip_label = ctk.CTkLabel(self, text="Target IP:")
        self.target_ip_label.pack(side="left", padx=(5, 0), pady=5)

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
        self.target_bank_label = ctk.CTkLabel(self, text="Bank:")
        self.target_bank_label.pack(side="left", padx=(5, 0), pady=5)

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

    def push_media_callback(self) -> None:
        self._presenter.update_bank()
        self._presenter.verify_match()
        self._presenter.get_thumb()

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
            show_vertical_grid=True,
            empty_horizontal=0,
            empty_vertical=0,
            auto_resize_columns=80,
            displayed_columns=[0],  # Hide the MediaID Column
            all_columns_displayed=False,
            auto_resize_row_index=True,
            table_bg="#2c2c2d",  # bg colours
            header_bg="#2c2c2d",
            index_bg="#2c2c2d",
            header_selected_cells_bg="#2c2c2d",
            index_selected_cells_bg="#2c2c2d",
            vertical_scroll_background="#2c2c2d",
            top_left_bg="#2c2c2d",
            header_fg="white",  # fg colours
            table_fg="white",
            index_fg="white",
            header_grid_fg="#202020",
            table_grid_fg="#202020",
            index_grid_fg="#202020",
            header_selected_cells_fg="white",
            index_selected_cells_fg="white",
            table_selected_cells_fg="white",
            outline_thickness=1,  # highlight colours
            outline_color="#474747",
            scrollbar_show_arrows=False,  # Scrollbar options
            scrollbar_theme_inheritance="default",
            vertical_scroll_active_bg="#767679",
            vertical_scroll_not_active_bg="#767679",
            vertical_scroll_pressed_bg="#767679",
            vertical_scroll_troughcolor="#2c2c2d",
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

        self.main_property_frame = ctk.CTkFrame(
            self, fg_color="transparent", border_width=2, corner_radius=10
        )

        self.thumbnail_property = ctk.CTkLabel(
            self.main_property_frame,
            text="",
            width=128,
            height=128,
            fg_color="black",
        )

        # Internal grid for properties
        self.details_props_frame = ctk.CTkFrame(self.main_property_frame, width=400)
        self.details_props_frame.grid_columnconfigure(0)
        self.details_props_frame.grid_columnconfigure(2)
        self.details_props_frame.grid_rowconfigure(0)

        self.property_headers_frame = ctk.CTkFrame(self.details_props_frame)
        self.property_headers_frame.grid_configure(row=0, column=0)

        self.property_details_frame = ctk.CTkFrame(self.details_props_frame)
        self.property_details_frame.grid_configure(row=0, column=1)

        self.property_headers: list[str] = [
            "File Name",
            "File Size",
            "File Type",
            "Aspect Ratio",
            "Audio Channels",
            "Sample Rate",
            "Duration",
            "Frames",
            "Framerate",
            "Alpha",
            "Height",
            "Width",
            "Map Indexes",
        ]

        self.property_details_labels: list[ctk.CTkLabel] = []
        self.property_headers_labels: list[ctk.CTkLabel] = []

        self.main_property_frame.pack(pady=20, fill="both", expand=True)
        self.thumbnail_property.pack(pady=10)
        self.details_props_frame.pack(pady=10)
        self.create_prop_headers(self.property_headers)
        self.create_prop_details()
        self.pack_prop_headers()
        self.pack_prop_details()

    def pack_prop_headers(self) -> None:
        for label in self.property_headers_labels:
            label.pack(fill="x", ipadx=10)

    def pack_prop_details(self) -> None:
        for label in self.property_details_labels:
            label.pack(fill="x", ipadx=10)

    def create_prop_headers(self, headers: list[str]) -> None:
        for x in range(0, 13):
            self.property_headers_labels.append(
                ctk.CTkLabel(
                    self.property_headers_frame,
                    text=f"{headers[x]}:",
                    justify="right",
                    anchor="e",
                    width=100,
                )
            )

    def create_prop_details(self) -> None:
        for _ in range(1, 14):
            self.property_details_labels.append(
                ctk.CTkLabel(
                    self.property_details_frame,
                    text="",
                    width=250,
                )
            )

    def set_thumbnail(self, img: Image.Image) -> None:
        thumbnail = ctk.CTkImage(light_image=img, size=(128, 128))
        self.thumbnail_property.configure(image=thumbnail, require_redraw=True)

    def set_properties(self, properties: list[str]) -> None:
        for label, text in zip(self.property_details_labels, properties):
            if len(text) > 35:
                text = text[0:35] + "..."
            label.configure(text=text, require_redraw=True)


class ImportSheet(ctk.CTkFrame):
    def __init__(self, presenter: Presenter, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """
        Import Sheet
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
            show_vertical_grid=True,
            empty_horizontal=0,
            empty_vertical=0,
            auto_resize_columns=80,
            displayed_columns=[0],
            all_columns_displayed=False,
            auto_resize_row_index=True,
            table_bg="#2c2c2d",  # bg colours
            header_bg="#2c2c2d",
            index_bg="#2c2c2d",
            header_selected_cells_bg="#2c2c2d",
            index_selected_cells_bg="#2c2c2d",
            vertical_scroll_background="#2c2c2d",
            top_left_bg="#2c2c2d",
            header_fg="white",  # fg colours
            table_fg="white",
            index_fg="white",
            header_grid_fg="#202020",
            table_grid_fg="#202020",
            index_grid_fg="#202020",
            header_selected_cells_fg="white",
            index_selected_cells_fg="white",
            table_selected_cells_fg="white",
            outline_thickness=1,  # highlight colours
            outline_color="#2c2c2d",
            scrollbar_show_arrows=False,  # Scrollbar options
            scrollbar_theme_inheritance="default",
            vertical_scroll_active_bg="#767679",
            vertical_scroll_not_active_bg="#767679",
            vertical_scroll_pressed_bg="#767679",
            vertical_scroll_troughcolor="#2c2c2d",
        )

        self.sheet.enable_bindings(
            "single_select", "arrowkeys", "right_click_popup_menu"
        )
        self.sheet.row_index([x for x in range(256)])

        self.sheet.pack(expand=True, fill="both", padx=20, pady=20)

    def update_sheet(self, data: list[list[str]]) -> None:
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
        self.media_exists(data)

    def media_exists(self, data: list[list[str]]) -> None:
        for idx, list in enumerate(data):
            if self._presenter.media_in_library(list[0]):
                self.sheet.span(idx, "highlight", overwrite=True, end=True).highlight(
                    bg="green"
                )
            else:
                self.sheet.span(idx, "highlight", overwrite=True, end=True).highlight(
                    bg="red"
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
            show_top_left=False,
            headers=HEADERS,  # type: ignore
            show_x_scrollbar=False,
            total_columns=1,
            align="c",
            show_row_index=False,
            index=None,
            show_vertical_grid=True,
            empty_horizontal=0,
            empty_vertical=0,
            auto_resize_columns=80,
            displayed_columns=[0],
            all_columns_displayed=False,
            auto_resize_row_index=True,
            height=150,
            table_bg="#2c2c2d",  # bg colours
            header_bg="#2c2c2d",
            index_bg="#2c2c2d",
            header_selected_cells_bg="#2c2c2d",
            index_selected_cells_bg="#2c2c2d",
            vertical_scroll_background="#2c2c2d",
            top_left_bg="#2c2c2d",
            header_fg="white",  # fg colours
            table_fg="white",
            index_fg="white",
            header_grid_fg="#202020",
            table_grid_fg="#202020",
            index_grid_fg="#202020",
            header_selected_cells_fg="white",
            index_selected_cells_fg="white",
            table_selected_cells_fg="white",
            outline_thickness=1,  # highlight colours
            outline_color="#474747",
            scrollbar_show_arrows=False,  # Scrollbar options
            scrollbar_theme_inheritance="default",
            vertical_scroll_active_bg="#767679",
            vertical_scroll_not_active_bg="#767679",
            vertical_scroll_pressed_bg="#767679",
            vertical_scroll_troughcolor="#2c2c2d",
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
        self.status = ctk.CTkLabel(
            self, textvariable=self.status_var, fg_color="transparent"
        )
        self.status.pack(side="right", expand=True, fill="x")

    #     # debug buttons
    #     self.button = ctk.CTkButton(self, command=self.get_thumb)
    #     self.button.pack()

    # def get_thumb(self):
    #     self._presenter.get_thumb(
    #         "648c69e2-3879-4971-b3dd-f4c3dc5bf7d0:777b1d6abf7616f1817fa80fc7f8fa4d"
    #    )
