FROM python:3.6-onbuild

WORKDIR /app

COPY ./src requirements.txt ./

RUN pip install -r requirements.txt

CMD /usr/local/bin/gunicorn -w 2 -b :6000 server