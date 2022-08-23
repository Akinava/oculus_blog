import sys
from os import walk, replace, system
from os.path import join, isfile
import json
from datetime import datetime
import time


def get_marks():
    marks_metadata = read_metadata()['marks']
    return list(marks_metadata.keys())


def get_uuid_time():
    return int(time.time() * 10**4 % 10**10)


def get_metadata_file_path():
    import settings
    return join(settings.project_dir, settings.METADATA_FILE_NAME)


def read_metadata():
    return read_json(get_metadata_file_path())


def save_metadata(data):
    write_json(get_metadata_file_path(), data)


def get_files_list(dir):
    return next(walk(dir))[2]


def get_subdir_list(dir):
    return next(walk(dir))[1]


def get_data_dir_path(dir_name):
    import settings
    return join(settings.project_dir, dir_name)


def set_project_dir():
    import settings
    if hasattr(settings, 'project_dir'):
        return
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


def do_shell_command(ffmpeg_shell_command):
    import settings
    settings.logger.info('run shell command | {}'.format(ffmpeg_shell_command))
    system(ffmpeg_shell_command)


def setup_logger():
    import settings
    if hasattr(settings, 'logger'):
        return
    import logging
    settings.logger = logging.getLogger(__name__)
    settings.logger.setLevel(settings.logging_level)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(settings.logging_format)
    handler.setFormatter(formatter)
    settings.logger.addHandler(handler)
