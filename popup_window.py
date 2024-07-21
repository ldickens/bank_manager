from __future__ import annotations

from tkinter import BooleanVar, Event

import customtkinter as ctk
from tksheet import Sheet

from _types import Presenter


class PopupWindow(ctk.CTkToplevel):
    def __init__(
        self,
        master: ctk.CTk,
        presenter: Presenter,
        text_message: str = "",
        title: str = "",
        find_replace: bool = False,
        title_data: list[list[str]] = [],
        *args,
        **kwargs,
    ):
        super().__init__(master, *args, **kwargs)
        self.geometry("400x150")
        self.title = title
        self.find_replace = find_replace
        self.title_data = title_data

        self._presenter = presenter
        self.text = text_message
        self.selected_filename: str = ""
        self.media_sheet: TitleSheet
        self.search_bar: ctk.CTkEntry

        self.label = ctk.CTkLabel(self, text=self.text, pady=30)
        self.label.pack()

        self.confirmation_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.confirmation_frame.pack()

        self.yes_button = ctk.CTkButton(
            self.confirmation_frame,
            text="Yes",
            command=lambda: self.button_callback(True),
        )
        self.no_button = ctk.CTkButton(
            self.confirmation_frame,
            text="No",
            command=lambda: self.button_callback(False),
        )

        self.yes_button.pack(side="left", padx=10)
        self.no_button.pack(side="left", padx=10)

        if self.find_replace == True:
            self.geometry("400x400")
            self.media_sheet = self._create_sheet(self.title_data)
            self._set_bindings()
            self.search_bar = self._create_search_bar()
            self.search_bar.pack(padx=10, pady=10)
            self.media_sheet.pack(padx=10, pady=10)

    def _create_search_bar(self) -> ctk.CTkEntry:
        search_bar = ctk.CTkEntry(
            self,
            placeholder_text="Search",
            width=340,
        )

        search_bar.bind("<KeyRelease>", self.search_callback)

        search_bar.bind("<Return>", self.lose_focus_callback)

        return search_bar

    def search_callback(self, _: Event) -> None:
        if matches := self._presenter.search_media(
            self.search_bar.get(), find_replace=True
        ):
            self.media_sheet.update_sheet(matches)
        else:
            # clear sheet content when no matches found
            self.media_sheet.update_sheet([[]])

    def lose_focus_callback(self, _: Event) -> None:
        self.focus()

    def _set_bindings(self) -> None:
        self.media_sheet.sheet.extra_bindings(
            "all_select_events", func=self.select_event_callback
        )

    def _create_sheet(self, title_data: list[list[str]]) -> TitleSheet:
        title_sheet = TitleSheet(self)
        title_sheet.update_sheet(title_data)
        return title_sheet

    def select_event_callback(self, _: Event):
        if selected := self.media_sheet.sheet.get_currently_selected():
            row = selected[0]
            self.selected_filename = str(self.media_sheet.sheet[f"A{row+1}"].data)

    def button_callback(self, confirm: bool) -> None:
        self._presenter.confirm_upload = confirm

        if confirm and self.find_replace:
            self._presenter.replacement_filename = self.selected_filename

        self.close_window()

    def close_window(self) -> None:
        self.grab_release()
        self.destroy()


class TitleSheet(ctk.CTkFrame):

    HEADERS = ["File Name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """
        TitleSheet
        """

        self.sheet = Sheet(
            self,
            name="Bank_Data",
            show_top_left=False,
            headers=TitleSheet.HEADERS,  # type: ignore
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

        self.sheet.pack(expand=True, fill="both")

        self.sheet.enable_bindings(
            "single_select",
            "arrowkeys",
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
