import torch
from transformers import pipeline, Conversation

import sqlite3

con = sqlite3.connect("conversation_history.db")
# con.execute("CREATE TABLE ") # THIS IS NOT DONE EITHER

generator = pipeline("conversational", model="microsoft/DialoGPT-large")

def query_response(query, user_id):
    # load conversation history and then add into conversation object and then add latest query
    convo = Conversation()
    # convo.add_user_input(input)
    # convo.append_response(bot response that we loaded)
    # convo.mark_processed()
    # thats for each interaction
    # then after that add user input the latest one
    return generator(Conversation(query), max_length=100)