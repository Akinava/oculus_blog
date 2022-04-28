import sys


def get_project_dir():
    from settings import logger
    if len(sys.argv) < 2:
        logger.error('project dir required, run app: "{} poject_dir"'.format(sys.argv[0]))
        exit(1)
    return sys.argv[1]


def setup_logger():
    import logging
    import settings
    settings.logger = logging.getLogger(__name__)
    settings.logger.setLevel(settings.logging_level)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(settings.logging_format)
    handler.setFormatter(formatter)
    settings.logger.addHandler(handler)