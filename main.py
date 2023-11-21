import os
import spacy
from spacy.lang.ru.stop_words import STOP_WORDS


# Загружаем модель для русского языка
nlp = spacy.load("ru_core_news_sm")

# Функция для считывания текстов из файлов в список
# Конечный результат выглядит как ['текст1', 'текст2', ...]
def get_texts(folder_path='texts'):
    files = os.listdir(folder_path)
    texts = []
 
    for i in range(len(files)):
        file_path = os.path.join(folder_path, f'{i+1}.txt')

        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    texts.append(content)
            except Exception as e:
                print(f'Ошибка при чтении файла {i+1}.txt: {e}')
    
    return texts

# Функция для лемматизации текстов и получения списка списков лемматизированных слов
# Конечный результат выглядит как [['текст1_слово1', 'текст1_слово2', ...], ['текст2_слово1', ...], ...]
def lemmatize(texts):
    texts_lemmas = []

    for i in range(len(texts)):
        # Обработка текста
        doc = nlp(texts[i])

        # Лемматизация
        lemmas = [token.lemma_ for token in doc if token.is_alpha and token.lemma_ not in STOP_WORDS]
        texts_lemmas.append(lemmas)
    
    return texts_lemmas

# Функция для индексирования лемматизированных слов по их документам из вики
# Конечный результат выглядит как [('слово', index), ...]
def index_construction(texts_lemmas):
    indexed_lemmas = []
    for text_index in range(len(texts_lemmas)):
        for lemma in texts_lemmas[text_index]:
            indexed_lemmas.append((lemma, text_index + 1))
    
    return indexed_lemmas

# Функция, которая группирует список лемматизированных слов и возвращает
# Новый список вида [{'term': 'слово', 'finds': [(docID, term_count), ...]}, {...}, {...}, ...]
def group_indexed_lemmas(indexed_lemmas):
    # Сортировка по первому элементу (по "слову")
    sorted_indexed_lemmas = sorted(indexed_lemmas, key=lambda x: x[0])

    result_list = []

    # Цикл, который проходит по списку и создает элементы для нового списка
    current_term, current_doc = None, None
    for term, doc_id in sorted_indexed_lemmas:
        # Если термин и документ такие же, увеличиваем счетчик
        if term == current_term and doc_id == current_doc:
            result_list[-1]['finds'][doc_id] += 1
        # Если термин такой же, но изменился номер документа
        elif term == current_term and doc_id != current_doc:
            result_list[-1]['finds'][doc_id] = 1
            current_doc = doc_id
        else:   # Если изменился термин
            result_list.append({'term': term, 'finds': {doc_id: 1}})
            current_term, current_doc = term, doc_id
    
    return result_list

# Функция булевого поиска
# Возвращает либо список документов вида [1, 2, 4, 6, ...]
# Либо [(7, 6), (17, 6), (10, 5), (2, 3), (1, 1), ...] 
# где [(индекс документа, количество повторений этого слова в документе), ...]
def boolean_search(request, grouped_lemmas, texts_count):
    request = request.lower()
    # Проверка на префикс "NOT"
    if request.startswith("not "):
        is_not_query = True
        keyword = request[4:]
    else:
        is_not_query = False
        keyword = request

    # Лемматизация запроса
    doc = nlp(keyword)
    keyword = doc[0].lemma_
    
    finds_dict = {}
    # Поиск элемента с нужным термином
    for item in grouped_lemmas:
        if item['term'] == keyword:
            # Найден элемент с искомым термином, выводим список finds
            finds_dict = item['finds']
            break
    else:   # Если термин не найден
        if is_not_query:    # Если стоит префикс NOT, то можно вернуть все документы
            return [i for i in range(1, texts_count + 1)]
        else:
            print(f"Не найдено совпадений с термином '{keyword}'")
            return None

    # Сортировка по количеству повторений
    finds_list = list(finds_dict.items())
    sorted_finds = sorted(finds_list, key=lambda x: x[1], reverse=True)

    # Если у нас стоит префикс NOT, то возвращает все документы, которых нет в найденном списке
    if is_not_query:
        texts = [i for i in range(1, texts_count + 1)]  # Список всех имеющихся документов
        word_docs = [x for x in texts if all(x != find[0] for find in sorted_finds)]
        return word_docs
    else:
        return sorted_finds

# Функция понятного вывода
def output(result_list):
    try:
        if all(isinstance(item, tuple) and len(item) == 2 for item in result_list):
            # Обработка списка вида [(x, y), ...]
            for tuple_element in result_list:
                first_element, second_element = tuple_element
                print(f"{first_element}.txt, {second_element}")
        else:   # Обработка списка вида [x, ...] 
            for element in result_list:
                print(f"{element}.txt")
    except:
        pass


texts = get_texts()

texts_lemmas = lemmatize(texts)

indexed_lemmas = index_construction(texts_lemmas)

grouped_lemmas = group_indexed_lemmas(indexed_lemmas)

request = "not США"
result_list = boolean_search(request, grouped_lemmas, len(texts))

# print(grouped_lemmas)
# print("\n\n")
output(result_list)


# {'term': 'сша', 'finds': {1: 2, 9: 2, 10: 2, 11: 4, 13: 4, 18: 3, 20: 2, 21: 1, 29: 17, 32: 1, 33: 3, 36: 3, 41: 3, 49: 2, 52: 11, 53: 1, 54: 1, 55: 3, 56: 14, 57: 1, 59: 1, 64: 6, 65: 2, 66: 5, 68: 1, 69: 1, 71: 1, 75: 4, 77: 1, 79: 11, 83: 1, 86: 1, 87: 1, 94: 1, 96: 6, 97: 1, 100: 6}}