FROM python:3.8.0-buster

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt-get update -y && apt-get install -y postgresql gcc python3-dev musl-dev libmagic-dev

RUN apt-get install -y bash \
                       python3 \
                       python3-pkgconfig \
                       git \
                       gcc \
                       libcurl4 \
                       python3-dev \
                       libgpgme-dev \
                       libc-dev \
                        g++ \
    && rm -rf /var/cache/apt/*
RUN wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py
RUN pip3 install setuptools==30.1.0

# install psycopg2 dependencies
RUN apt-get -y install musl-dev

RUN pip3 install --upgrade pip
RUN pip3 install psycopg2-binary

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt
ADD . /app/
COPY entrypoint.sh .

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY start-kafka.sh .

# copy project
ADD . /app/


ENTRYPOINT ["/app/docker-entrypoint.sh"]

