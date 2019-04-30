# Osmoscope Server

Osmoscope Server is an optional component for Overpass-UI, the OpeenStreeetMap quality 
assurance tool. It attempts to provide an easy way to generating osmoscope data layers 
and maintain associated statistics using e.g. overpass queries. 
Additional layers can be added by anyone.


## Status

At the moment this software is only barely usable, more a proof-of-concept.


## To run the server

To run this yourself, you might start the server from the command line or as docker container.

### Run the server from command line
To run Osmoscope Server from the command line, you'll need python3, pip and virtualenv installed.

```
$ mkvirtualenv osmoscope-server
$ pip install -r requirements.txt
$ python app.py 
```
Note: you should do this in development only!

### Run the server as docker container
To run Osmoscope Server as docker container, you need to have docker installed. 

Build a docker image like e.g.
```
docker build -t mfdz/osmoscope-server .
```

and start it via e.g.

```
docker run -p 5000:80 -v $PWD/config/:/usr/src/app/layers  -v $PWD/config/:/usr/src/app/layers mfdz/osmoscope-server
```

You should see Osmoscope Server generating the data layers and finally starting a server using port 5000.

## Configure Osmoscope Server
The file config.py contains a sample configuration. To use your own, create an folder app/instance/, copy 
app/config.py to this folder and adapt it according to your needs:

```
# OSMOSCOPE_AREA_OR_BOUNDINGBOX defines a bounding box or an overpass area 
# (e.g. 'area:3600062611') to restrict overpass queries to an area of interest
# During development, you might use a smaller bounding box/area.
OSMOSCOPE_AREA_OR_BOUNDINGBOX = '48.699,9.199,48.70,9.2'

# The crontab OSMOSCOPE_UPDATE_SCHEDULE defines when all layers are 
# checked and updated (only in production mode)
OSMOSCOPE_UPDATE_SCHEDULE = '0 0 * * *'
```

## To add your own layers

For each layer you need to write a JSON file describing this layer. Look at the [example](http://area.jochentopf.com/osmm/layers.json) for
some idea about the format. 

Osmoscope Server will periodically generate the actual data layers in GeoJSON 
format and make them available for download. It also maintains statistic files for every layer.

For a more detailed description [read this](doc/creating-layers.md).


## Libraries and projects used

* [Flask](http://flask.pocoo.org)
* [osmtogeojson](https://github.com/tommyjcarpenter/osmtogeojson)
* [apscheduler](https://apscheduler.readthedocs.io/en/latest/)
* [overpass api python wrapper](https://github.com/mvexel/overpass-api-python-wrapper)
* [uwsgi-nginx-flask docker](https://github.com/tiangolo/uwsgi-nginx-flask-docker)

## License

Copyright (C) 2019 Holger Bruch (hb at mfdz dot de)

This program is available under the GNU GENERAL PUBLIC LICENSE Version 3.
See the file LICENSE.txt for the complete text of the license.


## Authors

This program was written and is maintained by Holger Bruch (hb at mfdz dot de). 
It was motivated by Jochen Topf's Osmoscope, a new decentralized OSM quality assurance tool.

