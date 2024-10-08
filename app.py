import tkinter
import tkinter.filedialog
from os import path
from re import fullmatch
from tkinter import Event, StringVar
from typing import Any, Callable

import customtkinter as ctk
from PIL import Image
from tksheet import Sheet

from _types import Presenter
from popup_window import PopupWindow


class App(ctk.CTk):
    def __init__(self, presenter: Presenter) -> None:
        super().__init__()

        self.screen_width: int = self.winfo_screenwidth()
        self.screen_height: int = self.winfo_screenheight()
        self._win_width: int = 1440
        self._win_height: int = 900
        self.win_pos_x: int = int((self.screen_width - self._win_width) / 2)
        self.win_pos_y: int = int((self.screen_height - self._win_height) / 2)
        self.geometry(
            f"{str(self._win_width)}x{str(self._win_height)}+{str(self.win_pos_x)}+{str(self.win_pos_y)}"
        )
        self.title("Bank Manager")
        self._presenter = presenter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme(
            path.abspath(path.join(path.dirname(__file__), "theme.json"))
        )

        self.main_frame = MainWindow(self, presenter)
        self.main_frame.pack(expand=True, fill="both")

        self.top_level_window: PopupWindow | None = None

        self.bind("<<CheckQueue>>", self.check_queue)

    def check_queue(self, _: Event) -> None:
        self._presenter.check_queue()

    def create_confirmation_window(
        self,
        text: str,
        title: str,
        find_replace: bool = False,
        title_data: list[list[str]] = [],
    ) -> PopupWindow:
        if self.top_level_window is None or not self.top_level_window.winfo_exists():
            self.top_level_window = PopupWindow(
                self,
                self._presenter,
                text_message=text,
                title=title,
                find_replace=find_replace,
                title_data=title_data,
            )
            self.top_level_window.grab_set()

        else:
            self.top_level_window.focus()

        return self.top_level_window


