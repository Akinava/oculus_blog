from os.path import join
import settings
from settings import (
    logger,
    DIR_NAME_VIDEO_RAW,
    DIR_NAME_VIDEO_TAGGED,
)
from utility import (
    get_dir_path,
    get_files_list,
    do_shell_command,
    read_metadata,
    mv_file,
)


def get_marks():
    marks_metadata = read_metadata()['marks']
    return list(marks_metadata.keys())


def make_help_print(marks):
    help_print = []
    for mark in marks:
        help_print.append('{}-{}'.format(marks.index(mark)+1, mark))
    return '\n'.join(help_print)


def tag_video():
    dir_raw_video = get_dir_path(DIR_NAME_VIDEO_RAW)
    marks = get_marks()
    help_print = make_help_print(marks)
    files_list = get_files_list(dir_raw_video)
    for file_name in files_list:
        file_path = join(dir_raw_video, file_name)
        print(file_path)
        do_shell_command('mplayer {}'.format(file_path))
        print('choose tag', '=' * 10)
        print(help_print)
        tag_index = input()
        mark = marks[int(tag_index)-1]
        print('chosen', mark)
        new_file_path = join(
            get_dir_path(DIR_NAME_VIDEO_TAGGED),
            '{}_{}.mp4'.format(mark, files_list.index(file_name)))
        mv_file(file_path, new_file_path)


if __name__ == '__main__':
    logger.info('app start')
    tag_video()
    logger.info('app stop')