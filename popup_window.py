import customtkinter as ctk


class PopupWindow(ctk.CTkToplevel):
    def __init__(self, text_message: str = "", title: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x300")

        self.text = text_message
        self.label = ctk.CTkLabel(self, text=self.text)
        self.label.pack()

    def close_window(self) -> None:
        self.grab_release()
        self.destroy()
