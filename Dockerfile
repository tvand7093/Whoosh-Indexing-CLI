FROM python:2.7

COPY . /app

WORKDIR /app

RUN pip install pymongo Whoosh python-dotenv

