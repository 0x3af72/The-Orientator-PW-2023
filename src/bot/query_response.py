import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

import sqlite3
import json

con = sqlite3.connect("conversation_history.db")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS dialogpt_conversations (user_id TEXT, chat_json TEXT)")
con.commit()
con.close()

print("Creating tokeniser...")
dialogpt_tokeniser = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")

print("Creating model...")
dialogpt_model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")
print("Done!")

def query_response(query, user_id):

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
    dialogpt_input_tokens = dialogpt_tokeniser.encode(f"{dialogpt_tokeniser.eos_token}".join(dialogpt_history) + dialogpt_tokeniser.eos_token, return_tensors='pt') 

    # generate response through top_k and top_p sampling    
    dialogpt_response_tokens = dialogpt_model.generate(
            dialogpt_input_tokens,
            max_length = 1000,
            do_sample = True,
            top_k = 100,
            top_p = 0.90, 
            temperature = 0.70,
            repetition_penalty=1.3
        )
    
    # decode response
    dialogpt_response_text = dialogpt_tokeniser.decode(dialogpt_response_tokens[:, dialogpt_input_tokens.shape[-1]:][0], skip_special_tokens=True)
    print(f"""
QUERY: {query}
USER ID: {user_id}
DIALOGPT RESPONSE: {dialogpt_response_text}
""")

    # add to history
    dialogpt_history.append(dialogpt_response_text)

    # limiting input tokens to 7 (including input)
    dialogpt_history = dialogpt_history[-6:]

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
    print(query_response("how was your day", "jeff"))