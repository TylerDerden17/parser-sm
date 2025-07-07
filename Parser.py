import os
import requests
from PIL import Image
from docx import Document
from docx.shared import Inches
from bs4 import BeautifulSoup

def download_image(img_url, img_path):
    try:
        img_data = requests.get(img_url)
        img_data.raise_for_status()  # Проверка на успешный ответ
        with open(img_path, 'wb') as handler:
            handler.write(img_data.content)
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при скачивании изображения {img_url}: {e}")


def convert_image_to_supported_format(img_path):
    """Конвертируем изображение в поддерживаемый формат (PNG, если это WEBP)."""
    if img_path.lower().endswith(".webp"):
        try:
            # Открываем изображение и конвертируем в PNG
            img = Image.open(img_path)
            img_path_new = img_path.replace(".webp", ".png")  # Преобразуем в PNG
            img.save(img_path_new, "PNG")
            os.remove(img_path)  # Удаляем оригинальное изображение в формате WEBP
            img_path = img_path_new  # Используем новый путь
            print(f"Изображение конвертировано в {img_path}")
        except Exception as e:
            print(f"Ошибка при конвертации изображения {img_path}: {e}")
    return img_path


def save_article_to_docx(url, filename):
    # Создаём документ
    doc = Document()

    # Получаем HTML-страницу
    page = requests.get(url)

    if page.status_code != 200:
        print("Ошибка: Не удалось загрузить страницу.")
        return

    soup = BeautifulSoup(page.text, "html.parser")

    # Заголовок статьи
    title = soup.select_one("div.post-card__title-wrap")
    if title:
        doc.add_heading(title.get_text(strip=True), level=1)

    # Текст статьи с картинками
    content = soup.select_one("div.post-card__text")

    if content:
        if not os.path.exists("images"):
            os.makedirs("images")

        # Проходим по каждому параграфу
        for p in content.find_all("p"):
            # Добавляем текст
            text = p.get_text()
            # Проверка на <strong> для жирного текста
            if p.find("strong"):
                text = f"**{text}**"
            # Проверка на <em> для курсива
            if p.find("em"):
                text = f"*{text}*"

            doc.add_paragraph(text)

            # Обрабатываем картинки
            img_tag = p.find("img")
            if img_tag and img_tag.get('src'):
                img_url = img_tag['src']

                # Если ссылка относительная, добавляем домен
                if not img_url.startswith("http"):
                    img_url = "https://smart-lab.ru" + img_url

                # Скачиваем картинку
                img_name = img_url.split("/")[-1]
                img_path = os.path.join("images", img_name)

                download_image(img_url, img_path)

                # Конвертируем изображение в поддерживаемый формат, если нужно
                img_path = convert_image_to_supported_format(img_path)

                # Добавляем картинку в документ
                try:
                    doc.add_picture(img_path, width=Inches(5.0))  # Добавляем картинку в документ
                except Exception as e:
                    print(f"Ошибка при добавлении картинки: {e}")

    # Сохраняем файл
    doc.save(f"{filename}.docx")
    print(f"Статья сохранена как {filename}.docx")
