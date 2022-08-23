import logging
from utility import setup_logger, set_project_dir


CLIENT_SECRET_FILE = 'client_secret.json'
CREDENTIALS_PICKLE_FILE = 'credentials.pickle'
METADATA_FILE_NAME = 'metadata.json'

DIR_NAME_VIDEO_RAW = '0.raw'
DIR_NAME_VIDEO_TAGGED = '1.tagged'
DIR_NAME_VIDEO_TIMED = '2.timed'
DIR_NAME_VIDEO_TO_POST = '3.to_post'
DIR_NAME_VIDEO_TIMING_PROCESSED = 'timing_processed'
DIR_NAME_VIDEO_CLIPPED = 'clipped'

VIDEO_EXT = 'mp4'
TIMING_EXT = 'txt'
DATETIME_FORMAT = '%Y.%m.%d_%H.%M'
MAX_FILES_TO_POST = 15

FORISMATIC_API_URL = 'https://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang={}'
FORISMATIC_API_DELAY = 2

logging_level = logging.INFO
logging_format = '%(asctime)s : %(levelname)s: %(threadName)s : %(module)s : %(funcName)s : %(message)s'

setup_logger()
set_project_dir()
