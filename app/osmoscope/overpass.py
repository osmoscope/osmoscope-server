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


def _process_relations(resulting_geojson, relation_storage, way_storage, node_storage, nodes_used_in_ways):
    ways_used_in_relations = {}
    for rel_id in relation_storage:
        r = relation_storage[rel_id]
        rel = {}
        rel["type"] = "Feature"
        rid = "relation/{}".format(rel_id)
        rel["id"] = rid
        rel["properties"] = r["tags"] if "tags" in r else {}
        rel["properties"]["@id"] = rid

        way_types = []
        way_coordinate_blocks = []
        only_way_members = True
        for mem in r["members"]:
            if mem["type"] == "way":
                way_id = mem["ref"]
                processed = osmtogeojson._process_single_way(way_id, way_storage[way_id], node_storage, nodes_used_in_ways)
                way_types.append(processed["geometry"]["type"])
                way_coordinate_blocks.append(processed["geometry"]["coordinates"])
                ways_used_in_relations[way_id] = 1
            else:
                only_way_members = False

        rel["geometry"] = {}

        if only_way_members and len([x for x in way_types if x == "Polygon"]) == len(way_types):
            # all polygons, the resulting relation geometry is polygon
            rel["geometry"]["type"] = "Polygon"
            rel["geometry"]["coordinates"] = [x[0] for x in way_coordinate_blocks]
        elif only_way_members and len([x for x in way_types if x == "LineString"]) == len(way_types):
            rel["geometry"]["type"] = "MultiLineString"
            rel["geometry"]["coordinates"] = [x for x in way_coordinate_blocks]
            merge.merge_line_string(rel)
        else:
            # relation does not consist of Polygons or LineStrings only... 
            # In this case, overpass reports every individual member with its relation reference
            # Another option would be to export such a relation as GeometryCollection
           
            rel["geometry"]["type"] = "GeometryCollection"
            member_geometries = []
            for mem in r["members"]:
                if mem["type"] == "way":
                    way_id = mem["ref"]
                    processed = osmtogeojson._process_single_way(way_id, way_storage[way_id], node_storage, nodes_used_in_ways)
                    member_geometries.append(processed["geometry"])
                elif mem["type"] == "node":
                    node_id = mem["ref"]
                    node = node_storage[node_id]
                    geometry = {}
                    geometry["type"] = "Point"
                    geometry["coordinates"] = [node["lon"], node["lat"]]
                    member_geometries.append(geometry)
                    # Well, used_in_rels, but we want to ignore it as well, don't we?
                    nodes_used_in_ways[node_id] = 1
                else:
                    logger.warn("Relations members not yet handled (%s)", rel_id)
                
            rel["geometry"]["geometries"] = member_geometries
            
            
        resulting_geojson["features"].append(rel)
    return ways_used_in_relations

osmtogeojson._process_relations = _process_relations