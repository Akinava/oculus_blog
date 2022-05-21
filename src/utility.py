import sys
from os import walk, replace
from os.path import join, isfile
import json
from datetime import datetime


def str_to_date_time(str_date_time):
    import settings
    return datetime.strptime(str_date_time, settings.DATETIME_FORMAT)


def get_files_list(dir):
    for _, _, files_list in walk(dir):
        return files_list


def get_project_dir():
    from settings import logger
    if len(sys.argv) < 2:
        logger.error('project dir required, run app: "{} poject_dir"'.format(sys.argv[0]))
        exit(1)
    return sys.argv[1]


def get_video_data_path():
    import settings
    return join(settings.project_dir, settings.VIDEO_DATA_FILE_NAME)


def read_video_data():
    return json.loads(read_file(get_video_data_path()))


def write_video_data(video_data):
    write_file(get_video_data_path(), json.dumps(video_data, indent=4))


def read_file(path):
    if not isfile(path):
        return None
    with open(path) as f:
        return f.read()


def write_file(path, data):
    with open(path, 'w') as f:
        return f.write(data)


def mv_file(file_path, dir):
    replace(file_path, dir)


def setup_logger():
    import logging
    import settings
    settings.logger = logging.getLogger(__name__)
    settings.logger.setLevel(settings.logging_level)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(settings.logging_format)
    handler.setFormatter(formatter)
    settings.logger.addHandler(handler)