import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from random import choice
import pickle
import pandas as pd
from collections import defaultdict
import lyricsgenius
from essential_generators import DocumentGenerator
import re
import collections
from pymongo import MongoClient
from tqdm.notebook import tqdm


def get_keys():
    '''
    Access API keys from external file and placed in a list.

    Parameters
    ----------
    None:

    Returns
    ----------
    API_KEYS: (list)
        Return API keys used for connected to Spotify and Genius APIs.
    '''
    f = open('api_keys.txt', 'r')
    API_KEYS = f.readlines()

    for idx, key in enumerate(API_KEYS):
        API_KEYS[idx] = key.replace('\n', '')

    return API_KEYS

def get_album_ids_from_query(album_search):
    '''
    Pluck unique album IDs from API query, iterrates through paginated query,
    return list of album IDs from query.

    Parameters
    ----------
    album_query: (dict)
        Dictionary querried from Spotify API.

    Returns
    ----------
    album_ids: (list)
        Return album IDs from API query.
    '''
    album_info = album_search['albums']['items']
    album_ids = []

    for n in range(len(album_info)):
        album_ids.append(album_info[n]['id'])


    return album_ids

def get_rand_offset():
    '''
    Return random number between 1 to 10 for selection pages in paginated pulls
    from Spotify API.

    Parameters
    ----------
    None:

    Returns
    ----------
    choice(range(10)): (int)
        Random int between 1 and 10.
    '''
    return choice(range(10))

def get_rand_word(gen):
    '''
    Return random generated word from essential_generators randomizer.

    Parameters
    ----------
    gen: (DocumentGenerator)
        essential_generators object to pull random word for API search.

    Returns
    ----------
    gen.word(): (str)
        Random word generated from essential_generators class.
    '''
    return gen.word()

def album_builder_test(album):
    '''
    Album dictionary pulled from Spotify API.

    Parameters
    ----------
    album: (dictionary)
        Album dictionary pulled from Spotify API.

    Returns
    ----------
    album_dict: (dictionary)
        Random word generated from essential_generators class.
    tracks: (list)
        List of track names from album dictionary for Genius API pull for album
        lyrics.
    track_ids: (list)
        List of track IDs specified by Spotify for audio feature API pull.
    '''
    album_dict = defaultdict(list)

    album_dict['artist'].append(album['artists'][0]['name'])
    album_dict['artist_id'].append(album['artists'][0]['id'])
    album_dict['album'].append(album['name'])
    album_dict['album_type'].append(album['album_type'])
    album_dict['album_id'].append(album['id'])
    album_dict['album_label'].append(album['label'])
    if album['external_ids']:
        album_dict['upc_code'].append(album['external_ids']['upc'])
    else:
        pass
#     album_dict['upc_code'].append(album['external_ids']['upc'])
    album_dict['album_popularity'].append(album['popularity'])
    album_dict['release_date'].append(album['release_date'])
    album_dict['release_prec'].append(album['release_date_precision'])
    album_dict['genres'].append(album['genres'])
    album_dict['album_release'].append(album['name'] + ' by ' + album['artists'][0]['name'])

    tracks, track_ids = [], []
    for track in album['tracks']['items']:
        tracks.append(track['name'])
        track_ids.append(track['id'])


    return album_dict, tracks, track_ids

def decode_lyrics(s):
    '''
    Clean and decode HTML from lyrics.

    Parameters
    ----------
    s: (str)
        Album lyrics collected from Genius API.

    Returns
    ----------
    s: (str)
        Cleaned lyrics from Genius API.
    '''
    s = s.encode('ascii', 'ignore')
    s = s.decode()
    s = s.replace('\n', ' ')
    s = s.replace('-', ' ')
    s = re.sub(r'[\[].*?[\)\]]', ' ', s)

    return s

