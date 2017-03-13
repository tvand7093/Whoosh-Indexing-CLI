FROM python:2.7

# This dockerfile assumes that when you run the application you use a mounted drive
# in the location of this git repository.

WORKDIR /app

RUN pip install pymongo Whoosh python-dotenv

