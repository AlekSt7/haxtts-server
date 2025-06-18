FROM python:3.10-bookworm

MAINTAINER Alek.st7
LABEL version="1.0.0"

WORKDIR /usr/app

ENV PYTHONUNBUFFERED=1

RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

COPY requirements_docker.txt .
RUN apt-get update && apt-get install -y portaudio19-dev
RUN pip3 install -r requirements_docker.txt

COPY ./ ./

EXPOSE 9898

CMD [ "python3", "-u", "./main.py", "--host", "0.0.0.0", "--port", "9898" ]