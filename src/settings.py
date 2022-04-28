import logging
from utility import setup_logger


DIR_VIDEO_INPUT = 'input'
DIR_VIDEO_OUTPUT = 'output'
DIR_VIDEO_DONE = 'done'
DIR_VIDEO_FAIL = 'fail'
DIR_TIMINGS = 'timings'

VIDEO_EXT = 'mp4'
TIMING_EXT = 'txt'
FILE_NAME_INDENT = 4
FIRST_OUTPUT_FILE_INDEX = 0

logging_level = logging.INFO
logging_format = '%(asctime)s : %(levelname)s: %(threadName)s : %(module)s : %(funcName)s : %(message)s'

setup_logger()
