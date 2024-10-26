import sys
import requests
from pymystem3 import Mystem

def tag_mystem(text, mapping=None, postags=True):
    """
    Обрабатывает текст, лемматизирует его и размечает по частям речи.
    
    :param text: Входной текст (строка)
    :param mapping: Словарь для преобразования тегов (по умолчанию None)
    :param postags: Флаг, указывающий, нужно ли возвращать теги (по умолчанию True)
    :return: Список лемм с частями речи
    """
    m = Mystem()
    
    processed = m.analyze(text)
    tagged = []
    
    for w in processed:
        try:
            lemma = w["analysis"][0]["lex"].lower().strip()
            pos = w["analysis"][0]["gr"].split(",")[0]
            pos = pos.split("=")[0].strip()
            if mapping:
                if pos in mapping:
                    pos = mapping[pos]  # конвертация тегов
                else:
                    pos = "X"  # тег не найден
            tagged.append(lemma.lower() + "_" + pos)
        except KeyError:
            continue
        
    if not postags:
        tagged = [t.split("_")[0] for t in tagged]
    
    return tagged

def load_mapping(url):
    """
    Загружает таблицу преобразования частеречных тэгов Mystem в тэги UPoS.
    
    :param url: URL для загрузки маппинга
    :return: Словарь маппинга
    """
    mystem2upos = {}
    r = requests.get(url, stream=True)
    for pair in r.text.split("\n"):
        pair = pair.split()
        if len(pair) > 1:
            mystem2upos[pair[0]] = pair[1]
    return mystem2upos
