#!/bin/sh

set -e  # Berhenti jika ada error

echo "Melakukan migrate database..."
python manage.py migrate

echo "Menjalankan perintah create_default_admin..."
python manage.py create_default_admin

echo "Menjalankan Gunicorn..."
exec gunicorn project_django.wsgi:application --bind 0.0.0.0:8000
