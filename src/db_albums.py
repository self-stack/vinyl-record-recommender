import mongo
import pickle
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

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


def main():
    '''main function of script'''

    client_id, client_secret, _ = get_keys()
    mongo.connect_mongo()
    mongo.connect_coll('vinyl_recc', 'api_albums')
       
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                                  client_secret=client_secret))

    album_ids = pickle.load(open('../data/MASTER_ALBUM_IDS.pkl', 'rb'))
    for _id in album_ids:
        api_album = sp.album(_id)
        mongo.insert_one(api_album)

    mongo.close_mongo()



if __name__ == '__main__':
    main()