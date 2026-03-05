import requests

def build_corpus_database(api_path, file_path):
    """
    Build a corpus database from a text file containing corpus data.

    This function reads a text file specified by file_path, where each line
    contains a corpus data for each word. It retrieves the lines, parses it 
    into a format and sends a POST request to the api path to add the data to 
    the SQL table.

    Parameters:
    file_path (str): The path to the text file containing corpus data.

    Raises:
    RequestException: In case any issues with sending a request to the API endpoint.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            segments = line.split()
            if len(segments) < 3:  # Ensure there's enough data to process
                print(f"Skipping invalid line: {line.strip()}")
                continue
            
            
            # Extract common fields
            chapter, verse, word_num, token = segments[0].split(':')

            # Construct data dictionary
            data = {
                "chapter": int(chapter),
                "verse": int(verse),
                "word_num": int(word_num),
                "token": int(token),
                "tag": segments[1],
                "info": segments[2]
            }

            # Add 'word' field only if there are at least 4 segments
            if len(segments) >= 4:
                data["word"] = segments[1]
                data["tag"] = segments[2]
                data["info"] = segments[3]

            try:
                response = requests.post(api_path, json=data)
                response.raise_for_status()  # Raises HTTPError for bad responses
                print(f"Success: {response.status_code}")
            except requests.RequestException as e:
                print(f"Request failed: {e}")
                print(data)
                break

if __name__ == "__main__":
    file_path = "database_builder/quran-morphology.txt"
    api_path = "http://localhost:8000/api/morphology_item"
    build_corpus_database(api_path, file_path)