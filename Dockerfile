FROM python:3.7-alpine

RUN mkdir -p /app/
WORKDIR /app/

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY ./app.py /app/app.py

ENTRYPOINT python -u /app/app.py
