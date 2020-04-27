FROM python:3.8.2-slim-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    libc-dev \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install -r requirements.txt

RUN mkdir /app
COPY ./app/ /app/

WORKDIR /app/

RUN useradd -ms /bin/bash user

USER user