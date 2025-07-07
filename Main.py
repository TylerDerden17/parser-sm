import Parser
import Parser_list

def display_menu():
    print("\nМеню:")
    print("1. Сохранить статью в DOCX")
    print("2. Спарсить статьи и сохранить в CSV")
    print("3. Просмотреть все статьи")
    print("4. Выйти")

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
            print("✅ Статьи сохранены в CSV!")
            for article in articles:
                print(article)
        else:
            print("⚠️ Не удалось найти статьи для парсинга.")
    except Exception as e:
        print(f"❌ Ошибка при парсинге или сохранении: {e}")

def display_all_articles():
    try:
        articles = Parser_list.parse()
        if articles:
            for article in articles:
                print(article)
        else:
            print("⚠️ Нет доступных статей для отображения.")
    except Exception as e:
        print(f"❌ Ошибка при получении статей: {e}")

def main():
    while True:
        display_menu()
        choice = input("Выберите действие (1-4): ").strip()

        if choice == "1":
            save_article()
        elif choice == "2":
            parse_and_save_articles()
        elif choice == "3":
            display_all_articles()
        elif choice == "4":
            print("👋 Выход из программы...")
            break
        else:
            print("❗ Некорректный выбор. Пожалуйста, выберите от 1 до 4.")

if __name__ == "__main__":
    main()
