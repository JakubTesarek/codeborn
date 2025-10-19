# syntax=docker/dockerfile:1
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# keep image’s installed packages visible but preserve default paths
ENV PYTHONPATH="/usr/local/lib/python3.13/site-packages:${PYTHONPATH}"

WORKDIR /app

# copy package metadata and source
COPY pyproject.toml ./
COPY codeborn_client ./codeborn_client

# install codeborn_client and its optional [user] extras
RUN pip install --no-cache-dir .[user]

# engine provides the command at runtime; no CMD here
