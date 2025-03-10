FROM python:3.12

MAINTAINER Alek.st7
LABEL version="1.0.0"

WORKDIR /usr/app

RUN apt-get update --fix-missing && apt-get upgrade -y

ENV PYTHONUNBUFFERED=1

RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

#install specific versions torch with cuda support
RUN pip install torch==2.5.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu124

COPY requirements_docker.txt .
RUN pip3 install -r requirements_docker.txt

COPY ./ ./

EXPOSE 9898

CMD [ "python3", "-u", "./main.py", "--host", "0.0.0.0", "--port", "9898" ]