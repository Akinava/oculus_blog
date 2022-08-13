import uuid
from os import walk, mkdir
from os.path import join, isfile, isdir
from datetime import datetime, timedelta
import settings
from settings import (
    logger,
    DIR_NAME_VIDEO_TIMED,
    VIDEO_EXT,
    TIMING_EXT,
    DIR_NAME_VIDEO_TO_POST,
    DIR_NAME_VIDEO_TIMING_PROCESSED,
    DATETIME_FORMAT,
    MAX_FILES_TO_POST,
)
from utility import (
    get_files_list,
    get_subdir_list,
    read_file,
    mv_file,
    get_data_dir_path,
    do_shell_command,
    read_metadata,
    save_metadata,
)


DONE = 0
FAIL = 1


def cat_video():
    dir_input_video = get_data_dir_path(DIR_NAME_VIDEO_TIMED)
    video_files_list = filter_file_by_ext(get_files_list(dir_input_video), VIDEO_EXT)
    for video_file_name in video_files_list:
        logger.info(video_file_name)
        if not isfile(get_input_timing_file_path(video_file_name)):
            continue
        cat_video_by_timing(video_file_name)
        mv_processed_files(video_file_name)


def mv_processed_files(video_file_name):
    input_video_file_path = get_input_video_file_path(video_file_name)
    processed_video_file_path = get_processed_video_file_path(video_file_name)

    input_timing_file_path = get_input_timing_file_path(video_file_name)
    processed_timing_file_path = get_processed_timing_file_path(video_file_name)
    mv_file(input_video_file_path, processed_video_file_path)
    mv_file(input_timing_file_path, processed_timing_file_path)


def get_input_video_file_path(video_file_name):
    return join(
        settings.project_dir,
        DIR_NAME_VIDEO_TIMED,
        video_file_name)


def get_processed_video_file_path(video_file_name):
    return join(
        settings.project_dir,
        DIR_NAME_VIDEO_TIMING_PROCESSED,
        video_file_name)


def get_to_post_video_file_path(video_file_name, sub_dir):
    next_date = get_next_date_time(video_file_name)
    mark = get_mark(video_file_name)
    return join(
        settings.project_dir,
        DIR_NAME_VIDEO_TO_POST,
        sub_dir,
        '{}_{}.{}'.format(mark, next_date, VIDEO_EXT)
    )


def get_timing_file_name(video_file_name):
    return video_file_name.replace(VIDEO_EXT, TIMING_EXT)


def get_input_timing_file_path(video_file_name):
    return join(
        settings.project_dir,
        DIR_NAME_VIDEO_TIMED,
        get_timing_file_name(video_file_name))


def get_processed_timing_file_path(video_file_name):
    return join(
        settings.project_dir,
        DIR_NAME_VIDEO_TIMING_PROCESSED,
        get_timing_file_name(video_file_name))


def filter_file_by_ext(files_list, filter_ext):
    filtered_files = []
    for f in files_list:
        if filter_ext in f:
            filtered_files.append(f)
    return filtered_files


def get_output_video_file_path(video_file_name):
    mark = get_mark(video_file_name)
    return join(
        settings.project_dir,
        DIR_NAME_VIDEO_TIMED,
        '{}_{}.{}'.format(mark, uuid.uuid4().hex, VIDEO_EXT))


def get_timing_lines(timing_data):
    return timing_data.split('\n')


def get_start_and_finish_time(line_index, timing_lines):
    return timing_lines[line_index], timing_lines[line_index + 1]


def timing_lines_len(timing_lines):
    return len(timing_lines) - 1


def cat_video_by_timing(video_file_name):
    input_video_file_path = get_input_video_file_path(video_file_name)
    timing_file_path = get_input_timing_file_path(get_timing_file_name(video_file_name))
    timing_data = read_file(timing_file_path)

    timing_lines = get_timing_lines(timing_data)
    logger.info('processing {}'.format(input_video_file_path))
    for line_index in range(timing_lines_len(timing_lines)):
        start_time, finish_time = get_start_and_finish_time(line_index, timing_lines)
        if '' in [start_time, finish_time]:
            continue
        output_video_file_path = get_output_video_file_path(video_file_name)
        ffmpeg_cat(input_video_file_path, output_video_file_path, start_time, finish_time)
    return DONE


def ffmpeg_cat(input_video_file_path, output_video_file_path, start_time, finish_time):
    ffmpeg_shell_command = make_ffmpeg_shell_command(input_video_file_path, output_video_file_path, start_time, finish_time)
    do_shell_command(ffmpeg_shell_command)


def make_ffmpeg_shell_command(input_video_file_path, output_video_file_path, start_time, finish_time):
    return 'ffmpeg -ss {start_time} -to {finish_time} -i "{input_video_file_path}" -c copy "{output_video_file_path}"'.format(
        start_time=start_time,
        finish_time=finish_time,
        input_video_file_path=input_video_file_path,
        output_video_file_path=output_video_file_path
    )


