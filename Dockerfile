#FROM python:alpine3.12
FROM python:3.8-slim

#RUN adduser -D microapp
RUN groupadd -r microapp && useradd -r -g microapp microapp

WORKDIR /home/microapp

# RUN apk add --no-cache --update \
#     python3 python3-dev gcc \
#     gfortran musl-dev \
#     libffi-dev openssl-dev

ARG HTTPS_PROXY
ENV HTTPS_PROXY=$HTTPS_PROXY

COPY requirements.txt requirements.txt
#RUN python -m venv venv
# RUN venv/bin/pip install --upgrade pip
# RUN venv/bin/pip install -r requirements.txt
# RUN venv/bin/pip install gunicorn
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY app app
COPY microapp.py ./
RUN mkdir -p /home/microapp/uploads

COPY boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP microapp.py

RUN chown -R microapp:microapp ./
USER microapp

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
