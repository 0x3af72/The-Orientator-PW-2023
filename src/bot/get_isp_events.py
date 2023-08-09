import gensim.downloader as api
from nltk.tokenize import word_tokenize

import json

import os
from dotenv import load_dotenv

load_dotenv()
PARENT_DIR = os.environ.get("PARENT_DIR")

# Load the pre-trained Word2Vec model
print("Loading Word2Vec model...", end="")
word2vec_model = api.load("word2vec-google-news-300")
print("Done")

# Load event data
with open(PARENT_DIR + "src/data/isp_events.json", "r") as r:
    events = json.load(r)

def best_match(query, event_list, embedding_model):
    # Tokenize and lowercase the query
    query_tokens = word_tokenize(query.lower())
    best_match = None
    max_similarity = -1
    
    for event in event_list:
        event_name_tokens = word_tokenize(event.lower())
        similarity = embedding_model.n_similarity(query_tokens, event_name_tokens)
        
        if similarity > max_similarity:
            max_similarity = similarity
            best_match = event
    
    return best_match

def get_event(query):
    match = best_match(query, events, word2vec_model)
    if not match:
        return False
    return match, events[match]

if __name__ == "__main__":
    while True:
        query = input(">>> ")
        print(get_event(query))