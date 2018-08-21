FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /webapps
WORKDIR /webapps

RUN apt-get update && apt-get upgrade -y && apt-get install -y \
libsqlite3-dev

COPY ./ /webapps/

RUN pip install -r /webapps/requirements.txt
