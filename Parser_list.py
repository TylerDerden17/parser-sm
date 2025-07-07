import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
import csv

def clean_filename_part(text: str) -> str:
    if not text:
        return ""
    return re.sub(r'[\\/*?:"<>|]', "", text.strip())

def convert_to_mobile_link(href: str) -> str:
    # Преобразует /company/.../123456.php в /mobile/topic/123456/
    match = re.search(r'/(\d+)\.php', href)
    if match:
        article_id = match.group(1)
        return f"https://smart-lab.ru/mobile/topic/{article_id}/"
    return href  # fallback

def parse():
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

    for elem in content.find_all(["h3", "p"]):
        if elem.name == "h3":
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

                title_guess = text.replace("Текст", "").replace("Видео", "").strip(" .•:-\u00A0")

                if not title_guess:
                    title_guess = re.sub(r'\s+', ' ', raw_text)
                    parts = title_guess.split('.')
                    title_guess = parts[1].strip() if len(parts) > 1 else "Без названия"

                article_number += 1

                result.append({
                    "Часть": clean_filename_part(current_chapter),
                    "Раздел": clean_filename_part(current_section),
                    "№": article_number,
                    "Название": clean_filename_part(title_guess),
                    "Тип": "Текст",
                    "Ссылка": convert_to_mobile_link(href)
                })

    return result

def save_to_csv(data, filename="osengine_articles.csv"):
    keys = ["Часть", "Раздел", "№", "Название", "Тип", "Ссылка"]
    data_sorted = sorted(data, key=lambda x: (x["Часть"], x["Раздел"], x["№"]))

    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data_sorted)

    print(f"Сохранено: {filename}")

