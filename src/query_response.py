import torch
from transformers import pipeline, Conversation

import sqlite3
import json

con = sqlite3.connect("conversation_history.db")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS conversations (user_id TEXT, chat_json TEXT)")
con.commit()
con.close()

print("Creating pipeline...")
generator = pipeline("conversational", model="microsoft/DialoGPT-large")

def query_response(query, user_id):

    # get database cursor
    con = sqlite3.connect("conversation_history.db") # NOTE: not sure if we should keep connecting
    cur = con.cursor()

    # load conversation history of this user
    cur.execute("SELECT * FROM conversations WHERE user_id=?", (user_id, ))
    rows = cur.fetchall()
    
    # initialize conversation history data
    if rows:
        user_inputs, responses = json.loads(rows[0][1])
    else: # nothing yet
        user_inputs = []
        responses = []
    user_inputs.append(query)

    # load conversation history into a conversation object
    convo = Conversation()
    for i in range(len(responses)): # NOTE: dont use len(user_inputs) because its 1 more than responses
        convo.add_user_input(user_inputs[i])
        convo.append_response(responses[i])
        convo.mark_processed()
    convo.add_user_input(user_inputs[-1])

    # get response
    new_response = generator(Conversation(query), max_length=100).generated_responses[-1]
    responses.append(new_response)

    # add new conversation record into db, close connection
    new_json = json.dumps([user_inputs, responses])
    if not rows:
        cur.execute("INSERT INTO conversations(user_id, chat_json) VALUES (?, ?)", (user_id, new_json))
    else:
        cur.execute("UPDATE conversations SET chat_json=? WHERE user_id=?", (new_json, user_id))
    con.commit()
    con.close()

    # return response
    return new_response

if __name__ == "__main__":

    # test query response
    print(query_response("third message", "jeff"))