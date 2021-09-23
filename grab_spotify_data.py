import os
import csv
import spotipy
import spotipy.util as util
import pandas as pd
import pickle
from spotipy.oauth2 import SpotifyOAuth

class GrabSpotInfo():
    def get_data(self):
        spotify = self.spot
        songs = self.all_songs
        dataset = []

         # Accepts spotify object and playlist, and fetches relevant features (returns list of feature sets)
        for track in songs['tracks']['items']:

            # Get audio data from Spotify based on ID
            aud_feat = spotify.audio_features(track['track']['id'])[0]
            dataset.append([track['track']['id'],aud_feat['energy'],aud_feat['liveness'],aud_feat['tempo'],
                            aud_feat['speechiness'],aud_feat['acousticness'],aud_feat['instrumentalness'],
                            aud_feat['time_signature'],aud_feat['danceability'],aud_feat['key'],
                            aud_feat['duration_ms'],aud_feat['loudness'],aud_feat['valence'],aud_feat['mode']])

        return dataset

    def __init__(self, spot, songs):
        self.spot = spot
        self.all_songs = songs
