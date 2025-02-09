import csv
import requests
from bs4 import BeautifulSoup
import re
import unicodedata
import string
from collections import OrderedDict
import chardet

def normalize_text(text):
    return unicodedata.normalize('NFC', text)

def extract_features_from_csv(csv_file_path):
    extracted_features = {}
    file_read_success = False
    
    with open(csv_file_path, 'rb') as file:
        result = chardet.detect(file.read())
        print(result)

    encodings = ['utf-8', 'latin-1', 'cp1252', 'utf-8-sig', str(result['encoding'])]  # Common encodings 
    for encoding in encodings:
        try:    
            with open(csv_file_path, 'r') as file:
                try:
                    # First try using DictReader
                    csv_reader = csv.DictReader(file)
                    for row in csv_reader:
                        track_name = row["Track Name"]
                        track_name = normalize_text(track_name) # Normalize the title of songs to avoid invalid char 
                        feature = row['Feature']
                        value = row['Value']

                        if feature in ["Artist", 'Danceability', 'Energy', 'Tempo', 'Valence', 'Speechiness']:
                            if track_name not in extracted_features:
                                extracted_features[track_name] = {}
                            extracted_features[track_name][feature] = value

                except KeyError:
                    # If KeyError, revert to using csv.reader
                    file.seek(0)  # Reset file read position to the beginning
                    csv_reader = csv.reader(file)
                    next(csv_reader)  # Skip header row
                    for row in csv_reader:
                        row[0] = normalize_text(row[0]) # Normalize the text in the problematic column (e.g., column 1)
                        # Process the row
                        track_name = row[0]  # Adjust indices based on your CSV structure
                        print(f"Extracting {track_name}")
                        feature = row[1]
                        value = row[2]


                        if feature in ["Artist", 'Danceability', 'Energy', 'Tempo', 'Valence', "Loudness", 'Speechiness', "Track Popularity"]:
                            if track_name not in extracted_features:
                                extracted_features[track_name] = {}
                            extracted_features[track_name][feature] = value


                    file_read_success = True
                    break  # If successful, exit the loop


        except UnicodeDecodeError:
            print(f"Trying different encoding: {encoding} didn't work")


    if not file_read_success:
        raise Exception("Unable to read the file with provided encodings.")

    return extracted_features

def extract_features_from_csv_complexity(csv_file_path):
    extracted_features = {}
    section_indices_count = {}
    file_read_success = False

    encodings = ['utf-8', 'latin-1', 'cp1252', 'utf-8-sig']  # Common encodings 
    for encoding in encodings:
        try:
            with open(csv_file_path, 'r', encoding=encoding) as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    track_name = row["Track Name"]
                    feature = row['Feature']
                    value = row['Value']
                    section_index = row['Section Index']

                    # Extracting features
                    if feature in ['Duration', 'Danceability', 'Energy', 'Tempo', 'Valence']:
                        if track_name not in extracted_features:
                            extracted_features[track_name] = {}
                        extracted_features[track_name][feature] = value

                    # Counting unique section indices
                    if section_index:  # This checks if section index is not empty
                        if track_name not in section_indices_count:
                            section_indices_count[track_name] = set()
                        section_indices_count[track_name].add(section_index)

                file_read_success = True
                break  # If successful, exit the loop

        except UnicodeDecodeError:
            print(f"Trying different encoding: {encoding} didn't work")

    if not file_read_success:
        raise Exception("Unable to read the file with provided encodings.")

    # Convert set counts to the number of unique indices and calculate complexity ratios
    for track_name in section_indices_count:
        section_count = len(section_indices_count[track_name])
        duration = float(extracted_features[track_name]['Duration']) if 'Duration' in extracted_features[
            track_name] else 0
        #complexity = complexity_ratio(duration, section_count)
        #extracted_features[track_name]['Complexity'] = complexity

    return extracted_features

def complexity_ratio(duration_ms, section_count):
    duration_in_minutes = (duration_ms / 1000) / 60
    duration_in_minutes = round(duration_in_minutes, 1)
    if duration_in_minutes > 0:
        return section_count / duration_in_minutes
    else:
        return 0

def sort_feature_data(features, sort_key):
    # Convert dictionary to a list of tuples (track_name, feature_dict)
    track_feature_list = [(track, feature_dict) for track, feature_dict in features.items()]

    # Sort the list by the specified feature in descending order
    sorted_list = sorted(track_feature_list, key=lambda x: float(x[1][sort_key]), reverse=True)

    return sorted_list

