from os import system
from os.path import join
from datetime import datetime, timedelta
import settings
from settings import (
    logger,
    DIR_VIDEO_INPUT,
    DIR_TIMINGS,
    VIDEO_EXT,
    TIMING_EXT,
    DIR_VIDEO_OUTPUT,
    DIR_VIDEO_DONE,
    DIR_VIDEO_FAIL,
    SCHEDULE,
    LAST_VIDEO_DATA_KEY,
    DATETIME_FORMAT,
)
from utility import (
    get_files_list,
    read_file,
    read_video_data,
    write_video_data,
    mv_file,
    str_to_date_time,
    get_project_dir,
)


DONE = 0
FAIL = 1


def cat_video():
    logger.info('project_dir: {}'.format(settings.project_dir))
    dir_input_video = get_dir_input_video()
    video_files_list = filter_file_by_ext(get_files_list(dir_input_video), VIDEO_EXT)
    for video_file_name in video_files_list:
        result = cat_video_by_timing(video_file_name)
        mv_result_files(result, video_file_name)


def mv_result_files(result, video_file_name):
    if result == FAIL:
        return
    input_video_file_path = get_video_file_path(video_file_name)
    result_video_file_path = get_result_file_path(result, video_file_name)
    timing_file_name = get_timing_file_name(video_file_name)
    input_timing_file_path = get_timing_file_path(timing_file_name)
    result_timing_file_path = get_result_file_path(result, timing_file_name)
    mv_file(input_video_file_path, result_video_file_path)
    mv_file(input_timing_file_path, result_timing_file_path)


def get_result_file_path(result, video_file_name):
    if result == DONE:
        return join(settings.project_dir, DIR_VIDEO_DONE, video_file_name)
    return join(settings.project_dir, DIR_VIDEO_FAIL, video_file_name)


def get_timing_file_name(video_file_name):
    return video_file_name.replace(VIDEO_EXT, TIMING_EXT)


def get_dir_input_video():
    return join(settings.project_dir, DIR_VIDEO_INPUT)


def get_video_file_path(video_file_name):
    return join(settings.project_dir, DIR_VIDEO_INPUT, video_file_name)


def get_timing_file_path(timing_file_name):
    return join(settings.project_dir, DIR_TIMINGS, timing_file_name)


def get_timing_lines(timing_data):
    return timing_data.split('\n')


def get_start_and_finish_time(line_index, timing_lines):
    return timing_lines[line_index], timing_lines[line_index + 1]


def timing_lines_len(timing_lines):
    return len(timing_lines) - 1


def cat_video_by_timing(video_file_name):
    input_video_file_path = get_video_file_path(video_file_name)
    timing_file_path = get_timing_file_path(get_timing_file_name(video_file_name))

    timing_data = read_file(timing_file_path)
    if timing_data is None:
        logger.warning('timing file {} not exist'.format(timing_file_path))
        return FAIL

    timing_lines = get_timing_lines(timing_data)
    logger.info('processing {}'.format(input_video_file_path))
    for line_index in range(timing_lines_len(timing_lines)):
        start_time, finish_time = get_start_and_finish_time(line_index, timing_lines)
        if '' in [start_time, finish_time]:
            continue
        ffmpeg_cat(input_video_file_path, start_time, finish_time)
    return DONE


def ffmpeg_cat(input_video_file_path, start_time, finish_time):
    ffmpeg_shell_command = make_ffmpeg_shell_command(input_video_file_path, start_time, finish_time)
    do_shell_command(ffmpeg_shell_command)


def make_ffmpeg_shell_command(input_video_file_path, start_time, finish_time):
    output_file_path = get_output_file_path()
    return 'ffmpeg -ss {start_time} -to {finish_time} -i "{input_video_file_path}" -c copy "{output_file_path}"'.format(
        start_time=start_time,
        finish_time=finish_time,
        input_video_file_path=input_video_file_path,
        output_file_path=output_file_path
    )


def get_last_video_date_time():
    last_video_time = get_last_video_time()
    if last_video_time is None:
        raise Exception('required data about last video')
    return last_video_time


def get_output_file_path():
    last_video_date_time = get_last_video_date_time()
    next_video_date_time = get_next_video_date_time(last_video_date_time)
    save_next_video_date_time(next_video_date_time)
    next_video_name = make_video_name(next_video_date_time)
    return join(settings.project_dir, DIR_VIDEO_OUTPUT, next_video_name)


def make_video_name(date_time):
    return '{}.{}'.format(date_time_to_str(date_time), VIDEO_EXT)


def save_next_video_date_time(next_video_date_time):
    next_video_date_time_str = date_time_to_str(next_video_date_time)
    video_data = read_video_data()
    video_data[LAST_VIDEO_DATA_KEY] = next_video_date_time_str
    write_video_data(video_data)


def get_last_video_time():
    return str_to_date_time(read_video_data()[LAST_VIDEO_DATA_KEY])

def date_time_to_str(date_time):
    return datetime.strftime(date_time, DATETIME_FORMAT)


def get_schedule():
    SCHEDULE.sort()
    schedule = []
    for t in SCHEDULE:
        schedule.append(datetime.strptime(t, '%H:%M').time())
    return schedule


def extract_current_date(date_time):
    return date_time.date()


def extract_next_date(date_time):
    return (date_time + timedelta(days=1)).date()


def get_last_schedule_time():
    return get_schedule()[-1]


def get_first_schedule_time():
    return get_schedule()[0]


def get_next_date(date_time):
    if date_time.time() < get_last_schedule_time():
        return extract_current_date(date_time)
    return extract_next_date(date_time)


def get_next_time(date_time):
    schedule = get_schedule()
    for t in schedule:
        if date_time.time() < t:
            return t
    return get_first_schedule_time()


def get_next_video_date_time(last_video_date_time):
    next_date = get_next_date(last_video_date_time)
    next_time = get_next_time(last_video_date_time)
    return datetime.combine(next_date, next_time)


def filter_file_by_ext(files_list, filter_ext):
    filtered_files = []
    for f in files_list:
        if filter_ext in f:
            filtered_files.append(f)
    return filtered_files


def do_shell_command(ffmpeg_shell_command):
    logger.info('run shell command | {}'.format(ffmpeg_shell_command))
    system(ffmpeg_shell_command)


if __name__ == '__main__':
    logger.info('app start')
    settings.project_dir = get_project_dir()
    cat_video()
    logger.info('app stop')
