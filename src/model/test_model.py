from transformers import AutoTokenizer, AutoModelForCausalLM

from dotenv import load_dotenv
import os

load_dotenv()

PARENT_DIR = os.environ.get("PARENT_DIR")

checkpoint = PARENT_DIR + "models/test-model/final" # "microsoft/DialoGPT-small"

print("Creating tokeniser...", end="")
tokeniser = AutoTokenizer.from_pretrained(checkpoint)
print("Done")

print("Creating model...", end="")
model = AutoModelForCausalLM.from_pretrained(checkpoint)
print("Done")

tokeniser.pad_token = tokeniser.eos_token
tokeniser.pad_token_id = tokeniser.eos_token_id

chat_history = []

for i in range(10):
    user_input = input(">> User : ")
    chat_history.append(user_input)
    input_tokens = tokeniser.encode(
        f"{tokeniser.eos_token}".join(chat_history[:3]) + tokeniser.eos_token, 
        padding=True, 
        truncation=True, 
        return_tensors="pt")

    response_tokens = model.generate(
            input_tokens,
            max_length = 1000,
            do_sample = True,
            top_k = 10,
            top_p = 0.90, 
            temperature = 0.90,
            # repetition_penalty=1.1,
            pad_token_id=tokeniser.eos_token_id
        )
    
    print(f">> DialoGPT : {tokeniser.decode(response_tokens[:, input_tokens.shape[-1]:][0], skip_special_tokens=True)}")