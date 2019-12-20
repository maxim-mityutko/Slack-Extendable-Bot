FROM python:alpine3.7
COPY . /bot
WORKDIR /bot

# GCC is required to build 'slackclient' on arm64
RUN apk add build-base
RUN pip install --upgrade pip
RUN pip install -r ./bot/requirements.txt

CMD python ./bot/bot.py
