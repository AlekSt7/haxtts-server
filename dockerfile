FROM python:3.9

MAINTAINER Alek.st7
LABEL version="1.0.0"

WORKDIR /usr/app

RUN apt-get update --fix-missing && apt-get upgrade -y
RUN apt-get install -y sox libsox-fmt-mp3 sox

ENV PYTHONUNBUFFERED=1

RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

#install specific versions torch with cuda support
RUN pip3 install torch==2.5.0 torchaudio==2.5.0 --index-url https://download.pytorch.org/whl/cu124

COPY requirements_docker.txt .
RUN pip3 install -r requirements_docker.txt

COPY ./ ./

EXPOSE 9898

CMD [ "python3", "-u", "./main.py", "--host", "0.0.0.0", "--port", "9898" ]