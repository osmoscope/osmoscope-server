import datetime
import json
import logging
import os 
import overpass
from osmtogeojson import osmtogeojson

logger = logging.getLogger(__name__)

class OverpassCheck:

    def __init__(self, area_or_boundingbox):
        self.area_or_boundingbox = area_or_boundingbox
    
    def is_supported(self, layerdefinition):
        return 'overpass_query' in layerdefinition

    def update_layer(self, layerdefinition, layersdir):
        """Performs check, writes data to <layerid>.json and returns number of results found.
          The param layerdefinition is expected as a dict declaring a property "overpass_query" which
          is the raw overpass query to be sent to the overpass-api server.
          The query may contain placeholders (for now only {{bbox}}, which will be replaced
          by a
        """
        # TODO This function might be generic and either be moved to a parent class or 
        # to the calling validator... Disadvantage of the latter: very large result sets would
        # require too much memory. Another option might be to pass in an output stream, probably filtered...
        geojson_response = self.perform_check(layerdefinition)

        layer_name = layerdefinition['id']
        
        # TODO how should we apply filtered entries? Already when generating layer? Or only on client side? 
        # Perhaps update_layer should not only return the number but the geojson which then could be filtered 
        # by the framework
        with open(layersdir + 'data_' + layer_name+'.json', 'w+') as outfile:  
            json.dump(geojson_response, outfile)

        return len(geojson_response['features'])


    def perform_check(self, layerdefinition):
        """Performs check and returns geojson collectioin of results found.
          The param layerdefinition is expected as a dict declaring a property "overpass_query" which
          is the raw overpass query to be sent to the overpass-api server.
          The query may contain placeholders (for now only {{bbox}}, which will be replaced
          by self.area_or_boundingbox.
        """
        
        query = layerdefinition['overpass_query']

        api = overpass.API(timeout=600)
        bbQuery = BoundingBoxQuery(query, self.area_or_boundingbox)
        logger.debug('Retrieve overpass layer via query %s', bbQuery)
        # overpass-wrapper currently does not support custom settings, so build=False
        response = api.get(bbQuery, 'json', build=False)
        geojson_response = osmtogeojson.process_osm_json(response)

        return geojson_response


class BoundingBoxQuery(object):
    """Query which replaces {{bbox}} placeholders by given bounding box/area."""

    def __init__(self, query, bbox):
        """
        Initialize query with given bounding box.
        :param bbox Bounding box with limit values in format "west, south,
        east, north".
        """
        self.query = query
        self.bbox = bbox
       
    def __str__(self):
        return self.query.replace('{{bbox}}',self.bbox) 

