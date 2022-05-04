import logging
from utility import setup_logger


SCHEDULE = [
    '12:00',
    # '18:00',
]

VIDEO_DATA_FILE_NAME = 'video_data.json'
LAST_VIDEO_DATA_KEY = 'last_video'
DIR_VIDEO_INPUT = 'input'
DIR_VIDEO_OUTPUT = 'output'
DIR_VIDEO_DONE = 'done'
DIR_VIDEO_FAIL = 'output'
DIR_VIDEO_POSTED = 'posted'
DIR_TIMINGS = 'input'
VIDEO_EXT = 'mp4'
TIMING_EXT = 'txt'
DATETIME_FORMAT = '%Y.%m.%d %H:%M'
FORISMATIC_API_URL = 'https://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en'
FORISMATIC_API_DELAY = 2
VIDEO_REQUEST_BODY_KEY = 'video_request_body'
VIDEO_TITLE_PLACE = ['snippet', 'title']
VIDEO_PUBLISH_AT_PLACE = ['status', 'publishAt']
logging_level = logging.INFO
logging_format = '%(asctime)s : %(levelname)s: %(threadName)s : %(module)s : %(funcName)s : %(message)s'

setup_logger()
