import os
import logging
from dotenv import load_dotenv

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import YouTube
from pytube import Search


load_dotenv()

def download(url) -> str:
    """
    Downloads YouTube video and returns file path for mp3.
    """
    try:
        if is_yt_url(url): # check to see if user input from play command is a youtube url
            yt = YouTube(url)
        elif is_spotify_url(url):
            search_terms = get_search_terms(url)
            yt = Search(search_terms).results[0]
        else:
            yt = Search(url).results[0] # first result of search query

        # attempt age bypass
        # yt.bypass_age_gate()

        audio_stream = yt.streams.filter(only_audio=True).first()
        output_path = os.path.join(os.path.dirname(__file__), 'downloads')

        return audio_stream.download(output_path=output_path)
    except Exception as ex:
        logging.error(str(ex))


def get_song_info(url, request_author) -> dict:
    """
    Extracts YouTube video info from submitted url.
    """
    try:
        if is_yt_url(url): # check to see if user input from play command is a youtube url
            yt = YouTube(url)
        elif is_spotify_url(url):
            search_terms = get_search_terms(url)
            yt = Search(search_terms).results[0]
        else:
            yt = Search(url).results[0] # first result of search query

        return {
            'song_name': yt.title, 
            'song_duration': format_time(yt.length), 
            'request_author': request_author, 
            'thumbnail_url': yt.thumbnail_url,
            'url': url
        }
    except Exception as ex:
        logging.error(str(ex))


def format_time(seconds):
    '''Formats total seconds to %M:%S format.'''
    minutes, seconds = divmod(seconds, 60)
    return f'{minutes}:{seconds:02d}'


def delete(file_path):
    '''Deletes audio file from downloads directory.'''
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f'Succesfully deleted {file_path}')
        except OSError as error:
            print(f'Error deleting file: {error}')
    else:
        print('The file path does not exist.')
        print(file_path)


def is_yt_url(user_input: str) -> bool:
    '''Checks if input string is a YouTube url.'''
    if 'https://www.youtube.com/' in user_input:
        return True
    return False


def is_spotify_url(user_input: str) -> bool:
    """
    Checks if input string is a spotify url.
    """
    if 'open.spotify.com/track/' in user_input:
        return True
    return False


def get_search_terms(url: str) -> str:
    """
    Extracts artist and song name from spotify url.
    """
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    track = sp.track(url)
    logging.info('Converting spotify url %s to [%s %s]', url, track['name'], track['artists'][0]['name'])
    return f"{track['name']} {track['artists'][0]['name']}"
