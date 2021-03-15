import sys
import re
import requests
import unicodedata
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from spanbert import SpanBERT
import spacy

queried = set()
extracted_tuples = dict()
spanbert = SpanBERT("./pretrained_spanbert")
nlp = spacy.load("en_core_web_lg")
possible_relations = [("per:schools_attended","PERSON", ["ORGANIZATION"]),
                      ("per:employee_of","PERSON", ["ORGANIZATION"]), 
                      ("per:cities_of_residence","PERSON", ["LOCATION","CITY","STATE_OR_PROVINCE","COUNTRY"]),
                      ("org:top_members/employees","ORGANIZATION", ["PERSON"])]
import spacy

spacy2bert = { 
        "ORG": "ORGANIZATION",
        "PERSON": "PERSON",
        "GPE": "LOCATION", 
        "LOC": "LOCATION",
        "DATE": "DATE"
        }

bert2spacy = {
        "ORGANIZATION": "ORG",
        "PERSON": "PERSON",
        "LOCATION": "LOC",
        "CITY": "GPE",
        "COUNTRY": "GPE",
        "STATE_OR_PROVINCE": "GPE",
        "DATE": "DATE"
        }


def get_entities(sentence, entities_of_interest):
    return [(e.text, spacy2bert[e.label_]) for e in sentence.ents if e.label_ in spacy2bert]


def create_entity_pairs(sents_doc, entities_of_interest, window_size=40):
    '''
    Input: a spaCy Sentence object and a list of entities of interest
    Output: list of extracted entity pairs: (text, entity1, entity2)
    '''
    entities_of_interest = {bert2spacy[b] for b in entities_of_interest}
    ents = sents_doc.ents # get entities for given sentence

    length_doc = len(sents_doc)
    entity_pairs = []
    for i in range(len(ents)):
        e1 = ents[i]
        if e1.label_ not in entities_of_interest:
            continue

        for j in range(1, len(ents) - i):
            e2 = ents[i + j]
            if e2.label_ not in entities_of_interest:
                continue
            if e1.text.lower() == e2.text.lower(): # make sure e1 != e2
                continue

            if (1 <= (e2.start - e1.end) <= window_size):

                punc_token = False
                start = e1.start - 1 - sents_doc.start
                if start > 0:
                    while not punc_token:
                        punc_token = sents_doc[start].is_punct
                        start -= 1
                        if start < 0:
                            break
                    left_r = start + 2 if start > 0 else 0
                else:
                    left_r = 0

                # Find end of sentence
                punc_token = False
                start = e2.end - sents_doc.start
                if start < length_doc:
                    while not punc_token:
                        punc_token = sents_doc[start].is_punct
                        start += 1
                        if start == length_doc:
                            break
                    right_r = start if start < length_doc else length_doc
                else:
                    right_r = length_doc

                if (right_r - left_r) > window_size: # sentence should not be longer than window_size
                    continue

                x = [token.text for token in sents_doc[left_r:right_r]]
                gap = sents_doc.start + left_r
                e1_info = (e1.text, spacy2bert[e1.label_], (e1.start - gap, e1.end - gap - 1))
                e2_info = (e2.text, spacy2bert[e2.label_], (e2.start - gap, e2.end - gap - 1))
                if e1.start == e1.end:
                    assert x[e1.start-gap] == e1.text, "{}, {}".format(e1_info, x)
                if e2.start == e2.end:
                    assert x[e2.start-gap] == e2.text, "{}, {}".format(e2_info, x)
                entity_pairs.append((x, e1_info, e2_info))
    return entity_pairs

# Method to get top ten results from Google Custom Search API (From example in Project 1)
def get_query(api_key, engine_key, query):
    s = build("customsearch","v1",developerKey=api_key)
    res = s.cse().list(
        q=query,
        cx=engine_key
    ).execute()
    return res['items']


# Extract plaintext from url
def to_plaintext(url):
    print("\tFetching text from url ...")
    try:
        res = requests.get(url,timeout=5)
        html_page = res.text.encode('ascii','ignore')
        soup = BeautifulSoup(html_page, 'html.parser')
        [s.decompose() for s in (soup(['img','script','head','nav','form','sup']))]
        text = soup.get_text(strip=True, separator=' ').replace("\n", "").replace("\t", "").replace("  ", ' ')
        text = unicodedata.normalize("NFKD",text)
    except:
        return ""
    print(len(text))
    
    return text[:20000]


