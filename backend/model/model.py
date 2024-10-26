from model.data_processing.docs_processing import *
from sentence_transformers import SentenceTransformer

# Загружаем модель для создания embedding-векторов
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
from transformers import AutoTokenizer, pipeline
import torch

# Модель
model_generate = "recoilme/Gemma-2-Ataraxy-Gemmasutra-9B-slerp"
# Инициализация токенайзера
tokenizer = AutoTokenizer.from_pretrained(model_generate)


# Инициализация пайплайна
pipeline_gen = pipeline(
    "text-generation",
    model=model_generate,
    torch_dtype=torch.float16,
    device=0,
)



# считаем данные с файла
with open('./data/data.md') as f:
    text = []
    full_text = []
    for i in f:
        full_text.append(i)
        i=i.replace('\n', '')
        i=remove_punctuation(i)
        if len(i.strip()) != 0:
            text.append(i)


categories = [i.split('\t')[0] for i in text[6:93]]
# используем функции из файла from docs_processing 
real_categories = split_into_categories(categories)
# пользователь вводит вопрос и происходит поиск лучшей категории

def answer_generate(question, context, history):
    # Сообщения
    messages = history + [
        {"role": "user", "content": f"Привет"},
        {"role": "assistant", "content": f"{context}"},
        {"role": "user", "content": f"{question}"}
    ]

    # Применяем шаблон для подготовки сообщений
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    outputs = pipeline_gen(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)
    return outputs[0]["generated_text"]


def response(question, history):
    best_option = find_best_cos_sim(question, real_categories, model)
    context = find_context(best_option[0].lower(), full_text)
    return answer_generate(question, context, history)
