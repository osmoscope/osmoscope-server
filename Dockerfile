# To build:
# docker build -t mfdz/osmoscope-server .
# To run:
# docker run -p 5000:5000 -v $PWD/layers/:/usr/src/app/layers mfdz/osmoscope-server
FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app .

EXPOSE 5000

CMD [ "python", "./app.py" ]
