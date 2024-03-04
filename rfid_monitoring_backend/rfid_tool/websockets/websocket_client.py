# websocket_client.py

import asyncio
import random

import websockets
import json
import logging

class WebSocketClient:
    """
    A WebSocket client for sending and receiving messages from a WebSocket server.

    This class handles the connection to a WebSocket server, sending messages,
    and listening for incoming messages.
    """
    def __init__(self, uri):
        """
        Initializes the WebSocket client with a server URI.

        Args:
            uri (str): The URI of the WebSocket server to connect to.
        """
        self.connection = None
        self.uri = uri
        # Reconnection parameters
        self.reconnection_attempts = 0  # Track reconnection attempts
        # Reconnection parameters
        self.initial_delay = 1  # in seconds
        self.max_delay = 30  # in seconds
        self.backoff_factor = 2
        self.max_retries = 5  # Maximum number of reconnection attempts

    async def connect(self):
        try:
            self.connection = await websockets.connect(self.uri)
            print("Connected to WebSocket server")
            # Reset the reconnection attempt counter upon successful connection
            self.reconnection_attempts = 0
            return True
        except Exception as e:  # pragma: no cover
            print(f"Connection failed: {e}")
            return False

    async def send_message(self, message):
        """
        Asynchronously sends a message to the WebSocket server.

        Args:
            message (str or dict): The message to be sent to the server. If it's a dict, it will be converted to JSON.
        """
        await self.connection.send(json.dumps(message))
        print(f"Sent message: {json.dumps(message)}")

    async def close_connection(self):
        """
        Asynchronously closes the WebSocket connection.
        """
        if self.connection is not None:
            await self.connection.close()
            print("Connection closed")

    def on_message_received(self, message):
        """
        Handles the event when a message is received from the WebSocket server.

        Args:
            message (str): The message received from the server.
        """
        # Handle received message
        print(f"Received message: {message}")

    async def handle_disconnection(self):
        self.reconnection_attempts += 1
        if self.reconnection_attempts > self.max_retries:
            print("Maximum reconnection attempts reached, giving up.")  # pragma: no cover
            return  # pragma: no cover

        # Calculate the delay using an exponential backoff strategy
        delay = min(self.initial_delay * (self.backoff_factor ** (self.reconnection_attempts - 1)), self.max_delay)
        # Adding some randomness to avoid thundering herd problem
        delay = random.uniform(delay / 2, delay)
        print(f"Reconnecting in {delay:.2f} seconds...")
        await asyncio.sleep(delay)

        if await self.connect():
            # Connection successful, reset attempt counter and proceed as normal
            self.reconnection_attempts = 0
            # Here, you would also start listening for messages again, or perform any other necessary setup
        else:  # pragma: no cover
            # If reconnection failed, retry
            await self.handle_disconnection()

    async def listen_for_messages(self):
        """
        Asynchronously listens for messages from the WebSocket server.

        Continuously receives messages from the server until the connection is closed.
        """
        try:
            while True:
                message = await self.connection.recv()
                self.on_message_received(message)
        except websockets.exceptions.ConnectionClosedOK:
            print("Connection closed normally.")
            await self.handle_disconnection()
        except websockets.exceptions.ConnectionClosedError as e:  # pragma: no cover
            print(f"Disconnected from server with code: {e.code}, reason: {e.reason}")
            await self.handle_disconnection()
        except Exception as e:  # pragma: no cover
            print(f"Unexpected error: {e}")
            await self.handle_disconnection()

    async def run_and_listen(self, message): # pragma: no cover
        """
        Connects to the WebSocket server, sends a message, and starts listening for incoming messages.

        Args:
            message (str or dict): The message to send after connecting to the server.
        """
        await self.connect()
        await self.send_message(message)
        listen_task = asyncio.create_task(self.listen_for_messages())
        await listen_task
