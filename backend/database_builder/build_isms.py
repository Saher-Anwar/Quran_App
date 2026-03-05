import requests
import logger

def parse_line(line):
    """
    Parses a line of text into a list of words.

    Args:
        line (str): The line of text to be parsed.

    Returns:
        list: location - word - tag - description.
    """
    parsed_line = line.split()
    if len(parsed_line) < 4:
        return None
    
    if not parsed_line or not is_ism(parsed_line[2], parsed_line[3]):
        return None
    
    description = extract_description(parsed_line[3])
    ism = parse_description(description)

    ism.update(extract_location(parsed_line[0]))
    ism["word"] = parsed_line[1]
    ism["tag"] = parsed_line[2]

    return ism

def extract_location(location):
    """
    Parses a location string into a list of integers.

    Args:
        location (str): The location string to be parsed.

    Returns:
        list: A list of integers representing the location -> chapter - verse - word - token.
    """
    res = location.split(":")
    return {"chapter": int(res[0]), "verse": int(res[1]), "word_num": int(res[2]), "token": int(res[3])}

def is_ism(tag_segment, desc_segment):
    """
    Checks if the word is an ism (interrogative pronoun).

    Returns:
        bool: True if the word is an ism, False otherwise.
    """
    if "PN" in desc_segment:
        return True
    
    return False if "ROOT" not in desc_segment or tag_segment != "N" else True

def extract_description(description):
    """
    Segments a description string into a list of strings using \'|\' as the splitter.

    Args:
        description (str): The description string to be parsed.

    Returns:
        list: A list of strings representing the description.
    """       

    return description.split("|")

def parse_description(segments : list[str]):
    """
    Iterates over each segment and parses it accordingly.

    Args:
        segment (str): The segment string to be parsed.

    Returns:
        JSON: A JSON containing the root word, lemma, and properties of an ism.
    """ 
    res = {}
    cases = ["NOM", "ACC", "GEN"]
    res['status'], res["gender"], res["number"], res["type"] = "NOM", "M", "S", "proper" # Default values
    
    for segment in segments:
        if "ROOT" in segment:
            res["root"] = segment.split(":")[1]
        elif "LEM" in segment:
            res["lem"] = segment.split(":")[1]
        elif segment in cases:
            res["status"] = segment
        elif "INDEF" in segment:
            res["type"] = "common"
        else:
            temp = extract_gender_number(segment)
            if temp:
                res["gender"], res["number"] = temp

    return res

def extract_gender_number(segment):
    """
    Extracts the gender from a segment string.

    Args:
        segment (str): The segment string to be parsed.

    Returns:
        str: The gender extracted from the segment.
    """
    possible_results = ["M", "F", "MD", "FD", "MP", "FP"]
    for gen_num in possible_results:
        if gen_num in segment:
            return (gen_num, "S") if len(gen_num) == 1 else (gen_num[0], gen_num[-1])
    
    return None

def parse_file(file_path):
    """
    Parses a file and returns a list of isms.

    Args:
        file_path (str): The path to the file to be parsed.

    Returns:
        list: A list of isms.
    """
    isms = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parsed_line = parse_line(line)
            if parsed_line:
                isms.append(parsed_line)
    return isms

def test_parser():
    sample_text = "47:2:9:1	مُحَمَّدٍ	N	PN|ROOT:حمد|LEM:مُحَمَّد|GEN"
    print(parse_line(sample_text))

if __name__ == "__main__":
    file_path = "quran-morphology.txt"    # NOTE: delete this
    isms = parse_file(file_path)

    for ism in isms:

        res = requests.post('http://localhost:5000/submit', json=ism)
        if res.status_code == 200 or res.status_code == 201:
            print("Success")
        else:
            print(ism)
            print(res.status_code)
            print(res.text)
            break
