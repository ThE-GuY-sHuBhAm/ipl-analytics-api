#!/bin/sh
gunicorn --chdir /ipl-analytics-api app:app -w 2 --threads 2 -b 0.0.0.0:$PORT