def sort_feature_data_multiple(features, sort_key1, sort_key2): #CHEAP WAY, you should combine this function with the one above and allow for multiple keys if wanted, ALTERNATIVELY do a if block which sees how many sort keys are given
    # Convert dictionary to a list of tuples (track_name, feature_dict)
    track_feature_list = [(track, feature_dict) for track, feature_dict in features.items()]
    for track, feature_dict in features.items():
        print("Inside SORTING def: ", track)
    # Sort the list by the specified features in descending order
    sorted_list = sorted(track_feature_list, key=lambda x: (float(x[1][sort_key1]), float(x[1][sort_key2])), reverse=True)

    return sorted_list

def export_sorted_csv(sorted_lists, feature_keys, output_file_path):
    with open(output_file_path, "w", newline="", encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)

        # Write header
        header = ["Track Name"]
        for key in feature_keys:
            header.extend([key])
        writer.writerow(header)

        # Assuming all lists have the same length and corresponding tracks
        for i in range(len(sorted_lists[0])):
            row = []
            for j, sorted_list in enumerate(sorted_lists):
                track_name, features = sorted_list[i]
                print(feature_keys[j], j)
                if j == 0:  # Add track name only once
                    row.append(track_name)
                row.append(features.get(feature_keys[j], ""))
            #print(row)
            writer.writerow(row)
            """
                if track_name in profanity_percent_dict:
                    profanity = profanity_percent_dict[track_name]
                else:
                    # Handle the case where the track is not in the dictionary
                    profanity = f"{track_name} does not have a profanity test"

                prof_list.extend([track_name, profanity])
            """
                #row.extend([str(track_name), feature_value])

            #print(row)
            #writer.writerow(row)
        #writer.writerow(prof_list)

def export_sorted_csv_complex(extracted_features, feature_keys, output_file_path):
    with open(output_file_path, "w", newline="", encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)

        # Write header
        header = ["Track Name"] + feature_keys
        writer.writerow(header)

        # Sort and write data
        for track_name, features in extracted_features.items():
            row = [track_name] + [features.get(key, "") for key in feature_keys]
            writer.writerow(row)

def clean_string(s):
    # Remove text within parentheses
    s = re.sub(r'\([^)]*\)', '', s).strip()

    # Normalize and remove accents
    s = unicodedata.normalize('NFD', s)
    s = ''.join([char for char in s if unicodedata.category(char) != 'Mn'])

    # Remove specific punctuation characters
    punctuation_to_remove = "'!.,-+"
    s = ''.join(char for char in s if char not in punctuation_to_remove)

    return s

# Format artist name and track name to fit the Genius.com url format
def format_artist_name(name):
    return name[0].upper() + name[1:].lower() if name else ''

def format_track_name(name):
    return name.lower()

def scrape_lyrics_from_genius(track_name, artist_name):
    # Format the search URL
    base_url = "https://genius.com/"
    clean_artist_name = format_artist_name(clean_string(artist_name)).replace(' ', '-')
    clean_track_name = format_track_name(clean_string(track_name)).replace(' ', '-')

    search_url = f"{base_url}{clean_artist_name}-{clean_track_name}-lyrics"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        lyrics_div = soup.find('div', class_='lyrics')
        lyrics = lyrics_div.get_text().strip() if lyrics_div else "Lyrics not found"

        return lyrics

    except requests.RequestException as e:
        return f"Error: {e}"

def find_vulgar_words_in_lyrics(lyrics, vulgar_list):
    found_words = set()
    for word in vulgar_list:
        # Create a regular expression to match the word and its variations
        regex = re.compile(r'\b' + re.escape(word) + r'\w*\b', re.IGNORECASE)
        matches = regex.findall(lyrics)
        found_words.update(matches)
    return found_words

def get_word_list(file_path: str, language_list):

    with open(file_path, 'r') as file:

        for line in file:

            # Each word is on a new line, strip to remove any trailing newline characters

            word = line.strip()

            if word:  # Ensure the line is not empty
                language_list.append(word)

    return language_list

def compute_position_differences(list1, list2):
    position_diff = {}

    # Create a mapping of track names to their positions in each list
    positions_in_list1 = {track[0]: idx for idx, track in enumerate(list1)}
    positions_in_list2 = {track[0]: idx for idx, track in enumerate(list2)}

    # Calculate the position differences
    for track in positions_in_list1:
        print("This is the compute pos function: ", track)
        if track in positions_in_list2:
            position_diff[track] = abs(positions_in_list1[track] - positions_in_list2[track])

    return position_diff