class MainWindow(ctk.CTkFrame):
    def __init__(self, master, presenter: Presenter, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

        self._presenter = presenter

        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(expand=True, fill="both")

        self.status_frame = ctk.CTkFrame(self, fg_color="#292929", height=30)
        self.status_frame.pack(fill="x")

        self.top_frame.grid_rowconfigure(0)
        self.top_frame.grid_rowconfigure(1, weight=1)
        self.top_frame.grid_rowconfigure(2)
        self.top_frame.grid_rowconfigure(3, weight=1)
        self.top_frame.grid_rowconfigure(4)
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1)
        self.top_frame.grid_columnconfigure(2, weight=1)

        """
        Options
        """
        self.options_outer_frame = ctk.CTkFrame(self.top_frame, fg_color="#292929")
        self.options_outer_frame.grid_configure(
            column=0, columnspan=3, row=0, sticky="nsew"
        )
        self.options_frame = OptionsFrame(
            self._presenter, master=self.options_outer_frame, fg_color="#292929"
        )
        self.options_frame.pack()

        """
        Import Sheet
        """
        self.import_frame = ImportSheet(presenter=presenter, master=self.top_frame)
        self.import_frame.grid_configure(column=0, row=1, sticky="nsew", ipadx=20)

        """
        Details
        """
        self.details_frame = Details(self.top_frame)
        self.details_frame.grid_configure(row=1, column=1, sticky="nsew", ipadx=20)

        """
        Bank Sheet
        """
        self.bank_frame = BankSheet(self._presenter, master=self.top_frame)
        self.bank_frame.grid_configure(column=2, row=1, sticky="nsew", ipadx=20)

        """
        MediaTools Bar """
        self.search_frame = MediaTools(self._presenter, master=self.top_frame)
        self.search_frame.grid_configure(
            column=0, columnspan=3, row=2, sticky="nsew", pady=(0, 10), padx=(20, 10)
        )
        """
        Media Sheet
        """
        self.media_frame = MediaSheet(self.top_frame)
        self.media_frame.grid_configure(column=0, columnspan=3, row=3, sticky="nsew")

        """
        Status Bar
        """
        self.status = StatusBar(
            presenter=presenter,
            master=self.status_frame,
            height=30,
            fg_color="transparent",
        )
        self.status.pack(fill="x", expand=False)


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
            self,
            text="Import CSV",
            command=self.import_csv_callback,
            state="disabled",
        )
        self.import_csv_button.pack(side="left", pady=5, padx=5)

        """
        Push Media 
        """
        self.update_bank_button = ctk.CTkButton(
            self, text="Push", command=self.push_media_callback, state="disabled"
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
        self.target_ip_entry.bind("<Return>", self.return_pull_callback)

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

        # self.bank_select_entry.bind(
        #     "<FocusOut>", self.validate_bank_select_entry_focusout
        # )
        self.bank_select_entry.bind(
            "<FocusIn>", self.validate_bank_select_entry_focusin
        )
        self.bank_select_entry.bind(
            "<Return>", self.validate_bank_select_entry_focusout
        )

        """
        Pull Media
        """
        self.pull_media_button = ctk.CTkButton(
            self, text="Connect", command=self.pull_callback
        )
        self.pull_media_button.pack(side="left", pady=5, padx=5)

    def state_change(self, connected: bool) -> None:
        if connected:
            self.update_bank_button.configure(state="normal")
            self.import_csv_button.configure(state="normal")
            self.target_ip_entry.configure(state="disabled")
            self.pull_media_button.configure(text="Disconnect")
        else:
            self.update_bank_button.configure(state="disabled")
            self.import_csv_button.configure(state="disabled")
            self.target_ip_entry.configure(state="normal")
            self.pull_media_button.configure(text="Connect")

    def push_media_callback(self) -> None:
        self._presenter.update_bank()

    def import_csv_callback(self) -> None:
        self._presenter.import_csv(str(tkinter.filedialog.askopenfilename()))

    def pull_callback(self) -> None:
        if self.pull_media_button.cget("text") == "Connect":
            self._presenter.pull_media()
        else:
            self._presenter.disconnect()

    def return_pull_callback(self, Event: Event) -> None:
        self.lose_focus_callback(Event)
        self.pull_callback()

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
        if edit.isdigit() or edit == "":
            return True
        return False

    def validate_bank_select_entry_focusin(self, event: Event) -> None:
        self.validate_bank_pre_edit = self.bank_select_entry_var.get()

    def validate_bank_select_entry_focusout(self, event: Event) -> None:
        entry = self.bank_select_entry_var.get()
        if entry == "":
            self.bank_select_entry_var.set(self.validate_bank_pre_edit)
        elif int(entry) > 256 or int(entry) < 0:
            self.bank_select_entry_var.set(self.validate_bank_pre_edit)
            self._presenter.show_status("Bank number not valid")

        self._presenter.pull_media()
        # bank_idx = int(self.bank_select_entry_var.get())
        # self._presenter.create_update_bank_sheet_ticket()
        # self._presenter.start_thumb_request()
        self.focus()


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

        self.sheet.row_index([x for x in range(256)])

        """
        Bindings
        """

        self.sheet.extra_bindings("all_select_events", func=self.select_event_callback)
        self.sheet.popup_menu_add_command("Replace...", self.find_and_replace)

        self.sheet.pack(expand=True, fill="both", padx=20, pady=20)

    def toggle_bindings(self, enabled: bool):
        if enabled:
            self.sheet.enable_bindings(
                "single_select", "arrowkeys", "right_click_popup_menu"
            )
        else:
            self.sheet.disable_bindings()

    def find_and_replace(self) -> None:
        if selected_row := self.sheet.get_currently_selected():
            row = selected_row[0]

            # offset by one to adjust  for starting at 0
            cell_data = self.sheet[f"A{row+1}"].data
            title_string = str(cell_data)

            if title_string in ["", "None"]:
                return

            self._presenter.find_and_replace(title_string)

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

    def clear_sheet(self) -> None:
        empty_data = [" " for x in range(0, 256)]
        self.sheet.set_sheet_data(
            data=empty_data,
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
            if len(text) > 30:
                text = text[0:31] + "..."
            label.configure(text=text, require_redraw=True)

    def clear_properties(self) -> None:
        self.thumbnail_property.pack_forget()
        self.details_props_frame.pack_forget()

        for label in self.property_details_labels:
            label.configure(text="", require_redraw=True)

        self.thumbnail_property = ctk.CTkLabel(
            self.main_property_frame,
            text="",
            width=128,
            height=128,
            fg_color="black",
        )

        self.thumbnail_property.pack(pady=10)
        self.details_props_frame.pack(pady=10)


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

        self.sheet.row_index([x for x in range(256)])

        self.sheet.pack(expand=True, fill="both", padx=20, pady=20)

        self.sheet.extra_bindings("FocusOut", lambda: print("FocusOut"))

    def deselect_cells(self, _: Event) -> None:
        self.sheet.deselect(column=0)

    def toggle_bindings(self, enabled: bool):
        if enabled:
            self.sheet.enable_bindings("None")
        else:
            self.sheet.disable_bindings()

    def clear_sheet(self) -> None:
        empty_data = [" " for x in range(0, 256)]
        self.sheet.set_sheet_data(
            data=empty_data,
            reset_col_positions=True,
            reset_row_positions=True,
            redraw=True,
            verify=False,
            reset_highlights=True,
            keep_formatting=False,
            delete_options=True,
        )

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

    HEADERS = ["File Name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """
        Import Sheet
        """

        self.sheet = Sheet(
            self,
            name="Bank_Data",
            show_top_left=False,
            headers=MediaSheet.HEADERS,  # type: ignore
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

        self.sheet.pack(expand=True, fill="both", padx=20, pady=(0, 20))

    def toggle_bindings(self, enabled: bool):
        if enabled:
            self.sheet.enable_bindings("None")
        else:
            self.sheet.disable_bindings()

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

    def clear_sheet(self) -> None:
        self.sheet.reset(table=True)
        self.sheet.headers(MediaSheet.HEADERS)


class StatusBar(ctk.CTkFrame):
    def __init__(self, presenter: Presenter, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._presenter = presenter

        self.status_text_frame = ctk.CTkFrame(
            self, height=30, width=100, fg_color="transparent"
        )
        self.status_text_frame.pack(side="left", expand=False, fill=None)
        self.status = ctk.CTkLabel(
            self.status_text_frame,
            text="",
            width=100,
            fg_color="transparent",
            justify="right",
            anchor="e",
        )
        self.status.pack(expand=True, fill="both", side="left", ipadx=10)

        self.working_bar_frame = ctk.CTkFrame(
            self, height=30, width=100, fg_color="transparent"
        )
        self.working_bar_frame.pack(side="left", expand=False, fill=None)
        self.working_bar = ctk.CTkProgressBar(
            self.working_bar_frame,
            mode="indeterminate",
            indeterminate_speed=1,
            width=40,
        )
        self.working_bar.set(0)

        self.progress_bar_frame = ctk.CTkFrame(
            self, height=30, width=110, fg_color="transparent"
        )
        self.progress_bar_frame.pack(side="right", padx=5, expand=False, fill=None)
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_bar_frame,
            mode="determinate",
            width=100,
            determinate_speed=1,
        )
        self.progress_bar_length: int = 0
        self.uploads_text_var = StringVar(value="0 / 0")
        self.uploads_text = ctk.CTkLabel(
            self.progress_bar_frame,
            textvariable=self.uploads_text_var,
        )

    def set_uploads_text(
        self, completed: str | None = None, total: str | None = None
    ) -> None:
        if completed:
            previous = self.uploads_text_var.get().split("/")
            self.uploads_text_var.set(f"{completed} / {previous[1].strip()}")
        if total:
            previous = self.uploads_text_var.get().split("/")
            self.uploads_text_var.set(f"{previous[0].strip()} / {total}")

    def set_status_text(self, text: str, auto: bool = False) -> None:
        self.status.configure(text=text, require_redraw=True)
        if auto == False:
            self.after(1000, self.set_status_text, " ", True)

    def set_state_working_bar(self, enabled: bool) -> None:
        if enabled:
            self.working_bar.pack(side="left", padx=10)
            self.working_bar.start()
        else:
            self.working_bar.stop()
            self.working_bar.pack_forget()

    def create_progress_bar(self, length: int) -> None:
        self.progress_bar_length = length
        self.progress_bar.set(0)
        self.progress_bar.pack(side="left", padx=5)
        self.uploads_text.pack(side="left", padx=5)

    def progress_bar_step(self, step: int) -> None:
        self.progress_bar.set(
            step / self.progress_bar_length
        )  # ctk progress bar between 0-1
        if self.progress_bar_length == step:  # If complete remove the bar
            self.after(500, self.complete_progress)

    def complete_progress(self) -> None:
        self.progress_bar.pack_forget()
        self.progress_bar.set(0)
        self.progress_bar_length = 0
        self.set_state_working_bar(False)
        self.uploads_text.pack_forget()
        self.uploads_text_var.set("0 / 0")


class MediaTools(ctk.CTkFrame):
    def __init__(self, presenter, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._presenter: Presenter = presenter

        self.upload_file = ctk.CTkButton(
            self,
            text="Upload File...",
            command=self.upload_file_callback,
            state="disabled",
        )
        self.upload_file.pack(side="left", padx=(0, 5))

        self.upload_folder = ctk.CTkButton(
            self,
            text="Upload Folder...",
            command=self.upload_folder_callback,
            state="disabled",
        )
        self.upload_folder.pack(side="left", padx=5)

        self.search_bar_string_var = StringVar()

        self.search_bar = ctk.CTkEntry(
            self,
            placeholder_text="Search",
            width=340,
            textvariable=self.search_bar_string_var,
        )
        self.search_bar.pack(side="right", padx=10)

        self.search_bar.bind("<KeyRelease>", self.search_callback)

        self.search_bar.bind("<Return>", self.lose_focus_callback)

    def upload_file_callback(self) -> None:
        self._presenter.upload_files(folder=False)

    def upload_folder_callback(self) -> None:
        self._presenter.upload_files(folder=True)

    def search_callback(self, event: Event) -> None:
        self._presenter.search_media(self.search_bar.get())

    def lose_focus_callback(self, event: Event) -> None:
        self.focus()

    def state_change(self, connected: bool) -> None:
        if connected:
            self.upload_file.configure(state="normal")
            self.upload_folder.configure(state="normal")
        else:
            self.upload_file.configure(state="disabled")
            self.upload_folder.configure(state="disabled")
