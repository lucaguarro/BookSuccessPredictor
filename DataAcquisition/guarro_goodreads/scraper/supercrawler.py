from twisted.internet import reactor
from twisted.internet import task
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

from NordVPN import NordVPNHelper
from SQLiteHelper import SQLiteHelper

import pathlib
import logging

LOG_ENABLED = False

configure_logging(install_root_handler=False)

root_logger = logging.getLogger()
root_logger.setLevel(logging.WARNING)

scrapy_log_path = pathlib.Path().absolute() / "Log" / "scrapy.log"
file_handler = logging.FileHandler(scrapy_log_path, 'w', 'utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
root_logger.addHandler(file_handler)

setting = get_project_settings()
runner = CrawlerRunner(setting)

crawler_name = 'book_info_scraper'
runner.crawl(crawler_name)

d = runner.join()
d.addBoth(lambda _: reactor.stop())

nord = NordVPNHelper()

def periodicFunction():
    print("pausing spiders")
    for crawler in runner.crawlers:
        crawler.engine.pause()
    nord.changeVPN(False) # selects a random vpn server within current continental location
    print("recontinuing spider")
    for crawler in runner.crawlers:
        crawler.engine.unpause()

loop = task.LoopingCall(periodicFunction)

loopDeferred = loop.start(60*5)
reactor.run()