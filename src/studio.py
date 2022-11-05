import os
import pickle
import requests
import json
import random
from time import sleep
from os.path import join
from google.auth.exceptions import RefreshError
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
    get_mark,
    get_marks,
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
    if credentials and credentials.expired and credentials.refresh_token:
        try:
            credentials.refresh(Request())
        except RefreshError:
            logger.warning('Token has been expired or revoked.')
            return make_credentials()
    return credentials


def make_credentials():
    scopes = [
        "https://www.googleapis.com/auth/youtube.readonly",
        "https://www.googleapis.com/auth/youtube",
        "https://www.googleapis.com/auth/youtube.force-ssl"]
    flow = InstalledAppFlow.from_client_secrets_file(
        get_client_secrets_file(),
        scopes)
    credentials = flow.run_local_server(port=0)
    return credentials


def get_credentials():
    credentials = load_credentials()

    if credentials is None:
        credentials = make_credentials()

    else:
        if credentials.valid:
            return credentials

        if credentials.expired and credentials.refresh_token:
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


def title_has_marks(marks, vid):
    for mark in marks:
        if mark in vid['snippet']['title']:
            return True
    return False


def filter_scheduled(videos):
    unscheduled_video = []
    marks = get_marks()
    for vid in videos:
        if title_has_marks(marks, vid):
            unscheduled_video.append(vid)
    return unscheduled_video


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
            title = requests.get(FORISMATIC_API_URL.format(language)).json()['quoteText'].strip()
        except (json.decoder.JSONDecodeError, ) as e:
            logger.warning('fail to get title, exception {}'.format(e))
        if len(title) > 100:
            continue
        sleep(FORISMATIC_API_DELAY)
    return title


def get_video_id(video_body):
    return video_body['contentDetails']['videoId']


def get_video_title(video_body):
    return video_body['snippet']['title']


def add_emoji(snippet_title, video_title):
    metadata = get_metadata(video_title)
    emoji_list = metadata['emoji']
    if len(emoji_list) == 1:
        emoji = emoji_list[0]
    else:
        emoji = random.choice(emoji_list)
    if len(emoji + ' ' + snippet_title) > 100:
        return snippet_title
    return emoji + ' ' + snippet_title


def get_metadata(video_title):
    mark = get_mark(video_title)
    return read_metadata()['marks'][mark]


def get_language(metadata):
    return metadata['video_body']['snippet']['defaultAudioLanguage']


def get_playlist_id(video_title):
    metadata = get_metadata(video_title)
    return metadata['playlistId']


def get_publish_at(video_title):
    mark = get_mark(video_title)
    date_time_str = video_title.replace(mark, '').strip()
    s = list(date_time_str)
    s[4], s[7], s[10], s[13] = '-', '-', 'T', ':'
    return ''.join(s) + ':00+02:00'


def make_video_body(video_id, video_title):
    metadata = get_metadata(video_title)
    language = get_language(metadata)
    snippet_title = get_title(language)
    snippet_title = add_emoji(snippet_title, video_title)
    video_body = metadata['video_body']
    video_body['id'] = video_id
    video_body['snippet']['title'] = snippet_title
    video_body['status']['publishAt'] = get_publish_at(video_title)
    return video_body


def get_video_log_line(orig_video_body):
    video_id = get_video_id(orig_video_body)
    video_title = get_video_title(orig_video_body)
    return 'https://studio.youtube.com/video/{}/edit {}'.format(video_id, video_title)


def post_video(video_id, video_title):
    video_body = make_video_body(video_id, video_title)
    playlist_id = get_playlist_id(video_title)
    print(playlist_id, video_body)
    update_video(video_body)
    insert_video_to_playlist(video_id, playlist_id)


if __name__ == '__main__':
    all_videos = get_all_videos()
    all_private_videos = filter_private(all_videos)
    videos = filter_scheduled(all_private_videos)

    for video_body in videos:
        video_id = get_video_id(video_body)
        video_title = get_video_title(video_body)
        logger.info('{}-{} https://studio.youtube.com/video/{}/edit {}'.format(
            len(videos),
            videos.index(video_body)+1,
            video_id,
            video_title))
        post_video(video_id, video_title)
