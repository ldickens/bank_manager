from __future__ import annotations

from app import App
from endpoint_enums import Endpoints
from rest_api import Model


class Presenter:
    def __init__(self, view: App, model: Model) -> None:
        self.view = view
        self.model = model

    def run(self) -> None:
        self.view.init_ui(self)
        self.view.mainloop()

    def get_media_map(self) -> None:
        self.model.rest_request(Endpoints.GET_MEDIA_MAP)
