#!/bin/sh
pwd
su -m wxuser -c "python3 manage.py makemigrations user course goods order"
su -m wxuser -c "python3 manage.py migrate"
su -m wxuser -c "uwsgi uwsgi.ini"
