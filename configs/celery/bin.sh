#!/bin/sh


sleep 10

cd /app
pwd
celery worker -A wxapp -l info
