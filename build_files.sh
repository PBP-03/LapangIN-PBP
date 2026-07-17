#!/bin/bash
# Runs during Vercel's build step for the @vercel/static-build source in vercel.json.
pip install -r requirements.txt
python manage.py collectstatic --noinput
