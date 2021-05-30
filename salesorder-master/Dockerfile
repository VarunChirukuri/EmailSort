FROM python:3.8.3-slim
RUN apt update
RUN apt-get install -y software-properties-common
RUN apt-get -y update && apt-get install -y --no-install-recommends \
         wget \
         nginx \
         nano \
         wget \
         ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN pip install flask gevent gunicorn jsonlogging boto3 flask_jwt_extended pyyaml
# Bundle app source
COPY app/* /opt/program/
RUN chmod a+x /opt/program/entrypoint.sh
ENTRYPOINT [ "/opt/program/entrypoint.sh" ]
