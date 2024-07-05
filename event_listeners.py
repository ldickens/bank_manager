import asyncio
from json import dumps

import websockets

from utilities import get_nic_addrs


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
        self.address = f"{EventListener.PREFIX}{ip_address}:{EventListener.PORT}"
        self.net_adptrs = get_nic_addrs()

    async def handler(self, websocket: websockets.WebSocketServerProtocol) -> None:
        print("WE GET HERE")
        async for message in websocket:
            print(message)

    async def start_listener(self) -> None:
        await self.subscribe_to_categories()
        async with websockets.serve(
            self.handler, host=self.net_adptrs, port=EventListener.PORT
        ):
            await asyncio.Future()

    async def subscribe_to_categories(self) -> None:
        event = []

        if self.media_callback == True:
            event.append({"subscribe": {"category": EventListener.MEDIA}})

        if self.system_callback == True:
            event.append({"subscribe": {"category": EventListener.SYSTEM}})

        if self.preset_callback == True:
            event.append({"subscribe": {"category": EventListener.PRESETS}})

        async with websockets.connect(self.address) as ws:
            await ws.send(dumps(event))
            print(f"Subscribed to callback events on {self.address}")