def lyrics_builder(song_names, artist, album_id, genius):
    '''
    Build lyrics dictionary for mongodb.

    Parameters
    ----------
    song_names: (list)
        List of track names from album dictionary for Genius API pull for album
        lyrics.
    artist: (str)
        Name of artist for Genius API pull.
    album_id: (str)
        Unique album ID specified by Spotify for mongodb, contactication of df
        in the future.
    genius: (lyricsgenius)
        Lyricsgenius class for accessing album lyrics.

    Returns
    ----------
    lyrics_dict: (dictionary)
        Album lyrics dictionary for mongodb.
    '''
    lyrics_dict = defaultdict(list)

    lyrics_dict['album_id'] = album_id
    album_lyrics = ''
    for song in song_names:
        if song == None or artist == None:
            continue

        song_search = genius.search_song(song, artist)

        if song_search != None:
            album_lyrics += song_search.lyrics;
        else:
            continue

    lyrics_dict['lyrics'] = decode_lyrics(album_lyrics)

    return lyrics_dict

def genres_builder(album_id, genres):
    '''
    Build genres dictionary for mongodb.

    Parameters
    ----------
    album_id: (str)
        Unique album ID specified by Spotify for mongodb, contactication of df
        in the future.
    genius: (list)
        List of genres of artist from Spotify API.

    Returns
    ----------
    genre_dict: (dictionary)
        List of album genres for mongodb.
    '''
    genre_dict = defaultdict(list)

    genre_dict['album_id'] = album_id
    genre_dict['genres'] = genres

    return genre_dict

def audio_features_builder(album_id, audio_features):
    '''
    Build audio features dictionary for mongodb.

    Parameters
    ----------
    album_id: (str)
        Unique album ID specified by Spotify for mongodb, contactication of df
        in the future.
    audio_features: (list)
        List of list of audio features for album from Spotify API.

    Returns
    ----------
    audo_feat_dict: (dictionary)
        Averaged audio features of album for mongodb.
    '''
    audio_feat_dict = defaultdict(list)
    keys_to_pop = ['type', 'id', 'uri', 'track_href', 'analysis_url']
    track_feats = ['danceability', 'energy', 'key',
                    'loudness', 'mode', 'speechiness', 'acousticness',
                   'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature']


    audio_feat_dict['album_id'] = album_id
    for track_info in audio_features:
        if track_info == None:
            continue
        [track_info.pop(key) for key in keys_to_pop]

    counter = collections.Counter()

    for d in audio_features:
        counter.update(d)

    sum_ = dict(counter)
    for k, v in sum_.items():
        audio_feat_dict[k] = v / len(audio_features)

    return audio_feat_dict

def main():
    '''
    Main function for API scrapping and loading data in mongodb.

    Parameters
    ----------
    None:

    Returns
    ----------
    None:
    '''

    client_id, client_secret, client_access_token = get_keys()
    gen = DocumentGenerator()
    q_type='album'
    limit = 50
    unique_ids = pickle.load(open('../data/MASTER_ALBUM_IDS.pkl', 'rb'))

    client = MongoClient('localhost', 27017)
    db = client['album_info']
    db['album_id_master']
    db['albums']
    db['lyrics']
    db['genres']
    db['feat_df']
    master_coll = db['album_master_id']
    album_coll = db['albums']
    lyric_coll = db['lyrics']
    genre_coll = db['genres']
    feat_coll = db['feat_df']

    for id_ in tqdm(unique_ids):
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                                  client_secret=client_secret))
        genius = lyricsgenius.Genius(client_access_token=client_access_token)
        album = sp.album(id_)
        album_dict, tracks, track_ids = album_builder_test(album)

        artist = album_dict['artist'][0]
        artist_id = album_dict['artist_id'][0]
        album_id = album_dict['album_id'][0]

        genres = sp.artist(artist_id)['genres']
        audio_features = sp.audio_features(track_ids)

        genres_dict = genres_builder(album_id, genres)
        lyrics_dict = lyrics_builder(tracks, artist, album_id, genius)
        features_dict = audio_features_builder(album_id, audio_features)

        '''dicts for mongo'''
        album_coll.insert_one(album_dict)
        lyric_coll.insert_one(lyrics_dict)
        genre_coll.insert_one(genres_dict)
        feat_coll.insert_one(features_dict)

    client.close()

if __name__ == '__main__':
    main()
