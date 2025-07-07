import os
import re
import requests
from bs4 import BeautifulSoup
import Parser
import Parser_list


def check_img_links_f():
    file_path = input("Введите путь к HTML файлу или URL для проверки ссылок на изображения: ").strip()

    if file_path.startswith("http"):
        try:
            response = requests.get(file_path)
            response.raise_for_status()
            html_content = response.text
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка при загрузке страницы: {e}")
            return
    else:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except Exception as e:
            print(f"❌ Ошибка при чтении файла: {e}")
            return

    soup = BeautifulSoup(html_content, "html.parser")
    post_content = soup.find("div", class_="post-card__text")

    if not post_content:
        print("⚠️ Не найден блок 'post-card__text'.")
        return

    img_tags = post_content.find_all("img")
    a_tags = post_content.find_all("a", class_="imgpreview")

    all_links = []

    # Добавляем ссылки из <img>
    for tag in img_tags:
        src = tag.get("src")
        if src:
            full_url = "https://smart-lab.ru" + src if not src.startswith("http") else src
            all_links.append(full_url)

    # Добавляем ссылки из <a href>
    for tag in a_tags:
        href = tag.get("href")
        if href:
            full_url = "https://smart-lab.ru" + href if not href.startswith("http") else href
            all_links.append(full_url)

    # Проверяем уникальные ссылки
    all_links = list(set(all_links))

    if not all_links:
        print("⚠️ Не найдено изображений.")
        return

    for link in all_links:
        try:
            response = requests.get(link)
            response.raise_for_status()
            print(f"✅ Изображение доступно: {link}")
        except Exception as e:
            print(f"❌ Ошибка при загрузке изображения {link}: {e}")


def display_menu():
    print("\nМеню:")
    print("1. Сохранить статью в DOCX")
    print("2. Спарсить статьи и сохранить в CSV")
    print("3. Просмотреть все статьи")
    print("4. Проверить изображения в HTML файле или URL")
    print("5. Выйти")


def save_article():
    url = input("Введите URL статьи для сохранения в DOCX: ").strip()
    try:
        Parser.save_article_to_docx(url)
        print("✅ Статья успешно сохранена.")
    except Exception as e:
        print(f"❌ Произошла ошибка при сохранении статьи: {e}")


def parse_and_save_articles():
    try:
        articles = Parser_list.parse()
        if articles:
            Parser_list.save_to_csv(articles)
            print("✅ Статьи сохранены в CSV:")
            for article in articles:
                print(article)
        else:
            print("⚠️ Не удалось найти статьи.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")


def display_all_articles():
    try:
        articles = Parser_list.parse()
        if articles:
            for article in articles:
                print(article)
        else:
            print("⚠️ Нет доступных статей.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")


def main():
    while True:
        display_menu()
        choice = input("Выберите действие (1–5): ").strip()

        if choice == "1":
            save_article()
        elif choice == "2":
            parse_and_save_articles()
        elif choice == "3":
            display_all_articles()
        elif choice == "4":
            check_img_links_f()
        elif choice == "5":
            print("👋 Выход...")
            break
        else:
            print("❗ Введите цифру от 1 до 5.")


if __name__ == "__main__":
    main()
