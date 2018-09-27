#!/bin/sh
pwd
sleep 5
python3 manage.py makemigrations user course goods order
python3 manage.py migrate
python3 manage.py collectstatic --no-input
chown -R 1000 media/
su -m wxuser -c "uwsgi uwsgi.ini"
