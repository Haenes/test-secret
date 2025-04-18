FROM python:3.13-alpine

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY src/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN addgroup nonroot && \
    adduser --disabled-password --ingroup nonroot user

USER user

COPY . .
