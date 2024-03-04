#!/bin/bash

# Navigate to your Django project directory if necessary
# cd /path/to/your/django/project

# Activate your virtual environment if you're using one
# source /path/to/your/venv/bin/activate

# Run Django database migrations
python manage.py makemigrations
python manage.py migrate

echo "Database migrations completed successfully."
