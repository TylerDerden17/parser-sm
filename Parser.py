import os
import re
import requests
from PIL import Image
from docx import Document
from docx.shared import Inches, Pt
from bs4 import BeautifulSoup
from docx.oxml.ns import qn  # Для явного указания шрифта
from docx.oxml import OxmlElement

def normalize_url(input_url):
    match = re.search(r'/(\d+)', input_url)
    if match:
        article_id = match.group(1)
        return f"https://smart-lab.ru/mobile/topic/{article_id}"
    else:
        raise ValueError("Не удалось извлечь ID статьи из ссылки.")


def download_image(img_url, img_path):
    try:
        img_data = requests.get(img_url)
        img_data.raise_for_status()
        with open(img_path, 'wb') as handler:
            handler.write(img_data.content)
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при скачивании изображения {img_url}: {e}")


def convert_image_to_supported_format(img_path):
    if img_path.lower().endswith(".webp"):
        try:
            img = Image.open(img_path)
            img_path_new = img_path.replace(".webp", ".png")
            img.save(img_path_new, "PNG")
            os.remove(img_path)
            img_path = img_path_new
            print(f"Конвертировано: {img_path}")
        except Exception as e:
            print(f"Ошибка конвертации {img_path}: {e}")
    return img_path


def save_article_to_docx(raw_url):
    url = normalize_url(raw_url)

    response = requests.get(url)
    if response.status_code != 200:
        print("Ошибка: не удалось загрузить страницу.")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    title_tag = soup.select_one("div.post-card__title-wrap")
    title = title_tag.get_text(strip=True) if title_tag else "Статья"

    # Удаляем запрещённые символы и заменяем . , пробелы на _
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
    safe_title = safe_title.replace('.', '_').replace(',', '_').replace(' ', '_')

    article_dir = os.path.join("articles", safe_title)
    os.makedirs(article_dir, exist_ok=True)

    # Создаём подпапку для изображений
    images_dir = os.path.join(article_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    doc = Document()

    # 🔷 Заголовок с нужным стилем
    heading = doc.add_paragraph()
    run = heading.add_run(title)
    run.font.name = 'Arial Black'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial Black')
    run.font.size = Pt(18)

    content = soup.select_one("div.post-card__text")
    if content:
        for p in content.find_all("p"):
            text = p.get_text()
            if not text.strip() and not p.find("img"):
                continue

            # 🔹 Добавление текста с нужным шрифтом
            paragraph = doc.add_paragraph()
            run = paragraph.add_run(text)
            run.font.name = 'Arial'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
            run.font.size = Pt(12)

            # 🔸 Обработка изображения
            img_tag = p.find("img")
            if img_tag and img_tag.get("src"):
                img_url = img_tag["src"]
                if not img_url.startswith("http"):
                    img_url = "https://smart-lab.ru" + img_url
                img_name = img_url.split("/")[-1].split("?")[0]
                img_path = os.path.join(images_dir, img_name)

                download_image(img_url, img_path)
                img_path = convert_image_to_supported_format(img_path)

                try:
                    doc.add_picture(img_path, width=Inches(5.0))
                except Exception as e:
                    print(f"Ошибка при вставке изображения {img_path}: {e}")

    docx_path = os.path.join(article_dir, f"{safe_title}.docx")
    doc.save(docx_path)
    print(f"\n✅ Статья сохранена: {docx_path}")
