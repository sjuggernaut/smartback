#!/bin/bash

case "$1" in
  start)
      # Apply database migrations
#      echo "Make migrations"
#      python3 manage.py makemigrations

#      # Apply database migrations
#      echo "Apply new database migrations"
#      python3 manage.py migrate
      echo "Collect static files"
      python3 manage.py collectstatic --noinput

      echo "Creating superuser"
      python3 manage.py create_super_user

      echo "Starting server"
#      python3 manage.py runserver 0.0.0.0:80
      gunicorn smartback.wsgi:application --bind 0.0.0.0:8000
  ;;
  kafka-backend)
      echo "Launching Sensor Consumers"
      python3 manage.py launch_providers
  ;;
  python)
    python3
  ;;
esac

