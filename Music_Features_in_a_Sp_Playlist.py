import requests
import base64
import json
import csv
import time
#from ComposerCareers import search_artist


# Set your client ID and client secret. This one is for Mindfulness Children study
client_id = 'f8e4f0d0d1af4c51aefbd601b6aa6a22'
client_secret = 'd4037f119c2d430c859e4eafcd2c791f'
"""
## This one is for sleep study number 1
client_id = "005e95613d414453a6cd102c34ed309d"
client_secret = "4ae913a8bd3644c1b1a211c9f935ff0c"

## This one is for sleep study number 2
client_id = "21b88f60cf4547e7ae6a22d268c28dea"
client_secret = "ee069919c0c14f468def1773424bc9b6"
"""
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
playlist_id = "34snmvef9WlaERnCTzpHsc" # Giampaolo's Anaesthetist Playlist - during surgery
#playlist_id = "4LTUm9lBLuxS2sWvj2seWG" # High Energy Manukapp Songs
#playlist_id = "3PEUTb9dGCOT9Uwq0bDs0r" # Top 40 Max Martin hits - does not work?
#playlist_id = "37i9dQZF1EFCXQeQGoO7Oj" # Written by Max Martin - Number 1 producer by Billboard.com
#playlist_id = "37i9dQZF1DX8SfyqmSFDwe" # Old School Reggaeton - ~4M followers, by Spotify
#playlist_id = "7DdWVKKeJJokKU8nIs3B9D" # Musica de Cuna de Luna cresciente - Aurora Cuna
#playlist_id = "37i9dQZF1DWY7IeIP1cdjF" # Baila Reggaeton - ~11M followers by Spotify
#playlist_id = "37i9dQZF1DX76Wlfdnj7AP" # Beast Mode Spotify Playlist - ~11M followers to 'GET YOUR BEAST MODE ON'  
#playlist_id = "4bWVVkRuk2tsbQPTdUjHN0" #Luna Creciente de cuna - Children's Sleep Music with >100M listens
#playlist_id = "3n2bodrPmMDqDHgGahPoSy" #Theta Sleep Playlist - Binaural beat soundtracks
#playlist_id = "59cND945NisAIf4O1LJuVx" #Soundtrack to Sleep Playlist - Film & video game low arousal music
#playlist_id = "1Mi0LJZyy1Y3da8OiBrpN5" #DREAM REM playlist - anecdotally most effective sleep music
#playlist_id = '2PPLv2Mf7dzFTzKeJLlqDo' # Probably the kid's fav music playlist
#playlist_id = "12AI2xZxmkSyTIUlA0EQQ5" # Comedy by Rowan Atkinson, and John Cleese & crew
#playlist_id = "6dvpf9MiBzlMbvMwzN7iA6"
#playlist_id = "37i9dQZF1DWZd79rJ6a7lp" #Official Sleep Spotify playlist
#playlist_id = "37i9dQZF1DXdzGIPNRTvyN" #Official Natural sleep music Spotify playlist
#playlist_id = "37i9dQZF1DXa1rZf8gLhyz" #Official Jazz Sleep Playlist
#playlist_id = "37i9dQZF1DXbcPC6Vvqudd" #Official Night Rain playlist
#playlist_id = "37i9dQZF1DWYcDQ1hSjOpY" #Official Deep Sleep Playlist
#playlist_id = "37i9dQZF1DXbADqT0j1Cxt" #Official Lullabies for babies playlist
#playlist_id = "37i9dQZF1DX8Sz1gsYZdwj" #Official Classical music for sleep playlist
#playlist_id = "1aQsmaWYuWYs1SX5E0kp3A" #groupe musique

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

output_file_path = "C:\\Users\\leomu\\OneDrive\\Desktop\\PhD\\Music Data\\Sleep Spotify\\giampaolo_playlist_spotify.csv"
export_csv(track_info, output_file_path)

"""
# Convert track_info keys (track names) to a sorted list
track_names = sorted(list(track_info.keys()))

# Get the first track's name
first_track_name = track_names[0]

# Get the first track's data
first_track_data = track_info[first_track_name]

# Extract the first key and its value in the Features of the first track
first_feature_key = list(first_track_data['Features'].keys())[0]
first_feature_value = first_track_data['Features'][first_feature_key]

# Extract the first section
first_section = first_track_data['Sections'][0]

# Extract the first key and its value from the first section
first_section_key = list(first_section.keys())[0]
first_section_value = first_section[first_section_key]

print(f"First Track: {first_track_name}")
print(f"First Feature of Track: {first_feature_key} = {first_feature_value}")
print(f"First Feature of First Section: {first_section_key} = {first_section_value}")
"""
