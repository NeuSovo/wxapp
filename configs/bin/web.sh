#!/bin/sh
pwd
sleep 5
chown -R 1000 /wxapp
su -m wxuser -c "python3 manage.py makemigrations user course goods order"
su -m wxuser -c "python3 manage.py migrate"
su -m wxuser -c "python3 manage.py collectstatic --no-input"
chown -R 1000 media/
su -m wxuser -c "uwsgi uwsgi.ini"
