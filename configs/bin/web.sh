#!/bin/sh
pwd
sleep 5
chown -R 1000 /wxapp
pip install gunicorn
su -m wxuser -c "python3 manage.py makemigrations user course goods order"
su -m wxuser -c "python3 manage.py migrate"
su -m wxuser -c "python3 manage.py collectstatic --no-input"
su -m wxuser -c "gunicorn wxapp.wsgi:application --bind :8000 --log-level info --reload"
