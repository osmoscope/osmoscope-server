# Creating Layers for Osmoscope Server

Creating a layer for use in Osmoscope Server is pretty easy. 
Osmoscope Server will periodically update
your data layer (currently in [GeoJSON](http://geojson.org/) format), 
maintain the statistics and publish it via it's internal web server.
All you have to do is create a JSON file in the special format 
expected by Osmoscope-UI, and an additional overpass_query parameter, 
which defines the query to retrieve this layer's data.

## The Layer File

For each layer you want to make available, you have to create a JSON file named ```layer_YOURLAYERNAME.json``` and place it in the ```config``` directory. 
This file contains the metadata about your layer. For the structure, see the [Osmoscope UI documentation](https://github.com/osmoscope/osmoscope-ui/blob/master/doc/creating-layers.md).

Define a property ```"overpass_query"``` which will be the query sent to the overpass server.

Note: You don't need to specify geojson_url and stats_data_url, as they will be generated by Osmoscope Server.

```
{
    "id": "ID OF YOUR LAYER",
    "name": "NAME OF YOUR LAYER",
    "doc": {
        "description": "MORE DETAILED DESCRIPTION OF THE LAYER",
        "why_problem": "MORE INFORMATION ON WHY THIS IS A PROBLEM (OPTIONAL)",
        "how_to_fix": "SOME INFORMATION ON HOW TO FIX THE ERROR (IF APPLICABLE)"
    },
    "updates": "HOW OFTEN THE DATA FOR THIS LAYER IS UPDATED",
    "overpass_query": "YOUR OVERPASS QUERY"
}
```
### Defining the area of interest
In your overpass query, you may use a placeholder {{bbox}} for the area of interest of your query. It may be  set via the setting ```OSMOSCOPE_AREA_OR_BOUNDINGBOX```  in  ```config/config.py``` an accepts either a bounding box or an area:
```
OSMOSCOPE_AREA_OR_BOUNDINGBOX = 'area:3600062611'
OSMOSCOPE_AREA_OR_BOUNDINGBOX = '48.699,9.199,48.70,9.2'
```

Note: In development mode, you would probably use a rather small area/bounding box.

## The DataSource File

Osmoscope Server generates a DataSouce File named ```layers.json``` , which references all
your defined layers.
```
{
    "name": "OSMOSCOPE_SERVERNAME",
    "layers": [
        "URL OF FIRST LAYER",
        "URL OF SECOND LAYER",
        ...,
        "URL OF LAST LAYER"
    ]
}
```
To set the server name, change the OSMOSCOPE_SERVERNAME setting in  ```config/config.py```.

## The Geodata
Osmoscope Server periodically updates the Geodata using the query defined in the layer file.
The data is stored to a file ```data_YOURLAYERNAME.json``` . Per default, every layer is updated on Osmoscope Server start and at the time specified via the  ```OSMOSCOPE_UPDATE_SCHEDULE ``` crontab pattern in  ```config/config.py```.
Note: It is recommended that you also configure ```OSMOSCOPE_REFERER``` and ```OSMOSCOPE_ADMIN_MAIL``` to support troubleshooting in case any of your queries causes issues at the Overpass server. 

## The Stats Data File
Osmoscope Server will maintain a CSV file named ```stats_YOURLAYERNAME.csv``` for each of your layers. After every successful data retrieval from overpass, the number of returned features is stored to it.

