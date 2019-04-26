import datetime
import json
import logging
import os 
import overpass
import re
from .overpass import OverpassCheck

logger = logging.getLogger(__name__)

class LayersValidator():

    def __init__(self, area_or_bounding_box, layers_configdir = 'config/', layersdir = 'layers/', 
        servername = 'Osmoscope Server', referer = None, fromHeader = None ):
        """ Create a new LayersValidator which can run checks for
            layer definitions stored in layersdif. 
            The layer file names must match layerdef_file_pattern.

            Parameters
            ----------
            area_or_bounding_box : string
                Either a bounding box in 'min_lat,min_lon,max_lat,max_lon' format or an overpass area like 'area:3600062611'.
            layers_configdir : string
                Directory path where layer definitions are read from.
            layersdir : string
                Directory path where layer check results will be written to.
            servername: string (default: Osmoscope Server)
                Server name (as written in layers.json)
            referer: string (optional)
                As a good practice, you should supply the site you will publish this layer for. It allows the 
                overpass service providers to get in contact with you, if your queries are causing trouble.
            fromHeader: string (optional)
                As a good practice, you should supply the your contact email. It allows the 
                overpass service providers to get in contact with you, if your queries are causing trouble.
        """     
        self.area_or_bounding_box = area_or_bounding_box
        self.layersdir = layersdir
        self.layers_configdir = layers_configdir
        self.layerdef_file_pattern = '^layer_.*\.json'
        self.servername = servername
        
        # TODO think about a dynamic plugin-like way to register validators
        self.validators = [OverpassCheck(self.area_or_bounding_box)]

    def check_all_layers(self):
        """ Iterates over all files in layers_configdir and tries to perform their check.

            Currently, only layer definition files containing a property 'overpass_query' 
            are supported.

            Further assumptions: 
            'id' could be a valid file name
            'geojson_url' will be generated as 'data_<id>.json'
            'stats_data_url' will be generated as 'stats_<id>.json'
        """
        for filename in os.listdir(self.layers_configdir):
            if (re.search(self.layerdef_file_pattern, filename)):
                with open(self.layers_configdir+filename) as layerdef_file:
                    layerdefinition = json.load(layerdef_file)
                    
                    logger.info("Loaded layer %s", layerdef_file.name)
                    
                    self.check_layer(layerdefinition)
        self._update_layers_index()

    def check_layer(self, layerdefinition):
        for validator in self.validators:
            if validator.is_supported(layerdefinition):
                count = validator.update_layer(layerdefinition, self.layersdir)
                stats_filename = self._get_stats_filename(layerdefinition)
                self._update_layers_file(layerdefinition, stats_filename)
                self._update_stats(stats_filename, datetime.datetime.now(), count)
                return
        logger.warn("Layer %s not supported by any validator.", layerdefinition['id'])

    def _get_stats_filename(self, layerdefinition):
        return 'stats_' + layerdefinition['id'] +'.csv'

    def _update_layers_file(self, layerdefinition, stats_filename):
        layerdefinition['stats_data_url'] = stats_filename
        # TODO Later on, this might change if tippicanoe is used to create vector tiles
        data_filename = 'data_' + layerdefinition['id'] + '.json'
        layerdefinition['geojson_url'] = data_filename
        layer_filename = 'layer_' + layerdefinition['id'] + '.json'
        with open(self.layersdir + layer_filename , 'w') as layersfile:
            json.dump(layerdefinition, layersfile, indent = 2)        

    def _update_stats(self, stats_filename, when, count):
        statfile_path = self.layersdir + stats_filename

        if not os.path.exists(statfile_path):
            with open(statfile_path, 'w+') as statsfile:
                statsfile.write('Date,Count\n')
        
        with open(statfile_path, 'a') as statsfile:
            statsfile.write('{},{}\n'.format(when.strftime('%Y-%m-%d'), count))

    def _update_layers_index(self):
        layers = []
        for filename in os.listdir(self.layersdir):
            if (re.search(self.layerdef_file_pattern, filename)):
                layers.append(filename)

        index = {
            'name': self.servername,
            'layers': layers
        }
        with open(self.layersdir + 'layers.json', 'w') as layersfile:
            json.dump(index, layersfile, indent = 2)
