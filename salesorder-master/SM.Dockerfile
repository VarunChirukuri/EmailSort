FROM python:3.8.3-slim

RUN apt update
RUN apt-get install -y git-all
RUN pip3 install flair==0.4.5
#RUN pip3 install --upgrade git+https://github.com/zalandoresearch/flair.git
RUN apt-get install -y software-properties-common curl gnupg2 ca-certificates lsb-release
#RUN curl -s https://updates.signal.org/desktop/apt/keys.asc | apt-key add -
RUN curl -fsSL https://nginx.org/keys/nginx_signing.key |  apt-key add -
RUN echo "deb http://nginx.org/packages/mainline/debian `lsb_release -cs` nginx" \
    |  tee /etc/apt/sources.list.d/nginx.list
#RUN add-apt-repository ppa:nginx/stable
RUN apt update
RUN apt-get -y update && apt-get install -y --no-install-recommends \
         wget \
         nginx \         
         nano \
         vim \         
         wget \          
         ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install flask gevent gunicorn boto3 flask_jwt_extended

EXPOSE 8080

ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/program/:${PATH}"
ENV MODEL_PATH="/tmp"

COPY flair_model/* /opt/program/

WORKDIR /opt/program/
RUN mkdir -p  /var/lib/nginx/body/
RUN mkdir -p  /tmp/nginx/
RUN mkdir -p  /tmp/model/
RUN mkdir -p  /opt/ml/model/
RUN mkdir -p  /home/ubuntu/.flair/embeddings/en
RUN wget -O /home/ubuntu/.flair/embeddings/en/en.wiki.bpe.vs100000.model https://nlp.h-its.org/bpemb/en/en.wiki.bpe.vs100000.model
#RUN python -c 'from flair.embeddings import BytePairEmbeddings;from flair.data import Sentence; emd = BytePairEmbeddings("en", dim=300);s = Sentence("sales order");'
RUN touch /tmp/nginx/access.log
RUN touch /tmp/nginx/error.log
#RUN touch /var/log/nginx/error.log
RUN chmod 600 /tmp/nginx/*
#RUN chmod 600 /tmp//nginx
RUN chmod a+x /opt/program/train && \
    chmod a+x /opt/program/serve
RUN chown nginx:nginx /tmp/nginx
WORKDIR /opt/program
CMD ["/opt/program/serve"]
