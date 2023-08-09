import os
from dotenv import load_dotenv

from itertools import product

import csv
import tempfile
from tempfile import _TemporaryFileWrapper
import json
import random

from tqdm import tqdm
import timeit
import datetime

from parrot import Parrot
import nltk
from nltk.tag import PerceptronTagger
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize

import traceback

start = timeit.default_timer()
load_dotenv()
PARENT_DIR = os.environ.get("PARENT_DIR")

print("Loading NLP Tools...")
parrot = Parrot(model_tag="prithivida/parrot_paraphraser_on_T5", use_gpu=False) 

resources = ["tokenizers/punkt", "corpora/words", "taggers/averaged_perceptron_tagger", "corpora/wordnet", "chunkers/maxent_ne_chunker"]
for dep in resources:
    try:
        print(f"Resource '{dep.split('/')[1]}' has been downloaded")
    except:
        print(f"Resource '{dep.split('/')[1]}' has not been downloaded")
        print(f"Downloading '{dep.split('/')[1]}'")
        nltk.download(dep.split('/')[1])

pt = PerceptronTagger(load=True)
n_data = 0
data = None

print("Loading data from CSV file...", end="")
with open(PARENT_DIR + "src/data/base_data.csv", 'r') as file:
    data = list(csv.reader(file))
    random.shuffle(data)
print("Done")

state = None

tmp_files = os.listdir(PARENT_DIR+"src/temp/")
tmp_file = None

if not tmp_files:
    print("Creating Temporary File...", end="")
    tmp_file = tempfile.NamedTemporaryFile(mode="w+", dir=PARENT_DIR+"src/temp/", delete=False)
    tmp_file:_TemporaryFileWrapper
    print("Done")
else:
    print("Restoring Temporary File...", end="")
    temp = None
    with open(PARENT_DIR+"src/temp/"+tmp_files[0], "r") as f:
        temp = f.read()

    tmp_file = tempfile.NamedTemporaryFile(mode="w+", dir=PARENT_DIR+"src/temp/", delete=False)
    tmp_file:_TemporaryFileWrapper
    try:
        tmp_file.truncate()
        tmp_file.seek(0)
        tmp_file.write(temp)
        tmp_file.seek(0)
    finally:
        os.remove(PARENT_DIR+"src/temp/"+tmp_files[0])
    print("Done")

try:
    state = json.loads(tmp_file.read())
    state["row"] = int(state["row"])
except:
    state = {
        "row" : 0,
        "data" : [],
    }

data = list(data)[state["row"]+1:]

