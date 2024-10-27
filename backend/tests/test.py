import requests
import json
from sentence_transformers import SentenceTransformer
import pandas as pd

from model.data_processing.docs_processing import cosine_similarity

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
url = "http://93.92.199.89:40886/new_conv"

headers = {
'Content-Type': 'application/json'
}

uuid=requests.request("POST", url, headers=headers).json()['uuid']

url = "http://93.92.199.89:40886/new_message"
data = pd.read_excel('data.xlsx')
questions = data['Вопросы']
answers = data['Ответы']
def get_multiple_answers(questions):
    model_answers = []
    for q in questions:
        payload = json.dumps({
            "conversation_id": uuid,
            "text": q
        })
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.status_code)
        print(response.json())
        model_answers.append(response.json()['text'])
    return model_answers
def calc_score(model_answers, answers):
    scores = []
    for i in range(len(model_answers)):
        scores.append(cosine_similarity(model_answers[i], answers[i], model))
    return sum(scores)/len(scores)

print(calc_score(get_multiple_answers(questions), answers))
