import atexit
import logging
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from config import config
from osmoscope.validator import LayersValidator

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')

 
def update_layers():
    logger.info("Update osmoscope layers...")
    LayersValidator(config.OSMOSCOPE_AREA_OR_BOUNDINGBOX, 
        servername = config.OSMOSCOPE_SERVERNAME,
        referer = config.OSMOSCOPE_REFERER,
        fromHeader = config.OSMOSCOPE_ADMIN_MAIL
        ).check_all_layers()
               
 
if __name__ == '__main__':
    # TODO perhaps run on startup, if not any layer exists?
    if config.OSMOSCOPE_CHECK_ON_STARTUP:
        update_layers()

    schedule = config.OSMOSCOPE_UPDATE_SCHEDULE
    logger.info("Registrating update_layers job with schedule %s", schedule)
    scheduler = BlockingScheduler()
    # TODO Later on, multiple jobs could be defined, respecting the updates-properties of layer definitions 
    scheduler.add_job(func=update_layers, trigger=CronTrigger.from_crontab(schedule))
    scheduler.start()
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    
