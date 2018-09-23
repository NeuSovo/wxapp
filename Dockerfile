# Python support can be specified down to the minor or micro version
# (e.g. 3.6 or 3.6.3).
# OS Support also exists for jessie & stretch (slim and full).
# See https://hub.docker.com/r/library/python/ for all supported Python
# tags from Docker Hub.
FROM python:3.6-slim-stretch

# If you prefer miniconda:
#FROM continuumio/miniconda3

LABEL Name=wxapp Version=0.0.1

COPY  . /app
WORKDIR /app

RUN apt-get update -qq && \
    apt-get install -qq -y --no-install-recommends \
        git gcc g++ make default-libmysqlclient-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get autoremove -qq -y --purge && \
    rm -rf /var/cache/apt /var/lib/apt/lists && \
    python3 manage.py collectstatic --no-input


EXPOSE 8000

CMD python3 manage.py makemigrations user course goods order&& \
    python3 manage.py migrate && \
    uwsgi uwsgi.ini
