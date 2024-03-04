from django.db import models


class ArduinoData(models.Model):
    rfid_uid = models.CharField(max_length=255, null=True)  # Temporarily allow null
    model = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

