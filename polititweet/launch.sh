#!/bin/bash

# Start Gunicorn processes
echo Launching PolitiTweet web server...
exec gunicorn polititweet.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3