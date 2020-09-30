import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from random import choice
from essential_generators import DocumentGenerator
from pymongo import MongoClient

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
    f = open('../data/api_keys.txt', 'r')
    API_KEYS = f.readlines()

    for idx, key in enumerate(API_KEYS):
        API_KEYS[idx] = key.replace('\n', '')

    return API_KEYS

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

    # CONST and API instantiation
    client_id, client_secret, _ = get_keys()
    gen = DocumentGenerator()
    q_type='album'
    limit = 50

    client = MongoClient('localhost', 27017)
    db = client['raw_album_info']
    db['album_objects']
    album_coll = db['albums']

    while True:
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                          client_secret=client_secret))
        album_page_query = sp.search(q=get_rand_word(gen),
                                        limit=limit, offset=get_rand_offset(),
                                        type=q_type)

        if album_page_query == None:
            client.close()
            break

        album_coll.insert_one(album_page_query['albums'])

if __name__ == '__main__':
    main()
