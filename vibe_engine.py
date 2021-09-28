import os
import sys
import csv
import spotipy
import spotipy.util as util
import pandas as pd
import numpy as np
import pickle
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, jsonify, request
from sklearn.preprocessing import StandardScaler, LabelEncoder
from ibm_watson import ToneAnalyzerV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from dotenv import load_dotenv
import grab_spotify_data as gr
from dotenv import dotenv_values
from waitress import serve
from flask_json import FlaskJSON, as_json_p
config = dotenv_values(".env")


#os.environ["CLIENT_ID"] = config['CLIENT_ID']
#os.environ["CLIENT_SECRET"] = config['CLIENT_SECRET']
#os.environ["REDIRECT_URI"] = config['REDIRECT']

app = Flask(__name__)

# load .env file
load_dotenv()

def pstdout(*a):
    print(*a, file=sys.stdout)

## TODO: Also pass auth token here, for use when queing songs in 'add_to_queue'
@app.route('/getfilter/', methods=['GET'])
def get_playlist(varargs=None):
    # grab playlist ID, mood and access token from request

    playlist_id = request.args.get('playlist_id')
    mood = request.args.get('mood')
    acc_token = request.args.get('acc')

    app.logger.info("Access: " + acc_token)

    scope = "playlist-modify-public user-read-currently-playing"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    sp = spotipy.Spotify(auth=acc_token)
    songs = sp.playlist(playlist_id)
    #songs = sp.playlist("37i9dQZF1DZ06evO0N5yhI")
    #rf_model = pickle.load(open('model_export.sav','rb'))
    xg_model = pickle.load(open('xgboost_model.sav','rb'))
    # Pass songs and sp to GrabSpotInfo object
    raw_dataset = gr.GrabSpotInfo(sp, songs)
    raw_dataset = raw_dataset.get_data()
    # Convert raw_dataset into dataframe
    X_raw = pd.DataFrame(raw_dataset)

    # Scale values
    sc = StandardScaler()
    X = X_raw.iloc[:,1:].values
    X = sc.fit_transform(X)

    # Load encoder from file
    encoder = pickle.load(open('mood_encoder.sav','rb'))
    y_pred = xg_model.predict(X)
    results = encoder.inverse_transform(y_pred)

    # Now have mood predictions for each song on user's playli st (in english)

    merge = []
    for i, track in enumerate(raw_dataset):
        row = []
        for item in track:
            row.append(item)
        row.append(results[i])
        merge.append(row)

    chosen_ids = []
    
    for song in merge:
        pstdout(*song)
        if(song[-1] == mood):
            chosen_ids.append(song[0])
    #app.logger.info("Chosen ids:",chosen_ids[0], "Length:",len(chosen_ids))

    # Queue songs to currently playing device
    for track in chosen_ids:
        #pstdout(*track)
        sp.add_to_queue(track)
    t = sp.tracks(chosen_ids)['tracks']
    track_info = []
    #pstdout("result:",*t)
    for song in t:
        track_info.append([song['album']['images'][0]['url'],song['artists'][0]['name'],song['name']])
    current = sp.currently_playing()
    current = current['item']
    track_info.insert(0, [current['album']['images'][0]['url'],current['artists'][0]['name'],current['name']])
    # Returns array of songs (IDs) that fit the user's desired mood
    return jsonify(track_info)

@app.route('/gettone/<path:sent>', methods=['GET'])
@as_json_p
def get_tone(sent=None):
    # spaces in the string are replaced with '_'
    # Tone Analyzer API

    if(sent and sent.replace('_','')):
        authenticator = IAMAuthenticator(os.environ['IBM_KEY'])
        tone_analyzer = ToneAnalyzerV3(
            version='2017-09-21',
            authenticator=authenticator
        )
        sent = sent.replace('_',' ')
        tone_analyzer.set_service_url(os.environ['SERVICE_URL'])
        tone_analysis = tone_analyzer.tone(
            {'text': sent },
            content_type='application/json'
        ).get_result()

        return jsonify(derive_mood(tone_analysis['document_tone']['tones']))
    else:
        return None

# accepts ['tone_a','tone_b'] or ['one_tone']
def derive_mood(tones):
    vals = ['Anger', 'Fear', 'Joy', 'Sadness', 'Analytical', 'Confident', 'Tentative']
    sc = []
    to = []
    for k in tones:
        sc.append(k['score'])
        to.append(k['tone_name'])
    
    sc_len = len(sc)

    if(sc_len < 1):
        return 'no_tone'
    elif(sc_len > 1):
        to = to[-2:]

    if(sc_len > 1):
        if(vals[6] in to):
            return 'Easygoing'
        if(vals[0] in to and vals[3] in to):
            return 'Sad'
        if(vals[0] in to):
            return 'Aggressive'
        if(vals[1] in to and vals[2] in to):
            return 'Energetic'
        if(vals[1] in to and vals[3] in to):
            return 'Sad'
        if(vals[1] in to and vals[4] in to):
            return 'Sad'
        if(vals[1] in to and vals[5] in to):
            return 'Aggressive'
        if(vals[2] in to and vals[4] in to):
            return 'Energetic'
        if(vals[2] in to and vals[5] in to):
            return 'Energetic'
        if(vals[3] in to):
            return 'Sad'
        if(vals[4] in to and vals[5] in to):
            return 'Energetic'
        else:
            return 'Easygoing'
    else:
        if(to[0] == vals[0]):
            return 'Aggressive'
        if(to[0] == vals[1]):
            return 'Sad'
        if(to[0] == vals[2]):
            return 'Energetic'
        if(to[0] == vals[3]):
            return 'Sad'
        if(to[0] == vals[4]):
            return 'Easygoing'
        if(to[0] == vals[5]):
            return 'Energetic'
        if(to[0] == vals[6]):
            return 'Easygoing'
        return 'Other'

if __name__ == '__main__':
    #app.run(debug=True)
    serve(app, host='0.0.0.0', port=os.environ["PORT"], url_scheme='https')
