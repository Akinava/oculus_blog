import logging
from utility import setup_logger


SCHEDULE = [
    '12:00',
    # '18:00',
]
LAST_VIDEO_FILE = 'last_video.txt'

DIR_VIDEO_INPUT = 'input'
DIR_VIDEO_OUTPUT = 'output'
DIR_VIDEO_DONE = 'done'
DIR_VIDEO_FAIL = 'output'
DIR_TIMINGS = 'input'

VIDEO_EXT = 'mp4'
TIMING_EXT = 'txt'

DATETIME_FORMAT = '%Y.%m.%d %H:%M'

logging_level = logging.INFO
logging_format = '%(asctime)s : %(levelname)s: %(threadName)s : %(module)s : %(funcName)s : %(message)s'

setup_logger()
