import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from random import choice
import pickle

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

def get_random_offset():
    '''
    Random choice between 0 and 2000, which is the max offset for spotify query.


    Parameters
    ----------
    None:

    Returns
    ----------
    Random number: (int)
        Random number between 0 and 2000
    '''
    return choice(range(2001), seed=101)


def main():
    q_type='album'
    client_id = '0376bfe0a68f4146ad30b7983ffcc17a'
    client_secret = '7c8c899ad6c64d93a08f5399d44e73be'
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                        client_secret=client_secret))

    album_num = 10


if __name__=="__main__":
    main()
