# Generated by Django 4.2.7 on 2024-03-04 00:06

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("rfid_tool", "0003_rename_data_arduinodata_model_arduinodata_rfid_uid"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="user",
        ),
        migrations.DeleteModel(
            name="Tag",
        ),
        migrations.DeleteModel(
            name="UserProfile",
        ),
    ]