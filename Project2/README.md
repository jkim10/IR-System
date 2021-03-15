# Information Retrieval using ISE
By Justin Kim(jyk2149) and Mavis Athene U Chen(mu2288)

## Files in Submission
- proj2.tar.gz
    - extract.py
    - install.sh
- transcript.txt
- README.md

## How to Run
0. Make sure you have BeautifulSoup, Spacy, and the en_core_web_lg installed 
   ```bash
    pip3 install beautifulsoup4
    pip3 install -U pip setuptools wheel
    pip3 install -U spacy
    python3 -m spacy download en_core_web_lg
```

1. Unzip the proj2.tar.gz:
    `tar -zxf proj2.tar.gz`

2. Move into the proj2 folder:
```bash
    cd proj2
    bash install.sh
```

3. Run extract.py:
    `python3 extract.py <google api key> <google engine id> <r> <t> <q> <k>`





```bash
python3 extract.py <google api key> <google engine id> <r> <t> <q> <k>
```

Google API KEY: AIzaSyC6uXsEBblG4JwiO7X25rG5RDUdQrOmrkc

Google Search Engine ID: db7c825fd9c7885a2

Sample run for the transcript:

```bash
python3 extract.py AIzaSyC6uXsEBblG4JwiO7X25rG5RDUdQrOmrkc db7c825fd9c7885a2 2 .7 "bill gates microsoft" 10
```


## Internal Design

All our code is in `extract.py`. We have one `main` function and 3 other helper functions: `get_query`, `to_plaintext`, `annotate`. In `main` we have our the core logic of ISE: a while loop that keeps track of the number of iterations, a call to `get_query` to get the top 10 web results using [Google Custom Search API](https://developers.google.com/custom-search/), a call to `to_plaintext` to extract actual plain text from a given webpage using [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), a call to `annotate` which uses the [spaCy](https://spacy.io/) library to process and annotate text through linguistic analysis and [SpanBERT](https://github.com/gkaramanolakis/SpanBERT) classifier to extract the specified relations from text documents. At a high level overview, steps 1-2 and steps 4-6 are implemented in `main` and `get_query` and step 3 is implemented in `to_plaintext` and `annotate`. In addition, we followed all the constraints and details from steps 4-6 and also chose to return all extracted tuples in decreasing order of extraction confidence (not just the top-k tuples). 

## Description of "Step 3"

We initilaize a dict to store the extracted tuples, having the tuple (subject, object) as key and confidence as value. After extracting the urls from the google search api, we process each of the url's one by one. We used BeautifulSoup to get the plaintext of the the html. We chose to remove the following tags: 'img','script','head','nav','form','sup'. We strip the excess whitespaces, newlines, and special characters and return the first 20000 characters. Then we use spacy to separate the text into spaces, tokenize, and find the sentence entity pairs. We then filter out relation pairs that we are not interested in and store them as candidate pairs to prepare for SpanBERT. After SpaCy returns candidate pairs, we used SpanBERT to predict the relations with the extraction confidence. If the extraction confidence of a relation pair is below the threshold, we ignore this relation pair. If the extraction confidence of a relation pair is equal or above the threshold, we check if this particular relation pair already exists in our map: if it exists, we take the higher confidence between the current relation pair and the existing relation pair, if it doesn't, we simply add that to our map. 
