#!/bin/bash

cd KrsnaUs

exec gunicorn KrsnaUs.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3