# Annotate with Spacy, then extract relations using SpanBert
def annotate(text, relationship, threshold):
    print("\tAnnotating the webpage using spacy...")
    target_subject = possible_relations[relationship][1]
    target_objects = possible_relations[relationship][2]
    entities_of_interest = target_objects + [target_subject]
    doc = nlp(text)
    sentences = [x for x in list(doc.sents) if (len(str(x).strip()) > 1) and (len(get_entities(x,entities_of_interest)) >1)] 
    num_sentences = len(sentences)

    print(f"\tExtracted {num_sentences} sentences. Processing each sentence one by one to check for presence of right pair of named entity types; if so, will run the second pipeline ...")
    index = 1
    num_extracted = 0
    num_relations = 0
    num_overall = 0
    for sentence in sentences:
        flag = False
        if((index%5==0)):
            print(f"\tProcessed {index} / {num_sentences} sentences")
        candidate_pairs = []
        sentence_entity_pairs = create_entity_pairs(sentence, entities_of_interest)
        for ep in sentence_entity_pairs:
            # TODO: keep subject-object pairs of the right type for the target relation (e.g., Person:Organization for the "Work_For" relation)
            if((ep[1][1] == target_subject) and (ep[2][1] in target_objects)):
                candidate_pairs.append({"tokens": ep[0], "subj": ep[1], "obj": ep[2]})  # e1=Subject, e2=Object
            elif((ep[2][1] == target_subject) and (ep[1][1] in target_objects)):
                candidate_pairs.append({"tokens": ep[0], "subj": ep[2], "obj": ep[1]})  # e1=Subject, e2=Object
            
        candidate_pairs = [p for p in candidate_pairs if not p["subj"][1] in ["DATE", "LOCATION"]]  # ignore subject entities with date/location type

        if len(candidate_pairs) == 0:
            index +=1
            continue

        relation_preds = spanbert.predict(candidate_pairs)  # get predictions: list of (relation, confidence) pairs
        for ex, pred in list(zip(candidate_pairs, relation_preds)):
            r = pred[0]
            confidence = pred[1]
            subj = ex["subj"][0]
            obj = ex["obj"][0]
            if((r == possible_relations[relationship][0])):
                print(f"\t\t=== Extracted Relation ===")
                num_overall +=1
                print(f"\t\tSentence: {sentence}")
                print(f"\t\tConfidence: {confidence}; Subject: {subj}; Object: {obj}")
                if((confidence >= threshold)):
                    flag = True
                    key = (subj, obj)
                    if key in extracted_tuples:
                        if(confidence < extracted_tuples[key]):
                            print("Duplicate with lower confidence than existing record. Ignoring this.")
                        else:
                            print(f"\t\tAdding to the set of extracted relations")
                            num_relations +=1
                            extracted_tuples[key] = confidence
                    else:
                        print(f"\t\tAdding to the set of extracted relations")
                        num_relations +=1
                        extracted_tuples[key] = confidence
                else:
                    print(f"\t\tConfidence is lower than threshold confidence. Ignoring this.")
                print(f"\t\t==========")        
        if(flag):
            num_extracted += 1

        index +=1
    print(f"Extracted annotations for  {num_extracted}  out of total  {num_sentences}  sentences")    
    print(f"Relations extracted from this website: {num_relations} (Overall: {num_overall})")
    return doc

if __name__ == "__main__":

    # First parse and validate arguments
    if(len(sys.argv) != 7):
        print(f"Usage: {sys.argv[0]} <google api key> <google engine id> <r> <t> <q> <k>")
    
    client_key = sys.argv[1]
    engine_key = sys.argv[2]
    relation = int(sys.argv[3])-1
    threshold = float(sys.argv[4])
    query = sys.argv[5]
    num_tuples = int(sys.argv[6])
    is_complete = False

    print("-----")
    print("Parameters:")
    print(f"Client Key     = {client_key}")
    print(f"Engine Key     = {engine_key}")
    print(f"Relation       = {possible_relations[relation][0]}")
    print(f"Threshold      = {threshold}")
    print(f"Query          = {query}")
    print(f"# of Tuples    = {num_tuples}")
    print("Loading necessary libraries; This should take a minute or so ...")

    iterations = 0
    
    seen_urls = []
    while((True) and (len(extracted_tuples) < num_tuples)):
        print(f"=========== Iteration: {iterations} - Query: {query} ===========")
        queried.add(query)
        results = get_query(client_key,engine_key,query)
        num_urls = len(results)
        for i in range(len(results)):
            url = results[i]['link']
            print(f"URL ( {i+1} / {len(results)}): {url}")
            if(url not in seen_urls):
                seen_urls.append(url)
                text = to_plaintext(url)
                if(len(text) <= 0):
                    print("Unable to fetch text from URL. Continuing")
                    continue
                print(f"\tWebpage length (num characters): {len(text)}")
                annotated = annotate(text,relation, threshold)
            else:
                print(f"URL already seen. skipping...")
                
        sorted_extracted_tuples = sorted(extracted_tuples.items(), key=lambda item: item[1], reverse=True)
        if(len(extracted_tuples) < num_tuples):
            old_query = query
            for entry in sorted_extracted_tuples:
                temp_query = entry[0][0] + " " + entry[0][1]
                if temp_query not in queried:
                    query = temp_query
                    break
            print("This is the new query {}".format(query))
            if (old_query == query):
                print("ISE has stalled before retrieving k high-confidence tuples")
                print(f"============= ALL RELATIONS for {possible_relations[relation][0]} ({len(extracted_tuples)}) =============")
                for res in sorted_extracted_tuples:
                    print(f"Confidence: {res[1]}          | Subject: {res[0][0]}       | Object: {res[0][1]}")
                break
        print(f"============= ALL RELATIONS for {possible_relations[relation][0]} ({len(extracted_tuples)}) =============")
        for res in sorted_extracted_tuples:
            print(f"Confidence: {res[1]}          | Subject: {res[0][0]}       | Object: {res[0][1]}")
                          
        iterations+=1
    print(f"Total # of iterations = {iterations}")

    
