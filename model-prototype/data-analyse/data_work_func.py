import string
from sentence_transformers import util
import numpy as np

# уберает всю пунктуацию с помощью библиотеки string 
def remove_punctuation(text):
    translator = str.maketrans('', '', string.punctuation) 
    return text.translate(translator)

# Загрузите оглавление, получите разбиение по категориям, подходящее для дальнейшего использования
def split_into_categories(categories):
    cat = []
    place = '1'
    work_path = ''
    for i in categories:
        # если у категории есть продолжение, прыгаем глубже
        if place+'1' == i.split()[0]:
            work_path += '. '+' '.join(i.split()[1:]) # обновляем название категории
            place += '1' # обновляем номер категории
        # достигли финальной точки категории, но это не самая первая категория (у первой категории всегда есть подкатегория, поэтому рассматривается отдельно)
        elif len(i.split()[0])>1:
            cat.append(work_path[2:]) # сохраняем полное название категории
            work_path = '. '.join(work_path.split('. ')[:len(place)])+'. '+' '.join(i.split()[1:]) # обновляем название категории
            place = i.split()[0] # обновляем номер категории
        else:
            cat.append(work_path[2:]) # сохраняем полное название категории
            work_path = '. '+' '.join(i.split()[1:]) # обновляем название категории
            place = i.split()[0] # обновляем номер категории
    return cat

# поиск описания категории в документации. На вход подается категория и полная документация
def find_context(title, data):
    ind = 0
    # обнаружение индекса категории
    for i in range(len(data)):
        if ('<a name="_toc' in data[i].lower()) and (title in data[i].lower()):
            ind = i+1
    context = ''
    # поиск описания категории
    for i in data[ind:]:
        if '<a name="_toc' in i:
            # если началась другая категория заканчиваем описание
            break
        context += i+'\n'
    return context


def cosine_similarity(text1, text2, model):
    # Преобразуем текст в embedding-векторы
    embedding1 = model.encode(text1, convert_to_tensor=True)
    embedding2 = model.encode(text2, convert_to_tensor=True)
    
    # Вычисляем косинусное сходство
    cosine_sim = util.pytorch_cos_sim(embedding1, embedding2)
    
    return cosine_sim.item()  # Возвращаем значение сходства как float

def find_best_cos_sim(question, text):
    cos_sim = []
    # считаем косинусные сходства для категорий и вопроса
    for i in text:
        cos_sim.append(cosine_similarity(i, question))
    # выбираем категорию с наибольшим косинусным сходством
    return text[cos_sim.index(max(cos_sim))].split('. ')[-1]
