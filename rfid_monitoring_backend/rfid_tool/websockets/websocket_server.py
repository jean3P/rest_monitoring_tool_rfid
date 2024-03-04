# websocket_server.py

import asyncio
import websockets
import json
import logging


class WebSocketServer:
    """
    A WebSocket server for handling connections and communication with clients.

    This class manages the lifecycle of a WebSocket server, including handling
    client connections, receiving messages, and broadcasting messages to clients.
    """

    def __init__(self):
        """
        Initializes the WebSocket server.

        Sets up an event for managing server shutdown and a dictionary for tracking connected clients.
        """
        self.shutdown_event = asyncio.Event()
        self.connected_clients = {}

    async def handle_websocket(self, websocket: websockets.WebSocketServerProtocol, path: str):  # pragma: no cover
        """
        Handles incoming WebSocket connections.

        Args:
            websocket: The WebSocket connection object.
            path: The path on which the client is connected.
        """
        if path not in self.connected_clients:
            self.connected_clients[path] = set()
        self.connected_clients[path].add(websocket)
        try:
            async for message in websocket:
                print(f"Received message on {path}: {message}")
                data = json.loads(message)

                # Echoing back the received message
                await self.broadcast_to_path_clients(data, path)
        except json.JSONDecodeError:
            print("Invalid JSON received")
        except websockets.exceptions.ConnectionClosed as e:
            print(f"Connection closed with code: {e.code}, reason: {e.reason}")
            if e.code == 1000:  # Normal closure
                print(f"Connection closed gracefully {e.code}")
            elif e.code == 1006:  # Abnormal closure
                print(f"Connection closed abnormally (code {e.code})")
            else:
                print(f"Connection closed with error: {e}. With code: {e.code}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            if path in self.connected_clients:
                self.connected_clients[path].discard(websocket)
                if not self.connected_clients[path]:
                    del self.connected_clients[path]

    async def broadcast_to_path_clients(self, data, path):
        """
        Broadcasts a message to all clients connected on a specific path.

        Args:
            data: The data to be sent to the clients.
            path: The path to which the message should be broadcast.
        """
        clients = self.connected_clients.get(path, set())
        if clients:
            tasks = [asyncio.create_task(self.safe_send(client, data)) for client in clients]
            await asyncio.gather(*tasks, return_exceptions=True)

    async def safe_send(self, client, data):
        """
        Safely sends a message to a client, handling potential exceptions.

        Args:
            client: The client to send the message to.
            data: The data to be sent.
        """
        if client.open:
            try:
                await client.send(json.dumps(data))
            except websockets.exceptions.ConnectionClosed:  # pragma: no cover
                print("Connection closed while sending message")
            except Exception as e:  # pragma: no cover
                print(f"Unexpected error while sending message: {e}")

    async def shutdown(self):
        """
        Shuts down the WebSocket server gracefully.

        Closes all client connections and then stops the server.
        """
        print("Shutting down WebSocket server...")
        # Close all client connections
        tasks = [client.close(code=1000) for path in self.connected_clients.values() for client in path]
        await asyncio.gather(*tasks, return_exceptions=True)

        # Clear the list of connected clients
        self.connected_clients.clear()

        # Close the WebSocket server
        if hasattr(self, 'ws_server') and self.ws_server:
            await self.ws_server.close()
            await self.ws_server.wait_closed()
