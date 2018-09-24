# Python support can be specified down to the minor or micro version
# (e.g. 3.6 or 3.6.3).
# OS Support also exists for jessie & stretch (slim and full).
# See https://hub.docker.com/r/library/python/ for all supported Python
# tags from Docker Hub.
FROM python:3.6-slim-stretch

# If you prefer miniconda:
#FROM continuumio/miniconda3

LABEL Name=wxapp Version=0.0.1
VOLUME [ "/wxapp" ]
COPY  . /wxapp
WORKDIR /wxapp

RUN apt-get update -qq && \
    apt-get install -qq -y --no-install-recommends \
        git gcc g++ make default-libmysqlclient-dev && \
    apt-get autoremove -qq -y --purge && \
    rm -rf /var/cache/apt /var/lib/apt/lists
    
RUN pip install --no-cache-dir -r requirements.txt -i http://mirrors.tencentyun.com/pypi/simple --trusted-host mirrors.tencentyun.com&& \
    python3 manage.py collectstatic --no-input

RUN adduser --disabled-password --gecos '' wxuser

EXPOSE 8000
