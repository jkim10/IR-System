# -*- coding: utf-8 -*-
import sys
import pprint
import string
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
from googleapiclient.discovery import build
from nltk.stem import PorterStemmer 

alpha = 1.0
beta = 0.75
gamma = 0.15

ps = PorterStemmer() 

# Method to get top ten results from Google Custom Search API (From example in Project 1)
def get_query(api_key, engine_key, query):
    s = build("customsearch","v1",developerKey=api_key)
    res = s.cse().list(
        q=query,
        cx=engine_key
    ).execute()
    return res['items']

# Holds all the normalizing we want (stemming, lowercasing, punctuation)
def normalize_text(text):
    text = text.lower()
    text = text.translate(str.maketrans('','', string.punctuation))
    text = ps.stem(text)
    return text

#Calculate TF-IDF Table
def tf_idf(relevant, irrelevant,query):
    cleaned = [normalize_text(query)]
    documents = relevant + irrelevant
    for article in documents:
        snippet = article.get('snippet','') + " " + article['title']
        cleaned.append(normalize_text(snippet))
    tfidf_vectorizer = TfidfVectorizer(stop_words="english", sublinear_tf=True)
    vectors = tfidf_vectorizer.fit_transform(cleaned)
    feature_names = tfidf_vectorizer.get_feature_names()
    df = pd.DataFrame(vectors.todense().tolist(), columns=feature_names)
    return (df.head(),df.iloc[1:len(relevant)+1],df.tail(len(irrelevant))) # Return first the query, the relevant, and then the irrelevant

# Method to augment query. Returns addition to query
def augment_query(query, relevant_articles, irrelevant_articles):
    if not relevant_articles:
        return ""
    (query_vector, relevant_vector, irrelevant_vector) = tf_idf(relevant_articles,irrelevant_articles, query)
    ## Rocchio
    term1 = dict(((query_vector * alpha)).sum())
    term2 = dict(((relevant_vector * beta) / len(relevant_articles)).sum())
    term3 = dict(((irrelevant_vector * gamma) / len(irrelevant_articles)).sum())
    result = {key: max(0, term1.get(key,0) + term2[key] - term3.get(key, 0)) for key in term2}
    sorted_result = sorted(result, key=result.get, reverse=True)
    augment = []
    for word in sorted_result:
        if(len(augment) == 2):
            break
        else:
            if(word not in query):
                augment.append(word)           

    return " ".join(augment)




if __name__ == "__main__":
    # First parse and validate arguments
    if(len(sys.argv) != 5):
        print(f"Usage: {sys.argv[0]} <API Key> <Engine Key> <Precision> <Query>")
    
    client_key = sys.argv[1]
    engine_key = sys.argv[2]
    target_precision = float(sys.argv[3])
    query = sys.argv[4].strip('"')

    is_complete = False
   

    top_ten = get_query(client_key, engine_key, query)
   
    while not (is_complete):
        print("Parameters:")
        print(f"Client Key = {client_key}")
        print(f"Engine Key = {engine_key}")
        print(f"Query      = {query}")
        print(f"Precision  = {target_precision}")
        print("Google Search Results:")
        print("======================")

        if(len(top_ten) != 10):
            print("Could not obtain 10 relevant articles")
            quit()
            
        res_count = 1
        relevant = []
        irrelevant = []

        # Display and guage results
        for result in top_ten:
            print(f"Result {res_count}")
            print("[")
            print(f" URL: {result.get('formattedUrl','null')}")
            print(f" Title: {result.get('title','null')}")
            print(f" Summary: {result.get('snippet','null')}")
            print("]\n")
            is_relevant = input("Relevant (Y/N)?")
            if (is_relevant.lower() == "y"):
                relevant.append(result)
            else:
                irrelevant.append(result)
            res_count+=1
        print("======================")
        print("FEEDBACK SUMMARY")
        print(f"Query {query}")
    
        # Calculate Precision
        precision = len(relevant) / (len(relevant) + len(irrelevant))
        print(f"Precision {precision}")
        if(precision >= target_precision): # If target precision reached, exit program
            print("Desired precision reached, done")
            is_complete=True
        else: # Else continue and augment query
            print(f"Still below the desired precision of {target_precision}")
            print("Indexing Results ....")
            augment = augment_query(query, relevant,irrelevant)
            print("Indexing Results ....")
            print(f"Augmenting by {augment}")
            if((precision == 0) or (augment == "")): # Keeping this for now to match the example format, but may change
                print("Below desired precision, but can no longer augment the query")
                quit()
            query += " " + augment
            top_ten = get_query(client_key, engine_key, query)


