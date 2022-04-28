from os import walk, system, replace
from os.path import join, isfile
from settings import (
    logger,
    DIR_VIDEO_INPUT,
    DIR_TIMINGS,
    VIDEO_EXT,
    TIMING_EXT,
    DIR_VIDEO_OUTPUT,
    FIRST_OUTPUT_FILE_INDEX,
    FILE_NAME_INDENT,
    DIR_VIDEO_DONE,
    DIR_VIDEO_FAIL,
)


DONE = 0
FAIL = 1


def cat_video(project_dir):
    logger.info('project_dir: {}'.format(project_dir))
    dir_input_video = get_dir_input_video(project_dir)
    video_files_list = get_files_list(dir_input_video)
    for video_file_name in video_files_list:
        result = cat_video_by_timing(project_dir, video_file_name)
        mv_result_files(result, project_dir, video_file_name)


def mv_result_files(result, project_dir, video_file_name):
    input_video_file_path = get_video_file_path(project_dir, video_file_name)
    result_video_file_path = get_result_file_path(project_dir, result, video_file_name)
    timing_file_name = get_timing_file_name(video_file_name)
    input_timing_file_path = get_timing_file_path(project_dir, timing_file_name)
    result_timing_file_path = get_result_file_path(project_dir, result, timing_file_name)
    mv_file(input_video_file_path, result_video_file_path)
    mv_file(input_timing_file_path, result_timing_file_path)


def get_result_file_path(project_dir, result, video_file_name):
    if result == DONE:
        return join(project_dir, DIR_VIDEO_DONE, video_file_name)
    return join(project_dir, DIR_VIDEO_FAIL, video_file_name)


def get_timing_file_name(video_file_name):
    return video_file_name.replace(VIDEO_EXT, TIMING_EXT)


def get_dir_input_video(project_dir):
    return join(project_dir, DIR_VIDEO_INPUT)


def get_video_file_path(project_dir, video_file_name):
    return join(project_dir, DIR_VIDEO_INPUT, video_file_name)


def get_timing_file_path(project_dir, timing_file_name):
    return join(project_dir, DIR_TIMINGS, timing_file_name)


def get_timing_lines(timing_data):
    return timing_data.split('\n')


def get_start_and_finish_time(line_index, timing_lines):
    return timing_lines[line_index], timing_lines[line_index + 1]


def timing_lines_len(timing_lines):
    return len(timing_lines) - 1


def cat_video_by_timing(project_dir, video_file_name):
    input_video_file_path = get_video_file_path(project_dir, video_file_name)
    timing_file_path = get_timing_file_path(project_dir, get_timing_file_name(video_file_name))

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
        ffmpeg_cat(project_dir, input_video_file_path, start_time, finish_time)
    return DONE


def ffmpeg_cat(project_dir, input_video_file_path, start_time, finish_time):
    ffmpeg_shell_command = make_ffmpeg_shell_command(project_dir, input_video_file_path, start_time, finish_time)
    do_shell_command(ffmpeg_shell_command)


def make_ffmpeg_shell_command(project_dir, input_video_file_path, start_time, finish_time):
    output_file_path = get_output_file_path(project_dir)
    return 'ffmpeg -ss {start_time} -to {finish_time} -i {input_video_file_path} -c copy {output_file_path}'.format(
        start_time=start_time,
        finish_time=finish_time,
        input_video_file_path=input_video_file_path,
        output_file_path=output_file_path
    )


def get_output_file_path(project_dir):
    output_dir = join(project_dir, DIR_VIDEO_OUTPUT)
    files_list = get_files_list(output_dir)
    files_index_list = []
    for fname in files_list:
        basename, _ = fname.split('.')
        if not basename.isdigit():
            continue
        files_index_list.append(int(basename))

    if len(files_index_list) == 0:
        last_file_index = FIRST_OUTPUT_FILE_INDEX
    else:
        files_index_list.sort()
        last_file_index = files_index_list[-1] + 1
    output_file_name = '{num:0{width}}.{ext}'.format(num=last_file_index, width=FILE_NAME_INDENT, ext=VIDEO_EXT)
    return join(output_dir, output_file_name)


def get_files_list(dir):
    for _, _, files_list in walk(dir):
        return files_list


def mv_file(file_path, dir):
    replace(file_path, dir)


def read_file(path):
    if not isfile(path):
        return None
    with open(path) as f:
        return f.read()


def do_shell_command(ffmpeg_shell_command):
    logger.info('run shell command | {}'.format(ffmpeg_shell_command))
    system(ffmpeg_shell_command)
