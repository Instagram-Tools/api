FROM python:3.6

WORKDIR /app

COPY ./src requirements.txt ./

RUN pip install -r requirements.txt

CMD /usr/local/bin/gunicorn -b :5000 server