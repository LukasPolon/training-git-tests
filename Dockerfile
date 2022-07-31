# TODO: GIT version must be specified! best solution - install from source
FROM python:3.10

RUN apt-get update && apt-get install sshpass -y

RUN pip install --upgrade pip

WORKDIR /git-tests
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./ ./
