FROM amsterdam/docker_python:latest
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

EXPOSE 8120

RUN apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e .

USER datapunt

CMD authz_admin_service
