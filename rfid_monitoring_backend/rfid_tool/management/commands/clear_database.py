from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps


class Command(BaseCommand):
    help = 'Clears the specified database tables and resets their primary key counters.'

    def handle(self, *args, **options):
        # List of models to clear
        models_to_clear = ['ArduinoData']  # Add the names of the models you want to clear

        with connection.cursor() as cursor:
            for model_name in models_to_clear:
                # Get model class
                model_class = apps.get_model('rfid_tool', model_name)
                # Clear the table
                model_class.objects.all().delete()
                self.stdout.write(f'Cleared all entries from {model_name}')

                # Reset the primary key counter
                table_name = model_class._meta.db_table
                cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="{table_name}"')
                self.stdout.write(f'Reset primary key counter for {model_name}')

        self.stdout.write(self.style.SUCCESS('Successfully cleared specified tables and reset counters.'))
