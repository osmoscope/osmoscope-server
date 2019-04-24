from osmtogeojson import merge

def _determine_feature_type(way_nodes):
    # get more advanced???
    if way_nodes[0] == way_nodes[-1]:
        return "Polygon"
    else:
        return "LineString"


def _preprocess(j):
    """preprocess the file out into nodes ways and relations"""
    node_storage = {}
    nodes_reused = {}
    way_storage = {}
    ways_reused = {}
    relation_storage = {}
    for elem in j["elements"]:
        # on our first pass, we go through and put all the nodes into storage
        eid = elem["id"]
        if elem["type"] == "node":
            # sometimes a node is repeated twice in the OSM output; once with tags, once without. This affects filtering out nodes in ways
            if eid not in node_storage:
                node_storage[eid] = elem
            else:
                # if it's just a pure duplicate, which DOES AND CAN happen with certain overpass queries, just drop it
                if elem != node_storage[eid]:
                    nodes_reused[eid] = 1
                    # take the one that has the tags.
                    if "tags" in elem:
                        node_storage[eid] = elem

        # handle ways
        elif elem["type"] == "way":
            if eid not in way_storage:
                way_storage[eid] = elem
            else:
                # if it's just a pure duplicate, which DOES AND CAN happen with certain overpass queries, just drop it
                if elem != way_storage[eid]:
                    ways_reused[eid] = 1
                    # take the one that has the tags.
                    if "tags" in elem:
                        way_storage[eid] = elem

        # handle relations
        elif elem["type"] == "relation":
            if eid not in relation_storage:
                relation_storage[eid] = elem
            else:
                raise Exception()

    return way_storage, ways_reused, node_storage, nodes_reused, relation_storage


def _process_relations(resulting_geojson, relation_storage, way_storage, node_storage, nodes_used_in_ways):
    ways_used_in_relations = {}
    for rel_id in relation_storage:
        r = relation_storage[rel_id]
        rel = {}
        rel["type"] = "Feature"
        #rid = "relation/{}".format(rel_id)
        rid = "r{}".format(rel_id)
        rel["id"] = rid
        rel["properties"] = r["tags"] if "tags" in r else {}
        rel["properties"]["@id"] = rid

        way_types = []
        way_coordinate_blocks = []
        for mem in r["members"]:
            if mem["type"] == "way":
                way_id = mem["ref"]
                processed = _process_single_way(way_id, way_storage[way_id], node_storage, nodes_used_in_ways)
                way_types.append(processed["geometry"]["type"])
                way_coordinate_blocks.append(processed["geometry"]["coordinates"])
                ways_used_in_relations[way_id] = 1
            # 
            # else:
                # print(mem["type"])

        rel["geometry"] = {}

        if len([x for x in way_types if x == "Polygon"]) == len(way_types):
            # all polygons, the resulting relation geometry is polygon
            rel["geometry"]["type"] = "Polygon"
            rel["geometry"]["coordinates"] = [x[0] for x in way_coordinate_blocks]
        elif len([x for x in way_types if x == "LineString"]) == len(way_types):
            rel["geometry"]["type"] = "MultiLineString"
            rel["geometry"]["coordinates"] = [x for x in way_coordinate_blocks]
            merge.merge_line_string(rel)
        else:
            # in this case, overpass reports every individual member with its relation reference
            # print(way_types)
            print("Ignoring feature relation {}".format(rel_id))
            continue # do not add features without geom for now

        resulting_geojson["features"].append(rel)
    return ways_used_in_relations


def _process_single_way(way_id, w, node_storage, nodes_used_in_ways):
    way = {}
    way["type"] = "Feature"
    #wid = "way/{}".format(way_id)
    wid = "w{}".format(way_id)
    way["id"] = wid
    way["properties"] = w["tags"] if "tags" in w else {}
    way["properties"]["@id"] = wid  # the original osmtogeojson does this, so following suit
    way["geometry"] = {}

    geo_type = _determine_feature_type(w["nodes"])
    way["geometry"]["type"] = geo_type

    if geo_type == "Polygon":
        way["geometry"]["coordinates"] = [[]]  # Polygons are list of list of lists...
        append_here = way["geometry"]["coordinates"][0]
    elif geo_type == "LineString":
        way["geometry"]["coordinates"] = []
        append_here = way["geometry"]["coordinates"]

    for n in w["nodes"]:
        node = node_storage[n]
        append_here.append([node["lon"], node["lat"]])
        nodes_used_in_ways[n] = 1

    return way


def _process_ways(resulting_geojson, way_storage, ways_used_in_relations, ways_reused, node_storage, nodes_used_in_ways):
    for way_id in way_storage:
        if way_id not in ways_used_in_relations or way_id in ways_reused:
            w = way_storage[way_id]
            way = _process_single_way(way_id, w, node_storage, nodes_used_in_ways)
            resulting_geojson["features"].append(way)


def _process_nodes(resulting_geojson, node_storage, nodes_used_in_ways, nodes_reused):
    # dump the nodes that were not a part of a way into the resulting json
    for nid in node_storage:
        if nid not in nodes_used_in_ways or nid in nodes_reused:
            n = node_storage[nid]
            node = {}
            node["type"] = "Feature"
            #new_id = "node/{}".format(n["id"])
            new_id = "n{}".format(n["id"])
            node["id"] = new_id
            node["properties"] = n["tags"] if "tags" in n else {}
            node["properties"]["@id"] = new_id
            node["geometry"] = {}
            node["geometry"]["type"] = "Point"
            node["geometry"]["coordinates"] = [n["lon"], n["lat"]]
            resulting_geojson["features"].append(node)


def process_osm_json(j):
    resulting_geojson = {}
    resulting_geojson["type"] = "FeatureCollection"
    resulting_geojson["features"] = []
    way_storage, ways_reused, node_storage, nodes_reused, relation_storage = _preprocess(j)
    nodes_used_in_ways = {}
    ways_used_in_relations = _process_relations(resulting_geojson, relation_storage, way_storage, node_storage, nodes_used_in_ways)
    _process_ways(resulting_geojson, way_storage, ways_used_in_relations, ways_reused, node_storage, nodes_used_in_ways)
    _process_nodes(resulting_geojson, node_storage, nodes_used_in_ways, nodes_reused)
    return resulting_geojson
