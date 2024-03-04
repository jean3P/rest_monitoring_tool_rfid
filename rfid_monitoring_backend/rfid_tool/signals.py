import asyncio
import threading

from django.db.models.signals import post_save
from django.dispatch import receiver

from rfid_tool.models import ArduinoData
from rfid_tool.websockets.websocket_client import WebSocketClient


def send_update_async(message_type, data):
    url = f"ws://localhost:8001/1.0/"
    client = WebSocketClient(url)
    message = {'type': message_type, 'data': data}

    async def async_task():  # pragma: no cover
        try:
            await client.connect()
            await client.send_message(message)
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            await client.close_connection()

    threading.Thread(target=lambda: asyncio.run(async_task())).start()


@receiver(post_save, sender=ArduinoData)
def post_save_arduino_data(sender, instance, created, **kwargs):
    if created:
        message_type = 'new_arduino_data'
        data = {'id': instance.id}
        send_update_async(message_type, data)
        print("Signal sent from ArduinoData")
