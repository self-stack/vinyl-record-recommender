import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from random import choice
import pickle
import pandas as pd
from collections import defaultdict
import lyricsgenius


def get_keys():
    f = open('api_keys.txt', 'r')
    API_KEYS = f.readlines()

    for idx, key in enumerate(API_KEYS):
        API_KEYS[idx] = key.replace('\n', '')

    return API_KEYS

def get_random_query():
    '''
    Random choice from alphabet.

    Parameters
    ----------
    None:

    Returns
    ----------
    Wildcard for query : (string)
        Return random alphabet character and % (<char>%) from spotipy query.
    '''
    chars = 'abcdefghijklmnopqrstuvwxyz'
    return choice(list(chars)) + '%'

def get_all_album_ids(album_query, sp):
    album_info = album_query['albums']['items']
    album_ids = []
    page_cnt = 50

    for page in range(page_cnt):
        for n in range(len(album_info)):
            album_ids.append(album_info[n]['id'])
        album_info = sp.next(album_query['albums'])['albums']['items']

    return album_ids

def album_builder(unique_albums, sp):
    dfs_lst = []
    audio_feat_lst = ['song_id', 'danceability', 'energy', 'key', 'loudness',
    'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness',
    'valence', 'tempo', 'duration_ms', 'time_signature']

    for album_id in unique_albums:
        album_dict = defaultdict(list)
        audio_feat = defaultdict(dict)
        tracks = sp.album_tracks(album_id)
        album_name = sp.album(album_id)['name']

        for track in pd.Series(tracks['items']):
            album_dict['album'].append(album_name)
            album_dict['album_id'].append(album_id)
            artist_lst = []
            for artist in track['artists']:
                artist_lst.append(artist['name'])

            album_dict['artist'].append(artist_lst)
            album_dict['artist_id'].append(track['artists'][0]['id'])
            album_dict['song'].append(track['name'])
            album_dict['song_id'].append(track['id'])
            audio_feat[track['id']] = sp.audio_features(track['id'])[0]

        feat_df = pd.DataFrame.from_dict(audio_feat, orient='index')
        feat_df.reset_index(inplace=True)
        feat_df.rename(columns={'index':'song_id'}, inplace=True)
        feat_df = feat_df[audio_feat_lst]
        album_df = pd.DataFrame.from_dict(album_dict)
        full_album_df = album_df.merge(feat_df, on='song_id')

        dfs_lst.append(full_album_df)
        del album_df
        del album_dict
        del audio_feat

    return dfs_lst

def get_lyrics(song, artist):
    song = genius.search_song(song, artist)
    return song.lyrics

def get_full_lyrics(dfs_lst):
    for album in dfs_lst:
        lyrics_lst = []
        for idx, track in album.iterrows():
            try:
                lyrics_lst.append(get_lyrics(track.song, track.artist[0]))
            except:
                print('No lyrics for this song')
                continue

        try:
            album['lyrics'] = lyrics_lst
        except:
            print('Error applying lyrics')
            continue

    return dfs_lst

def main():
    client_id, client_secret, client_access_token = get_keys()
    q_type='album'
    limit = 50

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                        client_secret=client_secret))
    genius = lyricsgenius.Genius(client_access_token)

    album_ids = []
    chars = list('abcdefghijklmnopqrstuvwxyz')

    for letter in chars:
        print('Now querying {0}%'.format(letter))
        album_query = sp.search(q=letter + '%', limit=10, type=q_type)
        album_query_id = get_all_album_ids(album_query, sp)
        album_ids.append(album_query_id)
        print('Album Count extended to: {0}'.format(len(album_ids)))

    flattened_album_ids = [id for sublist in album_ids for lst in sublist]


    unique_albums = pd.Series(flattened_album_ids).unique()
    print('UNIQUE Album Count extended to: {0}'.format(len(unique_albums)))

    final_albums_df = pd.concat(get_full_lyrics(album_builder(unique_albums, sp)))
    # pickle.dump(final_albums_df, open('final_albums_df.pkl', 'wb'))


if __name__ == '__main__':
    main()