def get_mark(video_file_name):
    return video_file_name.split('_')[0]


def mark_in_video_file_name(video_file_name):
    mark = get_mark(video_file_name)
    marks = list(read_metadata()['marks'].keys())
    return mark in marks


def get_metadata_timer(video_file_name):
    mark = get_mark(video_file_name)
    metadata_timers = read_metadata()['timers']
    for name, data in metadata_timers.items():
        if mark in data['marks']:
            return name, data


def get_metadata_timer_value(video_file_name):
    _, value = get_metadata_timer(video_file_name)
    return value


def get_metadata_timer_name(video_file_name):
    name, _ = get_metadata_timer(video_file_name)
    return name


def get_next_date_time(video_file_name):
    value = get_metadata_timer_value(video_file_name)
    return value['next_date_time']


def date_time_to_str(date_time):
    return datetime.strftime(date_time, DATETIME_FORMAT)


def str_to_date_time(str_date_time):
    return datetime.strptime(str_date_time, settings.DATETIME_FORMAT)


def scheduling_video():
    dir_input_video = get_data_dir_path(DIR_NAME_VIDEO_TIMED)
    video_files_list = get_files_list(dir_input_video)
    for video_file_name in video_files_list:
        logger.info(video_file_name)
        if not mark_in_video_file_name(video_file_name):
            continue
        mv_video_to_post_dir(video_file_name)
        save_next_video_date_time(video_file_name)


def get_to_post_sub_dir(video_file_name):
    to_post_dir_path = get_data_dir_path(DIR_NAME_VIDEO_TO_POST)
    subdir_list = get_subdir_list(to_post_dir_path)
    for subdir_name in subdir_list:
        if len(get_files_list(join(to_post_dir_path, subdir_name))) < MAX_FILES_TO_POST:
            return subdir_name
    return make_to_post_subdir(video_file_name)


def make_to_post_subdir(video_file_name):
    next_date = get_next_date_time(video_file_name)[:10]
    subdir_name = '{}_{}'.format(next_date, uuid.uuid4().hex[:8])
    to_post_dir_path = get_data_dir_path(DIR_NAME_VIDEO_TO_POST)
    while subdir_name in get_subdir_list(to_post_dir_path):
        subdir_name = uuid.uuid4().hex[:8]
    mkdir(join(to_post_dir_path, subdir_name))
    return subdir_name


def mv_video_to_post_dir(video_file_name):
    input_video_file_path = get_input_video_file_path(video_file_name)
    sub_dir = get_to_post_sub_dir(video_file_name)
    to_post_video_file_path = get_to_post_video_file_path(video_file_name, sub_dir)
    mv_file(input_video_file_path, to_post_video_file_path)


def save_next_video_date_time(video_file_name):
    next_video_date_time = make_next_video_date_time(video_file_name)
    next_video_date_time_str = date_time_to_str(next_video_date_time)
    metadata = read_metadata()
    timer_name = get_metadata_timer_name(video_file_name)
    metadata['timers'][timer_name]['next_date_time'] = next_video_date_time_str
    save_metadata(metadata)


def make_next_date(video_file_name):
    last_video_date_time = str_to_date_time(get_next_date_time(video_file_name))
    if last_video_date_time.time() < get_last_schedule_time(video_file_name):
        return extract_current_date(last_video_date_time)
    return extract_next_date(last_video_date_time)


def extract_current_date(date_time):
    return date_time.date()


def extract_next_date(date_time):
    return (date_time + timedelta(days=1)).date()


def get_last_schedule_time(video_file_name):
    return get_schedule(video_file_name)[-1]


def get_first_schedule_time(video_file_name):
    return get_schedule(video_file_name)[0]


def get_schedule(video_file_name):
    value = get_metadata_timer_value(video_file_name)
    schedule_list = value['schedule']
    schedule_list.sort()
    schedule = []
    for t in schedule_list:
        schedule.append(datetime.strptime(t, DATETIME_FORMAT[9:]).time())
    return schedule


def make_next_time(video_file_name):
    schedule = get_schedule(video_file_name)
    last_video_date_time = str_to_date_time(get_next_date_time(video_file_name))
    for t in schedule:
        if last_video_date_time.time() < t:
            return t
    return get_first_schedule_time(video_file_name)


def make_next_video_date_time(video_file_name):
    next_date = make_next_date(video_file_name)
    next_time = make_next_time(video_file_name)
    return datetime.combine(next_date, next_time)


if __name__ == '__main__':
    logger.info('app start')
    logger.info('project_dir: {}'.format(settings.project_dir))
    cat_video()
    scheduling_video()
    logger.info('app stop')