def sort_position(position_dict):
    ordered_dict_pos = {}
    # Sort the dictionary by its values in descending order
    ordered_pos = sorted(position_dict.items(), key=lambda x: x[1], reverse=True)
    ordered_pos_diff = []
    #print(ordered_pos)
    # Create a new dictionary with positions
    for n, (track, pos) in enumerate(ordered_pos):
        #print(n, "followed by the pos variables", pos)
        ordered_dict_pos[track] = pos  # Assign the new position (n) for each track

        #ordered_pos_diff.append(ordered_dict_pos)
    #print(ordered_dict_pos))
    return ordered_dict_pos

def add_position_difference_to_tuples(sorted_lists, position_dict_list):
    updated_lists = []

    # Convert position_list to a dictionary for easier access
    position_dict = dict(position_dict_list)

    updated_list = []
    for iteration, track_tuple in enumerate(sorted_lists):
        #print("This is the ith iteration and the track tuple", iteration, track_tuple)



        track_name, feature_dict = track_tuple
        #print(track_name, feature_dict)
        print("inside adding pos function: ", track_name)
        pos_val = position_dict.get(track_name)

        # Add position difference to the feature dictionary
        updated_feature_dict = {**feature_dict, "Position Difference": pos_val}

        updated_list.append((track_name, updated_feature_dict))


    updated_lists.extend(updated_list)
    #print("This is the updated list with position differences", len(updated_lists), len(updated_list))

    return updated_lists


# usage
csv_file_path = "C:\\your\\path\\sleep_music_spotify.csv"
features = extract_features_from_csv(csv_file_path)
#features = extract_features_from_csv_complexity(csv_file_path)
#print(len(features))

# Sort by each feature
#sorted_by_danceability = sort_feature_data(features, 'Danceability')
#sorted_by_energy = sort_feature_data(features, 'Energy')
#sorted_by_tempo = sort_feature_data(features, 'Tempo')
#sorted_by_valence = sort_feature_data(features, 'Valence')
#sorted_by_speechiness = sort_feature_data(features, 'Speechiness')

sorted_by_danceability_and_valence = sort_feature_data_multiple(features, 'Danceability', 'Valence')
sorted_by_energy_and_tempo = sort_feature_data_multiple(features, "Energy", "Tempo")
position_differences = compute_position_differences(sorted_by_danceability_and_valence, sorted_by_energy_and_tempo)
#print("This is the current situation with computing positions ", len(position_differences), position_differences)
ordered_pos = sort_position(position_differences)
print("Checking features in the dictionary :", sorted_by_danceability_and_valence)



sorted_by_energy_and_tempo = add_position_difference_to_tuples(sorted_lists=sorted_by_energy_and_tempo, position_dict_list=ordered_pos)
sorted_by_danceability_and_valence = add_position_difference_to_tuples(sorted_by_danceability_and_valence, ordered_pos)
#print(len(sorted_by_energy_and_tempo))

# Now you have 5 different sorted lists
#print("Sorted by Danceability:", sorted_by_danceability)
#print("Sorted by Energy:", sorted_by_energy)
#print("Sorted by Tempo:", sorted_by_tempo)
#print("Sorted by Valence:", sorted_by_valence)
#print("Sorted by Speechiness:", sorted_by_speechiness)

french_vulgar = []
spanish_vulgar = []
english_vulgar = []

#Extraction of data 

#sorted_lists = [sorted_by_danceability, sorted_by_energy, sorted_by_tempo, sorted_by_valence, sorted_by_speechiness]
sorted_lists = [sorted_by_danceability_and_valence, sorted_by_danceability_and_valence, sorted_by_energy_and_tempo, sorted_by_energy_and_tempo, sorted_by_energy_and_tempo, sorted_by_energy_and_tempo, sorted_by_energy_and_tempo, sorted_by_energy_and_tempo]
output_file_path = "C:\\your\\path\\sorted_sleep_music.csv"

#features = extract_features_from_csv_complexity(csv_file_path)
#feature_keys = ['Danceability', 'Energy', 'Tempo', 'Valence', 'Speechiness', 'Complexity']  # Add 'Complexity

feature_keys = ['Danceability', 'Valence', 'Energy', 'Tempo', "Loudness", "Speechiness", "Track Popularity", "Position Difference"]
#print(len(sorted_lists[0]), len(sorted_by_danceability_and_valence))
export_sorted_csv(sorted_lists, feature_keys, output_file_path)

#export_sorted_csv_complex(features, feature_keys, output_file_path) #THIS IS TO EXPORT BASED ON THE FEATURES ONLY, using additional complexity measurement, it does not sort the lists.


#TODO
## Create Pearson's correlation, create a py file that opens and extract info from many types of files
## Correlation function is indepedent, but takes in any list of numbers. Create other functions that extracts numbers into list (which is a distribution),
## Have function that takes out desired numbers (case-specific) and outputs distirbution to text file (systematic), which can then be analysed and correlated



