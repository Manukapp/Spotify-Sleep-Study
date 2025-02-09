# Spotify Sleep Study - Research Tool

This repository contains Python scripts developed for a PhD research study at the **Cambridge Institute for Music Therapy Research, UK**. The study investigates the relationship between musical structure and sleep quality in dementia caregivers.

## Features:
- Extracts **Spotify track metadata** (danceability, energy, tempo, etc.) using the API.
- Organizes data into **CSV files** for statistical analysis.
- Used strictly for **academic research** (not a commercial application).

## Data Compliance:
- No **personal user data** is collected or stored.
- The API is used **solely for analyzing track features**.
- All research findings acknowledge **Spotify's data contribution**.

## How It Works:
1. Run `Music_Features_in_a_Sp_Playlist.py` to fetch track features from a Spotify playlist.
2. Saves into a "(features).csv" [change name to your playlist] 
3. Run `Classify_Spotify_Tracks_16_01_v.py` to organises the songs of the playlist in the order of total danceability, valence, energy (arousal), Tempo, Loudness,	Speechiness	& Track Popularity.
4. Statistical analysis is then performed using Python and SPSS.

## Contact:
- **Researcher:** Leonardo Muller-Rodriguez
- **Institution:** Cambridge Institute for Music Therapy Research
- **Profile:** [https://www.aru.ac.uk/people/leonardo-muller](https://www.aru.ac.uk/people/leonardo-muller)

