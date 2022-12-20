FROM python:3.10.8-slim-buster as build

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

RUN apt-get -y update && apt-get -y install git

WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY main.py main.py
# ARG skill
# COPY ./$skill/skill.py skill.py
COPY ./extractive-qa/skill.py skill.py 
COPY logging.conf logging.conf

EXPOSE 8000

CMD ["uvicorn", "skills.main:app", "--host", "0.0.0.0", "--port", "8083", "--log-config", "logging.conf"]
