# Python support can be specified down to the minor or micro version
# (e.g. 3.6 or 3.6.3).
# OS Support also exists for jessie & stretch (slim and full).
# See https://hub.docker.com/r/library/python/ for all supported Python
# tags from Docker Hub.
FROM python:3.6-slim-stretch

# If you prefer miniconda:
#FROM continuumio/miniconda3

LABEL Name=wxapp Version=0.0.1
COPY  requirements.txt /wxapp/requirements.txt
WORKDIR /wxapp

RUN echo  "deb http://mirrors.aliyun.com/debian/ stretch main non-free contrib\n\
deb-src http://mirrors.aliyun.com/debian/ stretch main non-free contrib\n\
deb http://mirrors.aliyun.com/debian-security stretch/updates main\n\
deb-src http://mirrors.aliyun.com/debian-security stretch/updates main\n\
deb http://mirrors.aliyun.com/debian/ stretch-updates main non-free contrib\n\
deb-src http://mirrors.aliyun.com/debian/ stretch-updates main non-free contrib\n\
deb http://mirrors.aliyun.com/debian/ stretch-backports main non-free contrib\n\
deb-src http://mirrors.aliyun.com/debian/ stretch-backports main non-free contrib" > /etc/apt/sources.list

RUN apt-get update -qq && \
    apt-get install -qq -y --no-install-recommends \
        git gcc g++ make default-libmysqlclient-dev && \
    apt-get autoremove -qq -y --purge && \
    rm -rf /var/cache/apt /var/lib/apt/lists

RUN pip install --no-cache-dir -r requirements.txt -i http://mirrors.cloud.tencent.com/pypi/simple --trusted-host mirrors.cloud.tencent.com
RUN adduser --disabled-password --gecos '' wxuser

EXPOSE 8000
