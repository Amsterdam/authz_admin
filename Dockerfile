FROM amsterdam/python
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

ARG https_proxy=http://10.240.2.1:8080/
ENV https_proxy=$https_proxy

EXPOSE 8000

RUN apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY . /app
WORKDIR /app

# This is needed for the ./run.sh script, that copies the right swagger
# definition file into swagger-ui.
RUN chown -R datapunt /app/swagger-ui/dist

RUN pip install -e .[test]

USER datapunt
