import csv

from dotenv import load_dotenv
import os

load_dotenv()
PARENT_DIR = os.environ.get("PARENT_DIR")

with open(PARENT_DIR + "/data.csv", 'r') as file:
    csvreader = csv.reader(file)
    question = []
    answer = []
    for q, a in list(csvreader)[1:]:
        question.append(q)
        answer.append(a)

