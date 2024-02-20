FROM python:3.12.2-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV TINI_VERSION=v0.19.0

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

COPY . .
