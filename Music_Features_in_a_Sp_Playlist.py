import requests
import base64
import json
import csv
import time
#from ComposerCareers import search_artist


# Set your client ID and client secret. This one is for Mindfulness Children study
client_id = 'f8e4f0d0d1af4c51aefbd601b6aa6a22'
client_secret = 'd4037f119c2d430c859e4eafcd2c791f'

# Function to get access token
def get_access_token(client_id, client_secret):
    
    client_creds = f"{client_id}:{client_secret}"
    
    client_creds_b64 = base64.b64encode(client_creds.encode()).decode()
    
    token_url = 'https://accounts.spotify.com/api/token'
    token_data = {
        'grant_type': 'client_credentials'
    }
    token_headers = {
        'Authorization': f"Basic {client_creds_b64}"
    }
    
    r = requests.post(token_url, data=token_data, headers=token_headers)
    token_response_data = r.json()
    
    access_token = token_response_data['access_token']
    
    return access_token

# Function to get tracks from a playlist
def get_playlist_tracks(playlist_id, access_token):
    tracks = []
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {
        'Authorization': f"Bearer {access_token}"
    }

    while url:
        response = requests.get(url, headers=headers)
        playlist_data = response.json()
        tracks += [item['track'] for item in playlist_data['items']]
        url = playlist_data['next']
    
    return tracks

# Function to get track features and segments
def get_track_info(track_id, access_token):
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    
    # Get track details including artist name
    track_url = f"https://api.spotify.com/v1/tracks/{track_id}"
    track_response = requests.get(track_url, headers=headers)
    track_data = track_response.json()
    artist_name = track_data['artists'][0]['name'] if track_data['artists'] else "Unknown Artist"

    #get song popularity features
    song_popularity = str(track_data["popularity"]) + "%"
    print(artist_name, "made a track that is", song_popularity, "popular (based on a ratio between recent views and all time views")
    #artist_id = search_artist(artist_name, access_token)
    #Get Artist popularity
    #artist_url = f"https://api.spotify.com/v1/artists/{artist_id}"
    #artist_response = requests.get(artist_url, headers=headers)
    #artist_data = artist_response.json()
    #print(artist_data)
    #artist_popularity = artist_data["popularity"]

    # Get track features
    features_url = f"https://api.spotify.com/v1/audio-features/{track_id}"



    print(features_url)
    features_response = requests.get(features_url, headers=headers)
    print(features_response)

    # Check if the response contains 'error' key
    if 'error' in features_response.json():
        # Skip this track if there's an error
        return None, None, None

    features = features_response.json()
    print(features)
    # Get track segments (sections)
    analysis_url = f"https://api.spotify.com/v1/audio-analysis/{track_id}"
    analysis_response = requests.get(analysis_url, headers=headers)
    analysis = analysis_response.json()
    sections = analysis.get('sections', [])
    #segments = analysis.get('segments', [])
    print(sections)
    return features, sections, artist_name, song_popularity #artist_popularity #, segments #sections (as 2nd output normally)

def export_csv(track_info: dict, output_file_path: str):
    with open(output_file_path, "w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.writer(csv_file)

        # Write header
        headers = ["Track Name", "Feature", "Value", "Section Index", "Section Feature", "Section Value"]
        writer.writerow(headers)
        counter = 0
        for track_name, track_data in track_info.items():
            # Write overall track features
            for feature_key, feature_value in track_data['Features'].items():
                counter += 1
                print(counter, track_name)
                writer.writerow([track_name, feature_key, feature_value, "", "", ""])

            # Write section data
            for i, section in enumerate(track_data['Sections']):
                for section_key, section_value in section.items():
                    writer.writerow([track_name, "", "", i, section_key, section_value])
            """

            # Write segment data
            for i, segment in enumerate(track_data['Segments']):
                for segment_key, segment_value in segment.items():
                    # Ensure segment_value is a single value, not a list
                    if isinstance(segment_value, list):
                        segment_value = ', '.join(map(str, segment_value))
                    writer.writerow([track_name, "", "", i, segment_key, segment_value])
            """

# Get access token
access_token = get_access_token(client_id, client_secret)


# Replace with your playlist ID
#playlist_id = "6hL4iXbj85bsJ97olgWqgU" # RadioMe First Songs playlist for heart rate analysis
playlist_id = "37i9dQZF1DWZd79rJ6a7lp" #Official Sleep Spotify playlist
#playlist_id = "37i9dQZF1DXdzGIPNRTvyN" #Official Natural sleep music Spotify playlist
#playlist_id = "37i9dQZF1DXa1rZf8gLhyz" #Official Jazz Sleep Playlist
#playlist_id = "37i9dQZF1DXbcPC6Vvqudd" #Official Night Rain playlist
#playlist_id = "37i9dQZF1DWYcDQ1hSjOpY" #Official Deep Sleep Playlist
#playlist_id = "37i9dQZF1DXbADqT0j1Cxt" #Official Lullabies for babies playlist
#playlist_id = "37i9dQZF1DX8Sz1gsYZdwj" #Official Classical music for sleep playlist

# Get tracks from the playlist
tracks = get_playlist_tracks(playlist_id, access_token)
#print(tracks)
#print("Pausing for 5 seconds...")
#time.sleep(5)  # Pauses the program for 5 seconds
#print("Resumed execution.")

track_info = {}
print("BIG BOOTY Check")
for track in tracks:
    print("Pausing for 5 seconds...")
    time.sleep(5)  # Pauses the program for 5 seconds
    print("Resumed execution.")
    track_id = track['id']
    features, sections, artist, song_popularity = get_track_info(track_id, access_token) #sections as 2nd output normally
    if features == None:
        break
    
    print(features, artist)
    #features, segments, artist = get_track_info(track_id, access_token)
    track_info[track['name']] = {
        'Features': {
            'Artist' : artist,
            'Acousticness': features['acousticness'],
            'Danceability': features['danceability'],
            'Duration': features['duration_ms'],
            'Energy': features['energy'],
            'Instrumentalness': features['instrumentalness'],
            'Key': features['key'],
            'Liveness': features['liveness'],
            'Loudness': features['loudness'],
            'Mode': features['mode'],
            'Speechiness': features['speechiness'],
            'Tempo': features['tempo'],
            'Time Signature': features['time_signature'],
            'Valence': features['valence'],
            "Track Popularity" : song_popularity
        },
        #'Sections': sections
        #'Segments': segments
    }

#print(track_info)

output_file_path = "C:\\your\\path\\sleep_playlist_spotify.csv"
export_csv(track_info, output_file_path)
