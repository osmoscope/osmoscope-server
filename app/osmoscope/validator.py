import datetime
import json
import logging
import os 
import overpass
import re
from .overpass import OverpassCheck

logger = logging.getLogger(__name__)

class LayersValidator():

    def __init__(self, area_or_bounding_box, layersdir = 'layers/', layerdef_file_pattern = '^layer_.*\.json'):
        """ Create a new LayersValidator which can run checks for
            layer definitions stored in layersdif. 
            The layer file names must match layerdef_file_pattern.

            Parameters
            ----------
            area_or_bounding_box : string
                Either a bounding box in 'min_lat,min_lon,max_lat,max_lon' format or an overpass area like 'area:3600062611'.
            layersdir : string
                Directory path where layer definitions are stored and check results will be written to.
            layerdef_file_pattern : string
                Pattern which must be matched by a layer definition file.    
        """     
        self.area_or_bounding_box = area_or_bounding_box
        self.layersdir = layersdir
        self.layerdef_file_pattern = layerdef_file_pattern
        
        # TODO think about a dynamic plugin-like way to register validators
        self.validators = [OverpassCheck(self.area_or_bounding_box)]

    def check_all_layers(self):
        """ Iterates over all files in layersdir and tries to perform their check.

            Currently, only layer definition files containing a property 'overpass_query' 
            are supported.

            Further assumptions: 
            layerdefinition files start with 'layer_'
            'id' could be a valid file name
            'geojson_url' is '<id>.json'
            'stats_data_url' is 'stats_<id>.json'
        """
        # TODO Should layer files be read from a config dir? 
        # If yes, some properties like e.g. stats-file could be left out from config files
        # and would be generated 
        for filename in os.listdir(self.layersdir):
            if (re.search(self.layerdef_file_pattern, filename)):
                with open(self.layersdir+filename) as layerdef_file:
                    layerdefinition = json.load(layerdef_file)
                    
                    logger.info("Loaded layer %s", layerdef_file.name)
                    
                    self.check_layer(layerdefinition)

    def check_layer(self, layerdefinition):
        for validator in self.validators:
            if validator.is_supported(layerdefinition):
                count = validator.update_layer(layerdefinition, self.layersdir)
                self._update_stats(layerdefinition['id'], datetime.datetime.now(), count)
                return
        logger.warn("Layer %s not supported by any validator.", layerdefinition['id'])

    def _update_stats(self, layer_name, when, count):
        # TODO should we calculate this or reuse name in layerdefinition, which might contradict each other?
        statfile_name = self.layersdir + "stats_" + layer_name+'.csv'

        if not os.path.exists(statfile_name):
            with open(statfile_name, 'w+') as statsfile:
                statsfile.write('Date,Count\n')
        
        with open(statfile_name, 'a') as statsfile:
            statsfile.write('{},{}\n'.format(when.strftime('%Y-%m-%d'), count))
