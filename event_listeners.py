from json import dumps, loads

import websockets.sync.client as webclient
from websockets.exceptions import ConnectionClosed

from app_state import AppState


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
        self.connected = True

    def connect(self) -> None:

        with webclient.connect(self._address) as ws:
            try:
                ws.send(self._jsonify_subscription())
                for message in ws:
                    if message == "OK":
                        continue
                    msg_obj = loads(message)
                    if msg_obj["category"] == "MEDIA":
                        AppState._update_media = True
                        print("\nMedia Updated: Reload required")
                        if AppState._uploading:
                            AppState._progress_steps += 1

                    if msg_obj["category"] == "SYSTEM":
                        AppState._update_system = True
                        print("\nSystem change detected: Disconnecting from host.")

                    if self.connected == True:
                        continue
                    else:
                        break  # Dirty break because I don't think Hippo handshakes a closure.

            except ConnectionClosed:
                print("Disconnected from the target host")

    def disconnect(self) -> None:
        self.connected = False

    def _jsonify_subscription(self) -> str:
        event = []

        if self.media_callback == True:
            event.append({"subscribe": {"category": EventListener.MEDIA}})

        if self.system_callback == True:
            event.append({"subscribe": {"category": EventListener.SYSTEM}})

        if self.preset_callback == True:
            event.append({"subscribe": {"category": EventListener.PRESETS}})

        return dumps(event)
