FROM python:3.6

WORKDIR /app

COPY ./src requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

CMD /usr/local/bin/gunicorn -w 2 -b :5000 server