from tkinter import BooleanVar

import customtkinter as ctk

from _types import Presenter


class PopupWindow(ctk.CTkToplevel):
    def __init__(
        self,
        master: ctk.CTk,
        presenter: Presenter,
        text_message: str = "",
        title: str = "",
        *args,
        **kwargs
    ):
        super().__init__(master, *args, **kwargs)
        self.geometry("400x150")
        self.title = title

        self._presenter = presenter
        self.text = text_message
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

    def button_callback(self, confirm: bool) -> None:
        self._presenter.confirm_upload = confirm
        self.close_window()

    def close_window(self) -> None:
        self.grab_release()
        self.destroy()


class ConfirmUpload(PopupWindow):
    def __init__(self, text_message: str):
        pass
