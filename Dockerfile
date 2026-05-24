FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /birbiruz

COPY requirements.txt /birbiruz/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /birbiruz/
