from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
import serial
from rfid_tool.models import ArduinoData
from rfid_tool.signals import send_update_async


class ArduinoReader:
    def __init__(self, port, baudrate=9600):
        self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=1)
        self.arduino.flush()

    def read_data(self):
        """Reads data from the Arduino and returns it."""
        if self.arduino.in_waiting > 0:
            data = self.arduino.readline().decode('utf-8').strip()
            return data
        return None

    def parse_and_store_data(self, data):
        data_dict = self.parse_arduino_data(data)
        if data_dict:
            model_info = f"{data_dict.get('ARDUINO_MODEL', '')} {data_dict.get('RFID_MODEL', '')}".strip()
            rfid_uid = data_dict.get('RFID_UID', '')

            # Check if an instance with the given rfid_uid already exists
            try:
                existing_data = ArduinoData.objects.get(rfid_uid=rfid_uid)
                # If it exists, send an update signal instead of creating a new instance
                print(f"Data with RFID_UID={rfid_uid} already exists in DB.")
                send_update_async('existing_arduino_data', {'id': existing_data.id})
            except ObjectDoesNotExist:
                # If it does not exist, create a new instance and a signal will be sent from the post_save signal
                try:
                    ArduinoData.objects.create(rfid_uid=rfid_uid, model=model_info)
                    print(f"Stored in DB: RFID_UID={rfid_uid}, MODEL={model_info}")
                except IntegrityError as e:
                    print(f"Error storing data in DB: {e}")

    @staticmethod
    def parse_arduino_data(data):
        """Parses the received data from Arduino."""
        keys = ['ARDUINO_MODEL', 'RFID_MODEL', 'RFID_UID']
        data_dict = {}
        start = 0

        for key in keys:
            start_idx = data.find(key, start)
            if start_idx == -1:
                continue

            end_idx = len(data)
            for next_key in keys:
                temp_idx = data.find(next_key, start_idx + len(key))
                if temp_idx != -1 and temp_idx < end_idx:
                    end_idx = temp_idx

            value = data[start_idx + len(key) + 2:end_idx].strip()
            data_dict[key] = value
            start = end_idx

        return data_dict
