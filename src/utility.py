import sys
from os import walk, replace
from os.path import join, isfile
import json
from datetime import datetime


def get_metadata_file_path():
    import settings
    return join(settings.project_dir, settings.METADATA_FILE_NAME)


def read_metadata():
    return read_json(get_metadata_file_path())


def save_metadata(data):
    write_json(get_metadata_file_path(), data)


def str_to_date_time(str_date_time):
    import settings
    return datetime.strptime(str_date_time, settings.DATETIME_FORMAT)


def get_files_list(dir):
    for _, _, files_list in walk(dir):
        return files_list


def set_project_dir():
    import settings
    if len(sys.argv) < 2:
        settings.logger.error('project dir required, run app: "{} poject_dir"'.format(sys.argv[0]))
        exit(1)
    settings.project_dir = sys.argv[1]


def read_json(path):
    data = read_file(path)
    if data is None:
        return data
    return json.loads(data)


def write_json(path, data):
    write_file(path, json.dumps(data, indent=4))


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