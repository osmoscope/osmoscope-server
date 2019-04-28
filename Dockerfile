# To build:
# docker build -t mfdz/osmoscope-server .
# To run:
# docker run -p 5000:80 -v $PWD/config/:/app/config -v $PWD/layers/:/app/layers mfdz/osmoscope-server
FROM tiangolo/uwsgi-nginx-flask:python3.7
# For details, see  
# https://hub.docker.com/r/tiangolo/uwsgi-nginx-flask/

# Replace supervisord.conf to start validate_periodically as well
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY requirements.txt .

RUN pip install --upgrade pip && \
  pip install --no-cache-dir -r requirements.txt

COPY . .

#create logging dir
RUN mkdir -p /opt/logs/

VOLUME ["/app/layers","/app/config"] 
