#!/usr/bin/python3
import time
import datetime
import logging
import sys
# from systemd.journal import JournaldLogHandler
from systemd.journal import JournalHandler

logger = logging.getLogger(__name__)

# journald_handler = JournaldLogHandler()

# journald_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))

# logger.addHandler(journald_handler)
# handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(JournalHandler())
logger.setLevel(logging.INFO)
# formatter = logging.Formatter(fmt="%(asctime)s %(name)s.%(levelname)s: %(message)s")
# handler.setFormatter(formatter)
# logger.addHandler(handler)

while True:
    logger.info(datetime.datetime.now())
    time.sleep(5)

