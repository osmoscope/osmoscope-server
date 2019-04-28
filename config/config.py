# OSMOSCOPE_AREA_OR_BOUNDINGBOX defines a bounding box or an overpass area 
# (e.g. 'area:3600062611') to restrict overpass queries to an area of interest
# During development, you might use a smaller bounding box/area.
OSMOSCOPE_AREA_OR_BOUNDINGBOX = '48.699,9.199,48.70,9.2'

# The crontab OSMOSCOPE_UPDATE_SCHEDULE defines when all layers are 
# checked and updated (only in production mode)
OSMOSCOPE_UPDATE_SCHEDULE = '0 0 * * *'

# OSMOSCOPE_SERVERNAME is the public name which will be published via layers.json
OSMOSCOPE_SERVERNAME = 'Osmoscope Server'

# The OSMOSCOPE_REFERER is sent as header to the overpass server too help troubleshooting in 
# case of server sid issues caused by your overpass queries
OSMOSCOPE_REFERER = None # "http://your-site.com/"

# The OSMOSCOPE_ADMIN_MAIL is sent as header to the overpass server too help troubleshooting in 
# case of server sid issues caused by your overpass queries
OSMOSCOPE_ADMIN_MAIL = None # "YouMail@mail.org"

# If Osmoscope should run all checks on startup, set OSMOSCOPE_CHECK_ON_STARTUP to True. Otherwise
# checks are only run according to OSMOSCOPE_UPDATE_SCHEDULE
OSMOSCOPE_CHECK_ON_STARTUP = False
