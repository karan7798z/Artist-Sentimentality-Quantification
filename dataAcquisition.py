import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import lyricsgenius
import pandas as pd
import time
import requests
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer

#Setting config parameters for the API Requests

#Enter your Spotify Client ID here
CLIENT_ID = ''

#Enter your Spotify Client Secret here
CLIENT_SECRET = ''

#Enter your Genius Access Token here
GENIUS_ACCESS_TOKEN = ""

#Initializing the SID Object
sid = SentimentIntensityAnalyzer()

#Function to Fetch Artist Details
def get_artist(name):
    results = sp.search(q='artist:' + name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        return items[0]
    else:
        return None

#Function to get Lyrical Sentiment Dictionary for a track
def get_sentiment_dict(lyrics_for_score):
    num_pos = 0
    num_neg = 0
    num_neut = 0
    lines = lyrics_for_score.split('\n')
    for line in lines:
        pol = sid.polarity_scores(line)
        x = pol['compound']
        if x >= 0.5:
            num_pos += 1
        elif x > -0.5 and x < 0.5:
            num_neut += 1
        else:
            num_neg += 1
    total_num = num_pos + num_neg + num_neut
    neg_per = (num_neg / float(total_num)) * 100
    pos_per = (num_pos / float(total_num)) * 100
    neut_per = (num_neut / float(total_num)) * 100

    sentiment_dict = {"neg_per": neg_per, "pos_per": pos_per, "neut_per": neut_per}
    return sentiment_dict

#Function to fetch data for each track of an album
def fetch_album_tracks(album):
    tracks = []
    results = sp.album_tracks(album['id'])
    tracks.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    tracklist = []
    for track in tracks:
        metadata = sp.track(track['id'])
        track_features = sp.audio_features(track['id'])

        # metadata
        name = metadata['name']
        album = metadata['album']['name']
        album_uri = metadata['album']['uri']
        album_img_med = metadata['album']['images'][1]['url']
        album_img_small = metadata['album']['images'][2]['url']
        artist = metadata['album']['artists'][0]['name']
        release_date = metadata['album']['release_date']
        length = metadata['duration_ms']
        popularity = metadata['popularity']

        # Track Features
        acousticness = track_features[0]['acousticness']
        danceability = track_features[0]['danceability']
        energy = track_features[0]['energy']
        instrumentalness = track_features[0]['instrumentalness']
        liveness = track_features[0]['liveness']
        loudness = track_features[0]['loudness']
        speechiness = track_features[0]['speechiness']
        tempo = track_features[0]['tempo']
        time_signature = track_features[0]['time_signature']
        track_uri = track_features[0]['uri']
        valence = track_features[0]['valence']

        # Lyrics
        song_name_for_lyrics = re.sub(' - EP Version', '', name)

        # Fix for spotify glitch in fetching tracks of the album - In Absentia by Porcupine Tree
        if album == 'In Absentia':
            song_name_for_lyrics = re.sub(' - Remastered', '', song_name_for_lyrics)

        if artist == 'The Beatles':
            song_name_for_lyrics = re.sub(' - Remastered 2009', '', song_name_for_lyrics)

        song = genius_api.search_song(song_name_for_lyrics, artist)

        if (song == None or song_name_for_lyrics in ['Revenant - Live', 'Moon Loop (Improvisation)',
                                                     'Moon Loop (Coda)', 'And the Swallows Dance Above the Sun',
                                                     'Voyage 34 (Phase One)',
                                                     'The Sky Moves Sideways (Phase One)', 'Up the Downstair',
                                                     'Phase I', 'Phase II',
                                                     'Phase III (Astralasia Dreamstate)',
                                                     'Phase IV (A New Civilization)',
                                                     'Not Beautiful Anymore', 'Bornlivedie', 'Intermediate Jesus',
                                                     'The Sky Moves Sideways Phase 2',
                                                     'Message from a Self Destructing Turnip',
                                                     'Queen Quotes Crowley', 'And the Swallows Dance Above the Sun',
                                                     'Pepperland',
                                                     'Sea Of Monsters', 'March Of The Meanies', 'Pepperland Laid Waste',
                                                     'Yellow Submarine In Pepperland']):
            lyrics = ''
        else:
            lyrics = song.lyrics
            lyrics = re.sub(r'[\(\[].*?[\)\]]', '', lyrics)
            lyrics = re.sub('\[|\]', '', lyrics)
            lyrics = '\n'.join([s for s in lyrics.splitlines() if s])

        sentiment_dict = get_sentiment_dict(lyrics)

        neg_per = sentiment_dict['neg_per']
        pos_per = sentiment_dict['pos_per']
        neut_per = sentiment_dict['neut_per']

        track_data_soup = [name, album, album_uri, album_img_med, album_img_small, artist, release_date, lyrics, length,
                           popularity, danceability, acousticness, energy, instrumentalness, liveness, loudness,
                           speechiness, tempo, time_signature, track_uri, valence, neg_per, pos_per, neut_per]

        final_df.loc[len(final_df)] = track_data_soup
        time.sleep(1)

#Function to get data for each album of provided artists.
#Function to get data for each track of each album is called inside this.
def fetch_artist_albums(artist):
    albums = []
    results = sp.artist_albums(artist['id'], album_type='album')
    albums.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        albums.extend(results['items'])
    print('Total albums: %s', len(albums))

    unique = set()  # skip duplicate albums
    tracks = []
    
    #If any albums are to be ignored, add those in this list
    albums_to_ignore = ['Where the Light Is: John Mayer Live In Los Angeles', 'As/Is',
                        'As/Is: Cleveland/Cincinnati, OH - 8/03-8/04/04', 'As/Is: Houston, TX - 7/24/04',
                        'As/Is: Philadelphia, PA/Hartford, CT - 8/14-8/15/04',
                        'As/Is: Mountain View, CA - 7/16/04', 'Any Given Thursday', 'Octane Twisted (Live)',
                        'OK Computer OKNOTOK 1997 2017', 'TKOL RMX 1234567', 'I Might Be Wrong',
                        'In Absentia (Remastered)', 'Octane Twisted', 'Anesthetize', 'Arriving Somewhere',
                        'Stars Die (Remastered)', 'Voyage 34 (Remastered)', 'Metanoia (Remastered)',
                        'Coma Divine (Remastered)', 'Signify (Remastered)', 'Staircase Infinities (Remastered)',
                        'Up the Downstair (Remastered)', 'On the Sunday of Life (Remastered)',
                        'The Sky Moves Sideways (Remastered)', 'Abbey Road (Super Deluxe Edition)', 'The Beatles',
                        'Live At The Hollywood Bowl',
                        'Let It Be... Naked (Remastered)', 'Yellow Submarine Songtrack',
                        'On Air - Live At The BBC (Vol.2)', '1 (Remastered)', 'Live At The BBC (Remastered)',
                        "Sgt. Pepper's Lonely Hearts Club Band (Deluxe Edition)",
                        "Sgt. Pepper's Lonely Hearts Club Band (Super Deluxe Edition)",
                        "Yellow Submarine (Remastered)", "Magical Mystery Tour (Remastered)", "In Rainbows (Disk 2)"]

    for album in albums:
        name = album['name'].lower()
        if name not in unique:
            if (('Remix' not in album['name']) and (album['name'] not in albums_to_ignore)):
                unique.add(name)
                fetch_album_tracks(album)
                time.sleep(7)

def main():

	#Enter names of your favorite acts/artists here
    my_favourite_artists_list = ['Radiohead', 'The Beatles', 'Porcupine Tree', 'John Mayer', 'Pink Floyd']
    
    for favourite_artist in my_favourite_artists_list:
        artist = get_artist(favourite_artist)
        fetch_artist_albums(artist)
        time.sleep(7)


if __name__ == '__main__':
    client_credentials_manager = SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    genius_api = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN, verbose=False)
    start_time = time.time()
    final_df = pd.DataFrame(
        columns=['name', 'album', 'album_uri', 'album_img_med', 'album_img_small', 'artist', 'release_date', 'lyrics',
                 'length', 'popularity', 'danceability', 'acousticness', 'energy', 'instrumentalness', 'liveness',
                 'loudness', 'speechiness', 'tempo', 'time_signature', 'track_uri', 'valence', 'neg_per', 'pos_per',
                 'neut_per'])
    main()

    # Removing a track by John Mayer with 0 valence as per Spotify, since I have some doubts about the 0 valence measure for the track (It absolutely doesn't sound that negative!).
    final_df.drop(final_df[final_df['name'] == 'On The Way Home'].index, inplace=True)

    # Counting number of words in the lyrics of each track
    final_df['word_count'] = [len(lyrics.replace('\n', ' ').split(' ')) for lyrics in final_df['lyrics']]


    final_df.to_excel("track_data.xlsx", index=False)

    print("--- %s seconds ---" % (time.time() - start_time))
