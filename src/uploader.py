from os.path import join, exists
import requests
from time import sleep, time
import pickle

from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import settings
from settings import (
    logger,
    DIR_VIDEO_OUTPUT,
    FORISMATIC_API_URL,
    FORISMATIC_API_DELAY,
    VIDEO_POST_MAX,
    VIDEO_EXT,
    VIDEO_REQUEST_BODY_KEY,
    VIDEO_PUBLISH_AT_PLACE,
    VIDEO_TITLE_PLACE,
    CLIENT_SECRET_FILE,
    YOUTUBE_API_SCOPES,
    YOUTUBE_API_VERSION,
    YOUTUBE_API_SERVICE,
    TOKEN_FILE,
)
from utility import (
    get_files_list,
    get_project_dir,
    str_to_date_time,
    read_video_data,
)


def get_pickle_file_path():
    return join(settings.project_dir, TOKEN_FILE)


def get_client_secret_file_path():
    return join(settings.project_dir, CLIENT_SECRET_FILE)


def load_cred():
    if not exists(get_pickle_file_path()):
        return None
    with open(get_pickle_file_path(), 'rb') as f:
        return pickle.load(f)


def save_cred(cred):
    with open(get_pickle_file_path(), 'wb') as f:
      pickle.dump(cred, f)


def update_cred(cred):
    if cred and cred.expired and cred.refresh_token:
      cred.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          get_client_secret_file_path(),
          YOUTUBE_API_SCOPES)
      cred = flow.run_local_server()
    return cred


def get_cred():
    cred = load_cred()
    if not cred or not cred.valid:
        cred = update_cred(cred)
        save_cred(cred)
    return cred


def create_service():
    cred = get_cred()
    try:
        service = build(YOUTUBE_API_SERVICE, YOUTUBE_API_VERSION, credentials=cred)
        logger.info('service created successfully')
        return service
    except Exception as e:
        logger.info('Unable to connect.')
        print(e)
        return None


def service_upload(output_video_file_path, request_body):
    service = create_service()
    media_file = MediaFileUpload(output_video_file_path)
    t = time()
    logger.info('start upload file :{}'.format(output_video_file_path))
    print(output_video_file_path, request_body)

    # response_upload = service.videos().insert(
    #     part='snippet,status',
    #     body=request_body,
    #     media_body=media_file
    # ).execute()
    # logger.info('completed in {} sec'.format(time() - t))
    # print(response_upload)

    # TODO move file


def post_video():
    logger.info('post video')
    video_files_list = get_video_files_list()
    for f_name in video_files_list:
        output_video_file_path = get_output_video_file_path(f_name)
        request_body = get_request_body(f_name)
        service_upload(output_video_file_path, request_body)


def get_request_body(f_name):
    request_body = read_video_data()[VIDEO_REQUEST_BODY_KEY]
    set_request_body_item(request_body, VIDEO_PUBLISH_AT_PLACE, get_publish_at_date_time(f_name))
    set_request_body_item(request_body, VIDEO_TITLE_PLACE, get_title())
    return request_body


def set_request_body_item(body_dict, place, value):
    last_key = place.pop()
    for key in place:
        body_dict = body_dict[key]
    body_dict[last_key] = value


def get_publish_at_date_time(f_name):
    date_time_str = f_name.replace(VIDEO_EXT, '').rstrip('.')
    return str_to_date_time(date_time_str).isoformat() + '.000Z'

def get_video_files_list():
    output_video_dir = get_output_video_dir()
    video_files_list = get_files_list(output_video_dir)
    sort_video_files_list(video_files_list)
    return get_video_files_max(video_files_list)


def get_video_files_max(video_files_list):
    return video_files_list[0: VIDEO_POST_MAX]


def sort_video_files_list(video_files_list):
    video_files_list.sort()


def get_output_video_dir():
    return join(settings.project_dir, DIR_VIDEO_OUTPUT)


def get_output_video_file_path(f_name):
    return join(settings.project_dir, DIR_VIDEO_OUTPUT, f_name)


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


if __name__ == '__main__':
    logger.info('app start')
    settings.project_dir = get_project_dir()
    post_video()
    logger.info('app stop')