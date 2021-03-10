# -*- coding: utf-8 -*-
import sys
import requests

from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from spanbert import SpanBERT

import spacy
from spacy_help_functions import get_entities, create_entity_pairs

queried = set()
extracted_tuples = set()
spanbert = SpanBERT("./pretrained_spanbert")
nlp = spacy.load("en_core_web_lg")
possible_relations = [("per:schools_attended","PERSON", ["ORGANIZATION"]),
                      ("per:employee_of","PERSON", ["ORGANIZATION"]), 
                      ("per:cities_of_residence","PERSON", ["LOCATION","CITY","STATE_OR_PROVINCE","COUNTRY"]),
                      ("org:top_members/employees","ORGANIZATION", ["PERSON"])]

# Method to get top ten results from Google Custom Search API (From example in Project 1)
def get_query(api_key, engine_key, query):
    s = build("customsearch","v1",developerKey=api_key)
    res = s.cse().list(
        q=query,
        cx=engine_key
    ).execute()
    return res['items']

def to_plaintext(url):
    print("\tFetching text from url ...")
    res = requests.get(url)
    html_page = res.content.decode('utf-8','ignore')
    soup = BeautifulSoup(html_page, 'html.parser')
    [s.decompose() for s in soup(['script','sup','i'])]
    text = soup.body.get_text()
    # import code; code.interact(local=dict(globals(), **locals()))
    print(len(text))
    return text[:20000]

def annotate(text, relationship, threshold):
    print("\tAnnotating the webpage using spacy...")
    target_subject = possible_relations[relationship][1]
    target_objects = possible_relations[relationship][2]
    entities_of_interest = target_objects + [target_subject]
    doc = nlp(text)
    num_sentences = len(list(doc.sents))

    print(f"\tExtracted {num_sentences} sentences. Processing each sentence one by one to check for presence of right pair of named entity types; if so, will run the second pipeline ...")
    index = 1
    for sentence in doc.sents:
        if((index%5==0)):
            print(f"\tProcessed {index} / {num_sentences} sentences")
        ents = get_entities(sentence, entities_of_interest)
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
            subject = ex["subj"][0]
            object = ex["obj"][0]
            if((r == possible_relations[relationship][0])):
                print(f"\t\t=== Extracted Relation ===")
                print(f"\t\tSentence: {sentence}")
                print(f"\t\tConfidence: {confidence}; Subject: {subject}; Object: {object}")
                if((confidence >= threshold)):
                    print(f"\t\tAdding to the set of extracted relations")
                    extracted_tuples.add((subject,object,confidence))
                else:
                    print(f"\t\tConfidence is lower than threshold confidence. Ignoring this.")
                print(f"\t\t==========")        
        index +=1    
    return doc

def spanBert_phase(threshhold, relation, num_tuples,  queried, extracted_tuples, candidate_pairs):
    relation_preds = spanbert.predict(candidate_pairs)
    for ex, pred in list(zip(candidate_pairs, relation_preds)):
        print("\tSubject: {}\tObject: {}\tRelation: {}\tConfidence: {:.2f}".format(ex["subj"][0], ex["obj"][0], pred[0], pred[1]))
        if (pred[0] == possible_relations[relation][0]):
            confidence = pred[1]
            if (confidence >= threhold):
                curr_tuple = (ex["subj"][0], ex["obj"][0]), confidence)
                if curr_tuple not in extracted_tuples:
                    extracted_tuples.add(curr_tuple)
            else:
                continue
    
    sorted_extracted_tuples = sorted(extracted_tuples, key=lambda tup: tup[2], reverse=True)
    if(len(extracted_tuples) < num_tuples):
        new_query = ""
        for entry in sorted_extracted_tuples:
            temp_query = entry[0] + " " + entry[1]
            if temp_query not in queried:
                new_query = temp_query
                break
        
        print("This is the new query {}".format(new_query))
        return (False, new_query)
    else:
        return (True, sorted_extracted_tuples, len(sorted_extracted_tuples))
            

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
    while(iterations != 1):
        print(f"=========== Iteration: {iterations} - Query: {query} ===========")
        results = get_query(client_key,engine_key,query)
        num_urls = len(results)
        for i in range(len(results)):
            url = results[i]['formattedUrl']
            print(f"URL ( {i+1} / {len(results)}): {url}")
            if(url not in seen_urls):
                seen_urls.append(url)
                text = to_plaintext(url)
                print(f"\tWebpage length (num characters): {len(text)}")
                annotated = annotate(text,relation, threshold)
        
        print(seen_urls)
        
        iter_result = spanBert_phase(threshhold, relation, num_tuples, candidate_pairs)
        if (iter_result[0] and iter_result[1] > 0):
            query = iter_result[1]
        else if (iter_result[0]):
            printf("ISE has stalled before retrieving k high-confidence tuples")
            return
        else:

            print(f"============= ALL RELATIONS for {possible_relations[relation][0]} ({iter_result[2]}) =============")
            for res in iter_result[1]:
                print(f"Confidence: {res[2]}          | Subject: {res[0]}       | Object: {res[1]}")
            print(f"Total # of iterations = {iterations}")
            return
                          
        iterations+=1   
