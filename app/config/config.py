# OSMOSCOPE_AREA_OR_BOUNDINGBOX defines a bounding box or an overpass area 
# (e.g. 'area:3600062611') to restrict overpass queries to an area of interest
# During development, you might use a smaller bounding box/area.
OSMOSCOPE_AREA_OR_BOUNDINGBOX = 'area:3600062611'

# The crontab OSMOSCOPE_UPDATE_SCHEDULE defines when all layers are 
# checked and updated (only in production mode)
OSMOSCOPE_UPDATE_SCHEDULE = '0 0 * * *'

# OSMOSCOPE_SERVERNAME is the public name which will be published via layers.json
OSMOSCOPE_SERVERNAME = 'Osmoscope Server'

# The OSMOSCOPE_REFERER is sent as header to the overpass server too help troubleshooting in 
# case of server sid issues caused by your overpass queries
# OSMOSCOPE_REFERER = "http://your-site.com/"

# The OSMOSCOPE_ADMIN_MAIL is sent as header to the overpass server too help troubleshooting in 
# case of server sid issues caused by your overpass queries
# OSMOSCOPE_ADMIN_MAIL = "your-mail@mail.org"
