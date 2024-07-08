import asyncio
from json import dumps

import websockets.sync.client as webclient
from websockets.exceptions import ConnectionClosed


class EventListener:
    MEDIA = "MEDIA"
    SYSTEM = "SYSTEM"
    PRESETS = "PRESETS"
    PREFIX = "ws://"
    PORT = 40513

    def __init__(
        self,
        media_callback: bool = False,
        system_callback: bool = False,
        preset_callback: bool = False,
        ip_address: str = "localhost",
    ):

        self.media_callback = media_callback
        self.system_callback = system_callback
        self.preset_callback = preset_callback
        self._address = f"{EventListener.PREFIX}{ip_address}:{EventListener.PORT}"

    def connect(self) -> None:

        with webclient.connect(self._address) as ws:
            try:
                ws.send(self._jsonify_subscription())
                for message in ws:
                    print(message)
            except ConnectionClosed:
                print("Disconnected from the target host")

    def _jsonify_subscription(self) -> str:
        event = []

        if self.media_callback == True:
            event.append({"subscribe": {"category": EventListener.MEDIA}})

        if self.system_callback == True:
            event.append({"subscribe": {"category": EventListener.SYSTEM}})

        if self.preset_callback == True:
            event.append({"subscribe": {"category": EventListener.PRESETS}})

        return dumps(event)
