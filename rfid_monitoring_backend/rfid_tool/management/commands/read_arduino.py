from django.core.management.base import BaseCommand
from rfid_tool.src.ArduinoReader import ArduinoReader


class Command(BaseCommand):
    help = 'Reads data from the Arduino and stores it in the database'

    def handle(self, *args, **kwargs):
        reader = ArduinoReader('/dev/cu.usbmodem111101')  # Adjust your port

        try:
            while True:
                data = reader.read_data()
                if data:
                    print(f"Data Received: {data}")
                    reader.parse_and_store_data(data)
        except KeyboardInterrupt:
            print("Stopped reading from Arduino")
