import string
from sentence_transformers import util
import numpy as np

def remove_punctuation(text):
    """
    Убирает пунктуацию текста
    
    :param text: Входной текст. 
    :return: Текст без знаков пунктуации. 
    """
    translator = str.maketrans('', '', string.punctuation) 
    return text.translate(translator)

def split_into_categories(categories):
    """
    Разбиение на категории при помощи оглавления.
    
    :param categories: Оглавление документации, считанное из формата Markdown
    :return: Список всех категорий по порядку. 
    """
    cat = []
    place = '1'
    step = 1
    work_path = ''
    for i in categories:
        # если у категории есть продолжение, прыгаем глубже
        if place+'1' == i.split()[0]:
            work_path += '. '+' '.join(i.split()[1:]) # обновляем название категории
            place += '1' # обновляем номер категории
            step += 1
        # достигли финальной точки категории, но это не самая первая категория (у первой категории всегда есть подкатегория, поэтому рассматривается отдельно)
        elif place[:-1]+str(int(place[-1])+1) == i.split()[0]:
            cat.append(work_path[2:]) # сохраняем полное название категории
            work_path = '. '.join(work_path.split('. ')[:step])+'. '+' '.join(i.split()[1:]) # обновляем название категории
            place = i.split()[0] # обновляем номер категории
        else:
            diff = len(place) - len(i.split()[0])
            if i.split()[0][-1] == 0:
                diff += 1
            elif place[-1] == 0:
                diff -= 1
            step -= diff
            cat.append(work_path[2:]) # сохраняем полное название категории
            work_path = '. '.join(work_path.split('. ')[:step])+'. '+' '.join(i.split()[1:])
            place = i.split()[0] # обновляем номер категории
            
    return cat


def find_context(title, data):
    """
    Поиск описания категории в документации.
    
    :param title: Категория, которую нужно найти
    :param data: Документация, считанная из формата Markdown
    :return: Текст описания категории
    """
    ind = 0
    # обнаружение индекса категории
    data_steps = list(title.split('. '))
    for step in data_steps:
        for i in range(ind, len(data)):
            if ('<a name="_toc' in data[i].lower()) and (step.lower() in data[i].lower()):
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
    """
    Расчет косинусного сходства
    
    :param text1, text2: Тексты для проверки.
    :param model: Модель эммбеддингов
    :return: Косинсное сходство в формате float
    """
    embedding1 = model.encode(text1, convert_to_tensor=True)
    embedding2 = model.encode(text2, convert_to_tensor=True)
    
    cosine_sim = util.pytorch_cos_sim(embedding1, embedding2)
    
    return cosine_sim.item() 

def find_best_cos_sim(question, text, model, top=5):
    """
    Расчет наибольшего косинусного сходства для вопроса и категорий
    
    :param question: Вопрос
    :param text: Список из категорий
    :return: Категория с наибольшим косинусным сходством с вопросом
    """
    text_info = [i.split('. ')[-1] for i in text]
    cos_sim = []
    for i in text_info:
        cos_sim.append(cosine_similarity(i, question, model))
    scs = sorted(cos_sim, reverse=True)
    top_n = []
    for i in scs[:top]:
        top_n.append(text[cos_sim.index(i)])
        text.pop(cos_sim.index(i))
        cos_sim.pop(cos_sim.index(i))
    return top_n
