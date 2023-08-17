from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers.utils import logging

import sqlite3
import json

from dotenv import load_dotenv
import os

logging.set_verbosity_error()

load_dotenv()

PARENT_DIR = os.environ.get("PARENT_DIR")

con = sqlite3.connect("conversation_history.db")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS dialogpt_conversations (user_id TEXT, chat_json TEXT)")
con.commit()
con.close()

checkpoint = PARENT_DIR + "models/model-132744/final"

print("Loading DialoGPT tokeniser...", end="")
dialogpt_tokeniser = AutoTokenizer.from_pretrained(checkpoint)
print("Done")

print("Loading DialoGPT model...", end="")
dialogpt_model = AutoModelForCausalLM.from_pretrained(checkpoint)
print("Done")

dialogpt_tokeniser.pad_token = dialogpt_tokeniser.eos_token
dialogpt_tokeniser.pad_token_id = dialogpt_tokeniser.eos_token_id

def query_response(query: str, user_id: int):
    query = query.capitalize()

    if query[-1] != "?":
        query += "?"

    # get database cursor
    con = sqlite3.connect("conversation_history.db") # NOTE: not sure if we should keep connecting
    cur = con.cursor()

    # load conversation history of this user
    cur.execute("SELECT * FROM dialogpt_conversations WHERE user_id=?", (user_id, ))
    dialogpt_rows = cur.fetchall()
     
    # initialize conversation history data
    if dialogpt_rows:
        dialogpt_history = json.loads(dialogpt_rows[0][1])
    else: # nothing yet
        dialogpt_history = []
        
    dialogpt_history.append(query)

    # tokenise chat history and query
    dialogpt_input_tokens = dialogpt_tokeniser.encode(
        # text = f"{dialogpt_tokeniser.eos_token}".join(dialogpt_history[-3:]) + dialogpt_tokeniser.eos_token, 
        text = query + dialogpt_tokeniser.eos_token,
        padding = True, 
        truncation = True, 
        return_tensors = "pt")

    # generate response through top_k and top_p sampling    
    dialogpt_response_tokens = dialogpt_model.generate(
            dialogpt_input_tokens,
            max_length = 200,
            do_sample = True,
            top_k = 10,
            top_p = 0.75, 
            temperature = 0.50
        )

    # decode response
    dialogpt_response_text = dialogpt_tokeniser.decode(dialogpt_response_tokens[:, dialogpt_input_tokens.shape[-1]:][0], skip_special_tokens=True)
    print(f"QUERY: {query} \nUSER ID: {user_id} \nRESPONSE: {' '.join(dialogpt_response_text.split(' ')[:len(query.split(' '))*25])}")

    # add to history
    dialogpt_history.append(dialogpt_response_text)

    # add conversation record into db, close connection
    dialogpt_json = json.dumps(dialogpt_history)

    if not dialogpt_rows:
        cur.execute("INSERT INTO dialogpt_conversations(user_id, chat_json) VALUES (?, ?)", (user_id, dialogpt_json))
    else:
        cur.execute("UPDATE dialogpt_conversations SET chat_json=? WHERE user_id=?", (dialogpt_json, user_id))

    con.commit()
    con.close()

    # return response
    return dialogpt_response_text

if __name__ == "__main__":
    # test query response
    query_response("who are you", "jeff")