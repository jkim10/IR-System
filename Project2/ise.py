# -*- coding: utf-8 -*-
import sys
import pprint
import string
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
from googleapiclient.discovery import build


# Method to get top ten results from Google Custom Search API (From example in Project 1)
def get_query(api_key, engine_key, query):
    s = build("customsearch","v1",developerKey=api_key)
    res = s.cse().list(
        q=query,
        cx=engine_key
    ).execute()
    return res['items']


if __name__ == "__main__":
    # First parse and validate arguments
    if(len(sys.argv) != 5):
        print(f"Usage: {sys.argv[0]} <google api key> <google engine id> <r> <t> <q> <k>")
    
    client_key = sys.argv[1]
    engine_key = sys.argv[2]
    relation = sys.argv[3]
    threshold = sys.argv[4]
    query = sys.argv[5]
    num_tuples = sys.argv[6]
    is_complete = False
   

    print("Parameters:")
    print(f"Client Key = {client_key}")
    print(f"Engine Key = {engine_key}")
    print(f"Relation      = {relation}")
    print(f"Threshold  = {threshold}")
    print(f"Query  = {query}")
    print(f"# of Tuples = {num_tuples}")
    print("Google Search Results:")
    print("======================")


    while not (is_complete):
       

