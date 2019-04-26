# To build:
# docker build -t mfdz/osmoscope-server .
# To run:
# docker run -p 5000:5000 -v $PWD/config/:/app/config -v $PWD/layers/:/app/layers mfdz/osmoscope-server
FROM tiangolo/uwsgi-nginx-flask:python3.7
# For details, see  
# https://hub.docker.com/r/tiangolo/uwsgi-nginx-flask/

COPY . /app

ENV LISTENPORT 80

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

#create logging dir
RUN mkdir -p /opt/logs/

VOLUME ["/app/layers","/app/config"] 
