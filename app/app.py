import atexit
import logging
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import Flask, request, send_from_directory
from osmoscope.validator import LayersValidator

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_url_path='')
app.config.from_pyfile('config.py', silent=True)
 
@app.route('/')
def osmoscope_server():
    return 'This is osmoscope server'

@app.route('/layers/<path:path>')
def send_layers(path):
    return send_from_directory('layers', path)

@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.cache_control.no_store = True 
    return response

def update_layers():
    logger.info("Triggered update_layers")
    LayersValidator(app.config['OSMOSCOPE_AREA_OR_BOUNDINGBOX']).check_all_layers()
 
if __name__ == '__main__':
    update_layers()

    if app.config['ENV'] == 'production':
        schedule = '0 0 * * *'
        logger.info("Registring update_layers job with schedule %s", schedule)
        scheduler = BackgroundScheduler()
        # TODO Later on, multiple jobs respecting the updates-properties of layer definitions 
        scheduler.add_job(func=update_layers, trigger=CronTrigger.from_crontab(schedule))
        scheduler.start()
        # Shut down the scheduler when exiting the app
        atexit.register(lambda: scheduler.shutdown())

    app.run(host='0.0.0.0')
