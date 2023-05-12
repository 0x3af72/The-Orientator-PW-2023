'''
This is the module imported in the main code.
Here we generate the response for the user's query about HCI.
'''

from transformers import pipeline

def query_response(query, generator:pipeline):
    responses = [text["generated_text"] for text in generator(query, max_length=60, num_return_sequences=3)]
    print(responses)
    responses = [text.replace("\n\n", "\n") for text in responses]
    return "Responses Given : \n" + "\n\n\n".join(responses)

