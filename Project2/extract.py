# -*- coding: utf-8 -*-
import sys
import urllib
import requests
import html
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from spanbert import SpanBERT

import spacy
from spacy_help_functions import get_entities, create_entity_pairs

queried = set()
extracted_tuples = dict()
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
    try:
        res = requests.get(url)
        html_page = html.unescape(res.text)
        soup = BeautifulSoup(html_page, 'html.parser')
        [s.decompose() for s in (soup(['img','script','head','ul','li','ol','nav']))]
        text = soup.get_text(strip=True, separator=' ').replace("\n", "").replace("\t", "")
    except:
        return ""
    print(len(text))
    return text[:20000]

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

#def spanBert_phase(threshhold, relation, num_tuples,  queried, extracted_tuples, candidate_pairs):
#    relation_preds = spanbert.predict(candidate_pairs)
#    for ex, pred in list(zip(candidate_pairs, relation_preds)):
#        if (pred[0] == possible_relations[relation][0]):
#            confidence = pred[1]
#            if (confidence >= threhold):
#                curr_tuple = (ex["subj"][0], ex["obj"][0]), confidence)
#                if curr_tuple not in extracted_tuples:
#                    extracted_tuples.add(curr_tuple)
#            else:
#                continue
    
           

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
        results = get_query(client_key,engine_key,query)
        # results = [ {"link": "https://en.wikipedia.org/wiki/Mark_Zuckerberg"},
        #             {"link": "https://news.harvard.edu/gazette/story/2017/05/mark-zuckerbergs-speech-as-written-for-harvards-class-of-2017/"},
        #             {"link": "https://www.youtube.com/watch?v=BmYv8XGl-YU"},
        #             {"link": "https://www.bbc.com/news/world-us-canada-40053163"},
        #             {"link": "https://www.youtube.com/watch?v=gsefnhTK5lc"},
        #             {"link": "https://www.wbur.org/news/2017/05/25/zuckerberg-harvard-commencement"},
        #             {"link": "https://www.youtube.com/watch?v=zW_0b1Vy-Ts"},
        #             {"link": "https://www.bostonglobe.com/metro/2018/04/11/mark-zuckerberg-couldn-stop-mentioning-his-harvard-dorm-room-during-facebook-testimony/slW4rCXyIdyctzEuB93J4L/story.html"},
        #             {"link": "https://www.youtube.com/watch?v=yqr6yLyuHQA"},
        #             {"link": "https://www.cnbc.com/2019/02/06/mark-zuckerbergs-dad-offered-him-college-or-a-mcdonalds-franchise.html"}]
        num_urls = len(results)
        for i in range(len(results)):
            url = results[i]['link']
            print(f"URL ( {i+1} / {len(results)}): {url}")
            if(url not in seen_urls):
                seen_urls.append(url)
                text = to_plaintext(url)
                if(len(text) <= 0):
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
    print(f"Total # of iterations = {iterations+1}")

    