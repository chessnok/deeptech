from data_work_func import *
from sentence_transformers import SentenceTransformer

# Загружаем модель для создания embedding-векторов
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# считаем данные с файла
with open('md_data/data.md') as f:
    text = []
    full_text = []
    # удалим пунктуацию и пустые строки
    for i in f:
        full_text.append(i)
        i=i.replace('\n', '')
        i=remove_punctuation(i)
        if len(i.strip()) != 0:
            text.append(i)


categories = [i.split('\t')[0] for i in text[6:93]]
# используем функции из файла data_work_func
real_categories = split_into_categories(categories)
# пользователь вводит вопрос и происходит поиск лучшей категории
question = input()
best_option = find_best_cos_sim(question, real_categories, model)
# получение текста документации для категории
find_context(best_option.lower(), full_text)

