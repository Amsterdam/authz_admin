FROM amsterdam/docker_python:latest
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

EXPOSE 8120

RUN apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app
COPY . /app

# This is needed for the ./run.sh script, that copies the right swagger
# definition file into swagger-ui.
RUN chown -r datapunt /app/swagger-ui/dist

RUN pip install --no-cache-dir -e .

USER datapunt

CMD ./run.sh
