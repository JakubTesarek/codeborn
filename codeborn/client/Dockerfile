# syntax=docker/dockerfile:1
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/usr/local/lib/python3.13/site-packages:${PYTHONPATH}"

WORKDIR /app

COPY pyproject.toml ./
COPY codeborn_client ./codeborn_client

RUN pip install --no-cache-dir .[user]
