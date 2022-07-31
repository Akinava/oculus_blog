import logging
from utility import setup_logger, set_project_dir


# SCHEDULE = [
#     '12:00',
#     '18:00',
# ]

CLIENT_SECRET_FILE = 'client_secret.json'
CREDENTIALS_PICKLE_FILE = 'credentials.pickle'
METADATA_FILE_NAME = 'metadata.json'

DIR_VIDEO_INPUT = 'input'
DIR_VIDEO_OUTPUT = 'output'
DIR_VIDEO_DONE = 'done'
DIR_VIDEO_FAIL = 'output'
DIR_VIDEO_POSTED = 'posted'

VIDEO_EXT = 'mp4'
TIMING_EXT = 'txt'
DATETIME_FORMAT = '%Y.%m.%d %H:%M'

FORISMATIC_API_URL = 'https://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang={}'
FORISMATIC_API_DELAY = 2

logging_level = logging.INFO
logging_format = '%(asctime)s : %(levelname)s: %(threadName)s : %(module)s : %(funcName)s : %(message)s'

setup_logger()
set_project_dir()
