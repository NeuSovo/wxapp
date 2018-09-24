#!/bin/sh
sleep 10
cd /wxapp
pwd
su -m wxuser -c "celery worker -A wxapp -l info"
