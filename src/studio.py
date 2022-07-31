import os
import pickle
import requests
import json
from time import sleep
from os.path import join
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import settings
from settings import (
    logger,
    FORISMATIC_API_URL,
    FORISMATIC_API_DELAY,
)
from utility import (
    read_metadata,
    save_metadata,
)


def get_client_secrets_file():
    return join(settings.project_dir, settings.CLIENT_SECRET_FILE)


def get_credentials_pickle_file():
    return join(settings.project_dir, settings.CREDENTIALS_PICKLE_FILE)


def load_credentials():
    if not os.path.exists(get_credentials_pickle_file()):
        return None
    with open(get_credentials_pickle_file(), 'rb') as f:
        return pickle.load(f)


def save_credentials(credentials):
    with open(get_credentials_pickle_file(), 'wb') as f:
      pickle.dump(credentials, f)


def update_credentials(credentials):
    scopes = [
        "https://www.googleapis.com/auth/youtube.readonly",
        "https://www.googleapis.com/auth/youtube",
        "https://www.googleapis.com/auth/youtube.force-ssl"]
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            get_client_secrets_file(),
            scopes)
        credentials = flow.run_local_server(port=0)
    return credentials


def get_credentials():
    credentials = load_credentials()
    if not credentials or not credentials.valid:
        credentials = update_credentials(credentials)
        save_credentials(credentials)
    return credentials


def authenticate():
    api_service_name = "youtube"
    api_version = "v3"
    credentials = get_credentials()
    return build(api_service_name, api_version, credentials=credentials)


def get_upload_playlist_id():
    metadata = read_metadata()
    upload_playlist_id = metadata.get('upload_playlist_id')
    if not upload_playlist_id is None:
        return upload_playlist_id
    upload_playlist_id = request_upload_playlist_id()
    metadata['upload_playlist_id'] = upload_playlist_id
    save_metadata(metadata)
    return upload_playlist_id


def request_upload_playlist_id():
    youtube = authenticate()
    request = youtube.channels().list(
        part="contentDetails",
        mine=True
    )
    response = request.execute()
    return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


def get_all_videos():
    youtube = authenticate()
    upload_playlist_id = get_upload_playlist_id()
    request = youtube.playlistItems().list(
            part="snippet,contentDetails,status",
            playlistId=upload_playlist_id,
            maxResults=50,
    )
    response = request.execute()

    all_videos = response["items"]
    while "nextPageToken" in response.keys():
        request = youtube.playlistItems().list(
            part="snippet,contentDetails,status",
            playlistId=upload_playlist_id,
            maxResults=50,
            pageToken=response["nextPageToken"]
        )
        response = request.execute()
        all_videos += response["items"]

    return all_videos


def filter_private(videos):
    return [vid for vid in videos if vid['status']['privacyStatus'] == 'private']


def filter_scheduled(videos):
    return [vid for vid in videos if '2022' in vid['snippet']['title']]


def insert_video_to_playlist(video_id, playlist_id):
    youtube = authenticate()
    body = {
        'snippet': {
            'playlistId': playlist_id,
            'resourceId': {
                'kind': 'youtube#video',
                'videoId': video_id,
            }
        }
    }
    response = youtube.playlistItems().insert(
        part='snippet',
        body=body,
    ).execute()
    return response


def update_video(body):
    youtube = authenticate()
    response = youtube.videos().update(
        part='snippet,status',
        body=body,
    ).execute()
    return response



def get_title(language):
    title = ''
    while len(title) < 1 or len(title) > 100:
        try:
            title = requests.get(FORISMATIC_API_URL.format(language)).json()['quoteText']
        except (json.decoder.JSONDecodeError, ) as e:
            logger.warning('fail to get title, exception {}'.format(e))
        if len(title) > 100:
            sleep(FORISMATIC_API_DELAY)
    return title


def get_video_id(video_body):
    return video_body['contentDetails']['videoId']


def get_mark_and_publish_time(video_body):
    return video_body['snippet']['title']


def find_metadata_by_mark(orig_video_body):
    mark_and_publish_time = get_mark_and_publish_time(orig_video_body)
    marks_metadata = read_metadata()['marks']
    for mark, metadata in marks_metadata.items():
        if mark in mark_and_publish_time:
            return metadata
    raise ValueError('Error: no metadata for video title {}'.format(mark_and_publish_time))


def get_language(metadata):
    return metadata['video_body']['snippet']['defaultAudioLanguage']


def get_playlist_id(metadata):
    return metadata['playlistId']


def get_publish_at(orig_video_body):
    mark_and_publish_time = get_mark_and_publish_time(orig_video_body)
    s = list(mark_and_publish_time)
    s[4] = '-'
    s[7] = '-'
    s[10] = 'T'
    s = s[:16]
    return ''.join(s) + ':00+02:00'


def make_video_body(orig_video_body, metadata):
    language = get_language(metadata)
    video_body = metadata['video_body']
    video_body['id'] = get_video_id(orig_video_body)
    video_body['snippet']['title'] = get_title(language)
    video_body['status']['publishAt'] = get_publish_at(orig_video_body)
    return video_body


def get_video_log_line(orig_video_body):
    video_id = get_video_id(orig_video_body)
    mark_and_publish_time = get_mark_and_publish_time(orig_video_body)
    return 'https://studio.youtube.com/video/{}/edit {}'.format(video_id, mark_and_publish_time)


def post_video(orig_video_body):
    metadata = find_metadata_by_mark(orig_video_body)
    video_body = make_video_body(orig_video_body, metadata)
    update_video(video_body)
    video_id = get_video_id(orig_video_body)
    playlist_id = get_playlist_id(metadata)
    insert_video_to_playlist(video_id, playlist_id)


if __name__ == '__main__':
    all_videos = get_all_videos()
    all_private_videos = filter_private(all_videos)
    videos = filter_scheduled(all_private_videos)

    # # FIXME
    # from utility import write_json, read_json
    # write_json('../tmp/all_private_videos.json', videos)
    # videos = read_json('../tmp/all_private_videos.json')

    for video in videos:
        log_line = get_video_log_line(video)
        logger.info('{}-{} {}'.format(len(videos), videos.index(video), log_line))
        post_video(video)
