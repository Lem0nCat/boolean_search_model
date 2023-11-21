import wikipedia
import os


# Кравлер, который сохраняет содержание страниц википедии
def save_wikipedia_content(topic, count = 100, lang = 'ru', dir = 'texts'):
    wikipedia.set_lang(lang)

    # Поиск названий страниц схожих с термином
    search_result = wikipedia.search(topic, results=count)

    # Цикл проходит по всем названиям
    for i in range(len(search_result)):
        # Получение страницы из википедии
        page = wikipedia.page(search_result[i])
        # Сохранение статей в текстовый файл
        with open(f'{dir}/{i+1}.txt', 'w', encoding='utf-8') as file:
            file.write(page.content)

    print(f"{count} articles on '{topic}' have been saved")

# Удаление всех txt файлов, внутри папки dir
def delete_all_files(dir = 'texts'):
    filelist = [ f for f in os.listdir(dir) if f.endswith(".txt") ]
    for f in filelist:
        os.remove(os.path.join(dir, f))

# Удаляем все файлы внутри папки texts и скачиваем тексты по теме
delete_all_files()
save_wikipedia_content("Games")