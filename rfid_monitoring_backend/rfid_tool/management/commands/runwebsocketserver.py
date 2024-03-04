import asyncio
import signal
import platform
from django.core.management.base import BaseCommand
import websockets
from rfid_tool.websockets.websocket_server import WebSocketServer


async def shutdown_server(server, loop):  # pragma: no cover
    print("Shutting down")
    await server.shutdown()  # Ensure server shutdown is awaited
    tasks = [t for t in asyncio.all_tasks(loop) if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


def run_server(loop, server):
    start_server = websockets.serve(server.handle_websocket, "localhost", "8001")
    loop.run_until_complete(start_server)

    try:
        loop.run_forever()
    except KeyboardInterrupt:  # pragma: no cover
        asyncio.run_coroutine_threadsafe(shutdown_server(server, loop), loop)


class Command(BaseCommand):
    help = 'Starts the WebSocket server'

    def handle(self, *args, **options):
        print("Starting WebSocket Server")
        server = WebSocketServer()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        if platform.system() != 'Windows':  # pragma: no cover
            for signame in ('SIGINT', 'SIGTERM'):
                loop.add_signal_handler(
                    getattr(signal, signame),
                    lambda: asyncio.create_task(shutdown_server(server, loop))
                )

        run_server(loop, server)
