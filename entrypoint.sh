#!/bin/bash

# Collect static files
echo "Collect static files"
python3 manage.py collectstatic --noinput

# Apply database migrations
echo "Make migrations"
python3 manage.py makemigrations

# Apply database migrations
echo "Apply database migrations"
python3 manage.py migrate

echo "Creating superuser"
python3 manage.py create_super_user

# Start server
echo "Starting server"
python3 manage.py runserver 0.0.0.0:8001





