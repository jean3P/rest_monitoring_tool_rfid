from django.apps import apps
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from rfid_tool.models import ArduinoData


def get_arduino_data_by_id(request, id):
    # Fetch the ArduinoData instance by ID or return a 404 error if not found
    arduino_data = get_object_or_404(ArduinoData, id=id)

    # Prepare the data to be returned
    data = {
        'id': arduino_data.id,
        'rfid_uid': arduino_data.rfid_uid,
        'model': arduino_data.model,
        'created_at': arduino_data.created_at.isoformat(),
    }

    # Return the data as JSON
    return JsonResponse(data)


@csrf_exempt  # Use this with caution and ensure CSRF protection is appropriately handled in your application
@require_http_methods(["POST"])  # Ensure that this operation can only be performed via POST request
def clean_database(request):
    # List of models you want to clear, can be extended to more models
    models_to_clear = ['ArduinoData']
    response_data = {'status': 'success', 'cleared_models': []}

    try:
        with connection.cursor() as cursor:
            for model_name in models_to_clear:
                # Get the model class from the app label and model name
                model_class = apps.get_model('rfid_tool', model_name)
                # Delete all records from the model
                deletion_count, _ = model_class.objects.all().delete()
                response_data['cleared_models'].append({model_name: deletion_count})

                # If using SQLite, reset the primary key counter
                if 'sqlite' in connection.vendor:
                    table_name = model_class._meta.db_table
                    cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="{table_name}"')

        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({'status': 'failure', 'error': str(e)}, status=500)