import re
from datetime import datetime
import spacy
from methods.matching import find_matches
import cv2
import numpy as np



# Load Spacy NLP model once at startup
nlp = spacy.load('en_core_web_md')


def extract_dates(text):

    print('Extracting dates from text:', text)
    mfg = None
    exp = None
    
    date_patterns = [
        r'\b\d{2}/\d{4}\b',
        r'\b\d{2}-\d{4}\b',
        r'\b\d{2}\.\d{4}\b',
        r'\b\w{3}-\d{2}\b',
        r'\b\w{3} \d{2}\b',
        r'\b\w{3}\.\d{2}\b',
        r'\b\w{3}\.\d{4}\b',
    ]


    # Extract dates
    date_matches = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        date_matches.extend(matches)
    print('Date matches:', date_matches)
    # Parse dates using datetime to determine MFG and EXP
    parsed_dates = []
    for date_str in date_matches:
        try:
            # Handle different date formats
            if re.match(r'\b\d{2}/\d{4}\b', date_str):
                date = datetime.strptime(date_str, '%m/%Y')
            elif re.match(r'\b\d{2}-\d{4}\b', date_str):
                date = datetime.strptime(date_str, '%m-%Y')
            elif re.match(r'\b\d{2}.\d{4}\b', date_str):
                date = datetime.strptime(date_str, '%m.%Y')
            elif re.match(r'\b\w{3}-\d{2}\b', date_str):
                date = datetime.strptime(date_str, '%b-%y')
            elif re.match(r'\b\w{3} \d{2}\b', date_str):
                date = datetime.strptime(date_str, '%b %y')
            elif re.match(r'\b\w{3}.\d{2}\b', date_str):
                date = datetime.strptime(date_str, '%b.%y')
            elif re.match(r'\b\w{3}.\d{4}\b', date_str):
                date = datetime.strptime(date_str, '%b.%Y')
            else:
                # Use spaCy to parse the date
                doc = nlp(date_str)
                for ent in doc.ents:
                    if ent.label_ == 'DATE':
                        date = ent.text
                        break
            parsed_dates.append(date)
            print('Parsed date:', date)
        except ValueError:
            print('Invalid date format:', date_str)
            continue

    # Remove duplicates from parsed dates
    unique_dates = list(set(parsed_dates))
    unique_dates.sort()

    # Assign MFG and EXP based on unique dates
    if unique_dates:
        mfg = unique_dates[0].strftime('%m/%Y')
        if len(unique_dates) > 1:
            exp = unique_dates[1].strftime('%m/%Y')
    # remove dates from text
    for date in date_matches:
        text = text.replace(date, '')

    print('MFG Date:', mfg)
    print('EXP Date:', exp)

    return mfg, exp, text



def extract_details(text, price, picknote):


    # extract dates
    mfg, exp, text = extract_dates(text)


    org_batch_no, batch_no = extract_batch_number(text)

    print('Extracted batch number:', batch_no)
    print('Extracted MFG Date:', mfg)
    print('Extracted EXP Date:', exp)
    print('Extracted Price:', price)
    batch_no, mfgDate,expDate,price, product_name, product_code = find_matches(org_batch_no, mfg, exp, price, picknote)

    
    return org_batch_no, batch_no, mfgDate, expDate, price, product_name, product_code




def extract_batch_number(text):

    # Initialize variables
    org_batch_no = None
    batch_no = None


    # Extract batch number
    batch_no_match = re.search(r'[a-zA-Z]*-*/*[0-9]+[a-zA-Z]*[0-9]*', text)
    if batch_no_match:
        org_batch_no = batch_no_match.group()

    # Remove special characters from the batch number
    if org_batch_no:
        org_batch_no = re.sub(r'[^a-zA-Z0-9]', '', org_batch_no)

    return org_batch_no, batch_no




def filter_text(results, min_text_length=5, confidence_threshold=0.40):
    filtered_results = []
    text = ''
    if len(results) > 1:
        price = results[-1][1]
        for result in results:
            text = result[1]
            confidence = result[2]
            if confidence > confidence_threshold:
                filtered_results.append(result)
        return filtered_results, price
    return filtered_results, None

def extract_text(image_data, reader):
    image = image_data
    image_np = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    recognition_results = reader.readtext(image_np)
    return recognition_results