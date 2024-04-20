#!/bin/sh
poetry run python manage.py migrate
poetry run python manage.py runserver 0.0.0.0:8000

# Check if DOPPLER_TOKEN is a non-empty string
#if [ -n "$DOPPLER_TOKEN" ]; then
#    # If $DOPPLER_TOKEN has any value, use doppler
#    exec doppler run -- "$@"
#else
#    # If $DOPPLER_TOKEN is empty, execute with no doppler
#    exec "$@"
#fi