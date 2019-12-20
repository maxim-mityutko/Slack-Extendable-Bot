FROM python:alpine3.7
COPY . /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r ./web/requirements.txt

CMD python ./web/server.py

EXPOSE 65010/tcp
