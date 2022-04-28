from settings import logger
from utility import get_project_dir
from video_editor import cat_video


def main():
    logger.info('main')
    project_dir = get_project_dir()
    cat_video(project_dir)


if __name__ == '__main__':
    logger.info('app start')
    main()
    logger.info('app stop')
