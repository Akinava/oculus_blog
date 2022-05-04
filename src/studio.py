from os.path import join
import requests
from time import sleep
from utility import get_files_list
from youtube_api import post_video as youtube_post_video
from settings import (
    logger,
    DIR_VIDEO_OUTPUT,
    FORISMATIC_API_URL,
    FORISMATIC_API_DELAY,
)


def post_video(project_dir):
    logger.info('post video')

    youtube_post_video('../Video_test/output/2022.05.21 12:00.mp4')
    exit()

    output_video_dir = join(project_dir, DIR_VIDEO_OUTPUT)
    video_files_list = get_files_list(output_video_dir)
    for f_name in video_files_list:
        output_video_file_path = get_output_video_file_path(project_dir, f_name)
        print(output_video_file_path)


def get_output_video_file_path(project_dir, f_name):
    return join(project_dir, DIR_VIDEO_OUTPUT, f_name)


def get_title():
    title = ''
    while len(title) < 1 or len(title) > 100:
        try:
            title = requests.get(FORISMATIC_API_URL).json()['quoteText']
        except:
            logger.warning('fail to get title')

        if len(title) > 100:
            sleep(FORISMATIC_API_DELAY)

    return title
