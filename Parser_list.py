import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
import csv

def clean_filename_part(text: str) -> str:
    """Очищает текст от недопустимых символов для имени файла"""
    if not text:
        return ""
    return re.sub(r'[\\/*?:"<>|]', "", text.strip())

def convert_to_mobile_link(href: str) -> str:
    """Преобразует /company/.../123456.php в /mobile/topic/123456/"""
    match = re.search(r'/(\d+)\.php', href)
    if match:
        article_id = match.group(1)
        return f"https://smart-lab.ru/mobile/topic/{article_id}/"
    return href  # fallback

def display_added_articles(added_articles, current_chapter, current_section):
    """Функция для отображения добавленных статей в текущей части"""
    if added_articles:
        print(f"\nДобавленные статьи в части: {current_chapter}")
        print(f"Раздел: {current_section}")
        for article in added_articles:
            print(f"№{article['№']} - {article['Название']} ({article['Ссылка']})")
    else:
        print(f"\nВ части {current_chapter} нет добавленных статей.")

    # Ожидаем ввод пользователя, чтобы продолжить
    input("\nНажмите Enter, чтобы продолжить...")

def parse():
    """Функция для парсинга страницы и сбора данных о статьях"""
    ua = UserAgent().chrome
    url = 'https://smart-lab.ru/mobile/topic/1024149/'
    page = requests.get(url, headers={'User-Agent': ua})
    print("Ответ сервера:", page.status_code)

    if page.status_code != 200:
        print("Ошибка: Невозможно получить страницу.")
        return []

    soup = BeautifulSoup(page.text, "html.parser")
    content = soup.select_one("div.post-card__text")

    if content is None:
        print("Ошибка: Не найден блок с текстом статьи.")
        return []

    current_chapter = ""
    current_section = ""
    article_number = 0
    result = []
    added_articles = []
    added_links = set()  # Множество для уникальных ссылок

    for elem in content.find_all(["h3", "p"]):
        if elem.name == "h3":
            # Проверяем на смену части и выводим добавленные статьи
            if current_chapter != "" and current_chapter != elem.get_text(strip=True):
                display_added_articles(added_articles, current_chapter, current_section)
                added_articles = []  # Очищаем список добавленных статей для новой части

            current_chapter = elem.get_text(strip=True)
            if "Часть" in current_chapter or "Коннекторы" in current_chapter:
                current_section = ""
            if elem.find("em"):
                current_section = elem.get_text(strip=True)

        elif elem.name == "p":
            raw_text = elem.get_text(" ", strip=True)
            links = elem.find_all('a')
            if not links:
                continue

            for link in links:
                href = link.get('href')
                text = link.get_text(strip=True)

                if not href or "видео" in text.lower():
                    continue

                # Проверяем на дублирующиеся ссылки
                mobile_link = convert_to_mobile_link(href)
                if mobile_link in added_links:
                    continue
                added_links.add(mobile_link)

                # Если название статьи выглядит как "Текст.", убираем точку
                if text.lower() == "текст." or text.lower() == "видео.":
                    text = text[:-1].strip()

                # Если текст ссылки пустой, то пытаемся извлечь название из самого контента
                if not text:
                    text = raw_text.split('.')[0].strip()

                # Проверяем, если название все еще пустое
                if not text:
                    text = "Без названия"

                article_number += 1

                # Выводим статью для подтверждения
                print(f"\nСтатья: {text}")
                print(f"Ссылка: {mobile_link}")
                user_input = input("Добавить статью? (y/n): ").lower()

                if user_input == "y":
                    article_data = {
                        "Часть": clean_filename_part(current_chapter),
                        "Раздел": clean_filename_part(current_section),
                        "№": article_number,
                        "Название": clean_filename_part(text),
                        "Тип": "Текст",
                        "Ссылка": mobile_link
                    }
                    result.append(article_data)
                    added_articles.append(article_data)  # Добавляем статью в список

    # В конце последней части отображаем добавленные статьи
    display_added_articles(added_articles, current_chapter, current_section)

    return result

def save_to_csv(data, filename="osengine_articles.csv"):
    """Сохраняет статьи в CSV файл"""
    keys = ["Часть", "Раздел", "№", "Название", "Тип", "Ссылка"]
    data_sorted = sorted(data, key=lambda x: (x["Часть"], x["Раздел"], x["№"]))

    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data_sorted)

    print(f"Сохранено: {filename}")

def display_csv_format(data):
    """Выводит данные в формате CSV, как в файле"""
    print("Часть, Раздел, №, Название, Тип, Ссылка")
    for article in data:
        print(f"{article['Часть']}, {article['Раздел']}, {article['№']}, {article['Название']}, {article['Тип']}, {article['Ссылка']}")
