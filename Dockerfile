FROM amsterdam/python3.6
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

RUN apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY . /app
WORKDIR /app

# This is needed for the ./run.sh script, that copies the right swagger
# definition file into swagger-ui.
RUN chown -R datapunt /app/swagger-ui/dist

RUN pip install --no-cache-dir -e .[test]

USER datapunt
