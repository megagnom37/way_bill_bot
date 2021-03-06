FROM python:3.8-slim

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./way_bill /way_bill
COPY ./creds.json /creds.json

CMD ["python", "-m", "way_bill"]