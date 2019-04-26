# To build:
# docker build -t mfdz/osmoscope-server .
# To run:
# docker run -p 5000:5000 -v $PWD/app/config/:/usr/src/app/config -v $PWD/app/layers/:/usr/src/app/layers mfdz/osmoscope-server
FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --upgrade pip && \
  pip install --no-cache-dir -r requirements.txt

COPY app .

EXPOSE 5000
VOLUME ["usr/src/app/layers","usr/src/app/config"] 

CMD [ "python", "./app.py" ]