for i, val1 in enumerate(tqdm(data, desc="Questions Paraphrased", unit="row", disable=False)):
    original, answer = val1
    state["row"] = i

    # sentence augmentation
    parrot_augment = parrot.augment(input_phrase=original) or []
    if parrot_augment:
        parrot_augment = [p for p, _ in parrot_augment]
        
        for j, question in enumerate(parrot_augment):
            question:str
            aug_split = question.split(" ") 
            ori_split = original.split(" ")

            for k, word in enumerate(ori_split):
                if k == 0:
                    if [w.lower() for w in ori_split[::-1]].index(word.lower()) != 0:
                        aug_split[0] = word.capitalize()
                        continue
                
                aug_split = list(map(lambda w: w.lower().replace(word.lower(), word) if word.lower() in w.lower() else w, aug_split))
            parrot_augment[j] = " ".join(aug_split)

    # word-by-word augmentation
    pt_tokens = word_tokenize(original)
    pt_tags = pt.tag(pt_tokens)
    
    wordnet_augment = []
    pos_synonyms = {}
    corpus_to_wordnet_tags = {"NN": "n","NNS": "n","NNP": "n","NNPS": "n","JJ": "a","JJR": "a","JJS": "a","RB": "r","RBR": "r","RBS": "r","VB": "v","VBD": "v","VBG": "v","VBN": "v","VBP": "v","VBZ": "v",}
    sp_words = ["a","an","the","this","that","these","those","some","any","I","you","he","she","it","we","they","me","you","him","her","it","us","them","mine","yours","his","hers","its","ours","theirs","in","on","at","to","from","with","by","of","for","about","between","among","and","but","or","nor","yet","so","is","are","do","does","doing","done","did","be","being","been"]
    kw_words = ["Tech Centre","Swimming Pool","Staffroom","Science Research Centre","SALT Centre","Kuo Chuan Museum","Kong Chian Library","Kong Chian Admin Centre","Kah Kee Hall","International School","Gymnasium","EP3","Drama Centre","Clocktower","Canteen","Boarding School","Auditorium","LT4","LT3","LT2","LT1","Block D","Block C","Block B","Block A","HCI","Hwa Chong","Orientator"]
    
    tmp_words = []
    for kw in kw_words:
        words = kw.split(" ")
        for word in words:
            tmp_words.append(word)
    kw_words = [*set(tmp_words)]

    for j, val2 in enumerate(pt_tags):
        word, pt_tag = val2 
        wn_tag = corpus_to_wordnet_tags[pt_tag] if pt_tag in corpus_to_wordnet_tags.keys() else None
        
        if wn_tag == None or word in sp_words or word in kw_words:
            continue
        
        syn = [s.lemma_names() for s in wn.synsets(lemma=word, pos=wn_tag)]
        syn = [[l.replace("_", " ") for l in s if l != word] for s in syn]
        syn = list(filter(lambda v: word not in v, syn))

        tmp_syn = []
        for s in syn:
            if s not in tmp_syn:
                tmp_syn.append(s)

        syn = list(filter(lambda v: v, tmp_syn))
        
        pos_synonyms[j] = syn

    if not pos_synonyms:
        continue

    for k in pos_synonyms.keys():
        pos_synonyms[k] = [i for s in pos_synonyms[k] for i in s]
    
    tmp_lst = []

    for k, lst in pos_synonyms.items():
        t = []
        for v in lst:
            t.append((k, v))
        tmp_lst.append(t)
    
    combinations = [*product(*tmp_lst)]

    for comb in combinations:
        split = [w for w, _ in pt_tags]

        for k, v in comb:
            try:
                split[k] = v
            except:
                traceback.print_exc()
                continue
            augment = " ".join(split)
            wordnet_augment.append(augment)

    augment_lst = parrot_augment + wordnet_augment
    random.shuffle(augment_lst)
    augment_lst = augment_lst[:3000] if len(augment_lst) > 3000 else augment_lst

    state["data"] += [(original, (augment, answer)) for augment in augment_lst]
    n_data += len(augment_lst)

    try:
        tmp_file.truncate()
        tmp_file.seek(0)
        tmp_file.write(json.dumps(state, indent=2)) 
        tmp_file.seek(0)
    except:
        print("Failed to save data")
        traceback.print_exc()

    if (not (state["row"]+1) % 10 and state["row"] > 0) or state["row"]+1 == len(data):
        with open(PARENT_DIR + "src/data/augmented_data.csv", "a+") as file:
            file.seek(0)
            reader = list(csv.reader(file))
            augment_data = [a for _, a in state["data"]]
            if not reader:
                augment_data.insert(0, ("Question", "Answer"))
            
            file.seek(2)
            writer = csv.writer(file)
            writer.writerows([*filter(lambda v: v, augment_data)])
        try:
            tmp_file.seek(0)
            tmp_file.truncate()
            tmp_file.seek(0)
        except:
            print("Failed to clear temporary file")
            traceback.print_exc()
        state["data"] = []
        # break
    
    if n_data > 250000:
        print(n_data)
        break

end = timeit.default_timer()
print("\n== Data Augmentation Completed ==")
print(f"Time elapsed : {str(datetime.timedelta(seconds=round(end-start, 5)))}")
print(f"No. rows of data added : {n_data} rows")