import torch
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration, AutoModelForCausalLM, AutoTokenizer

import sqlite3
import json

con = sqlite3.connect("conversation_history.db")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS blenderbot_conversations (user_id TEXT, chat_json TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS dialogpt_conversations (user_id TEXT, chat_json TEXT)")
con.commit()
con.close()

print("Creating tokeniser...")
blender_tokeniser = BlenderbotTokenizer.from_pretrained("facebook/blenderbot-1B-distill")
dialogpt_tokeniser = AutoTokenizer.from_pretrained("microsoft/DialoGPT-large")

print("Creating model...")
blender_model = BlenderbotForConditionalGeneration.from_pretrained("facebook/blenderbot-1B-distill")
dialogpt_model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-large")
print("Done!")

def query_response(query, user_id):

    # get database cursor
    con = sqlite3.connect("conversation_history.db") # NOTE: not sure if we should keep connecting
    cur = con.cursor()

    # load conversation history of this user
    cur.execute("SELECT * FROM blenderbot_conversations WHERE user_id=?", (user_id, ))
    blender_rows = cur.fetchall()

    cur.execute("SELECT * FROM dialogpt_conversations WHERE user_id=?", (user_id, ))
    dialogpt_rows = cur.fetchall()
     
    # initialize conversation history data
    if blender_rows:
        blender_history = json.loads(blender_rows[0][1])
    else: # nothing yet
        blender_history = []

    if dialogpt_rows:
        dialogpt_history = json.loads(blender_rows[0][1])
    else: # nothing yet
        dialogpt_history = []
    
    blender_history.append(query)
    dialogpt_history.append(query)

    # tokenise chat history and query
    blender_input_tokens = blender_tokeniser(["\n".join(blender_history)], return_tensors='pt', truncation=True)
    dialogpt_input_tokens = dialogpt_tokeniser.encode(f"{dialogpt_tokeniser.eos_token}".join(dialogpt_history) + dialogpt_tokeniser.eos_token, return_tensors='pt') 

    # generate response through top_k and top_p sampling
    blender_response_tokens = blender_model.generate(
            **blender_input_tokens,
            max_length = 1000,
            do_sample = True,
            top_k = 100,
            top_p = 0.90, 
            temperature = 0.75,
            pad_token_id = blender_tokeniser.eos_token_id
        )
    
    dialogpt_response_tokens = dialogpt_model.generate(
            dialogpt_input_tokens,
            max_length = 1000,
            do_sample = True,
            top_k = 100,
            top_p = 0.90, 
            temperature = 0.75,
            pad_token_id = blender_tokeniser.eos_token_id
        )
    
    # decode response
    blender_response_text = blender_tokeniser.batch_decode(blender_response_tokens, skip_special_tokens=True)[0].strip()
    dialogpt_response_text = dialogpt_tokeniser.decode(dialogpt_response_tokens[:, dialogpt_input_tokens.shape[-1]:][0], skip_special_tokens=True)
    print(f"""
QUERY: {query}
USER ID: {user_id}
BLENDER RESPONSE: {blender_response_text}
DIALOGPT RESPONSE: {dialogpt_response_text}
""")

    # add to history
    blender_history.append(blender_response_text)
    dialogpt_history.append(dialogpt_response_text)

    # limiting input tokens to 7 (including input)
    blender_history = blender_history[-6:]
    dialogpt_history = dialogpt_history[-6:]

    # add conversation record into db, close connection
    blender_json = json.dumps(blender_history)
    dialogpt_json = json.dumps(dialogpt_history)
    
    if not blender_rows:
        cur.execute("INSERT INTO blenderbot_conversations(user_id, chat_json) VALUES (?, ?)", (user_id, blender_json))
    else:
        cur.execute("UPDATE blenderbot_conversations SET chat_json=? WHERE user_id=?", (blender_json, user_id))

    if not dialogpt_rows:
        cur.execute("INSERT INTO dialogpt_conversations(user_id, chat_json) VALUES (?, ?)", (user_id, dialogpt_json))
    else:
        cur.execute("UPDATE dialogpt_conversations SET chat_json=? WHERE user_id=?", (dialogpt_json, user_id))

    con.commit()
    con.close()

    # return response
    return f"BlenderBot 2.0 : {blender_response_text}\n\nDialoGPT : {dialogpt_response_text}"

if __name__ == "__main__":
    # test query response
    print(query_response("how was your day", "jeff"))