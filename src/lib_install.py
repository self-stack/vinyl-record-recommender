import sys
import subprocess

#TODO: add pip3 install
# add pandas
# add pymongo
# add tqdm
subprocess.check_call([sys.executable, '-m', 'pip3', 'spotipy'])
subprocess.check_call([sys.executable, '-m', 'pip3', 'lyricsgenius'])
#subprocess.check_call([sys.executable, '-m', 'pip3', 'textblod
subprocess.check_call([sys.executable, '-m', 'pip3', 'essential-generators'])
#pip3 install pyLDAvis
