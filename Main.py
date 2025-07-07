import Parser
import Parser_list

def display_menu():
    print("\nМеню:")
    print("1. Сохранить статью в DOCX")
    print("2. Спарсить статьи и сохранить в CSV")
    print("3. Просмотреть все статьи")
    print("4. Выйти")

def save_article():
    url = input("Введите URL статьи для сохранения в DOCX: ")
    filename = input("Введите название файла для сохранения: ")
    Parser.save_article_to_docx(url, filename)

def parse_and_save_articles():
    articles = Parser_list.parse()
    Parser_list.save_to_csv(articles)
    print("Статьи сохранены в CSV!")
    for article in articles:
        print(article)

def main():
    while True:
        display_menu()

        choice = input("Выберите действие (1-4): ")

        if choice == "1":
            save_article()
        elif choice == "2":
            parse_and_save_articles()
        elif choice == "3":
            articles = Parser_list.parse()
            for article in articles:
                print(article)
        elif choice == "4":
            print("Выход из программы...")
            break
        else:
            print("Некорректный выбор. Пожалуйста, выберите от 1 до 4.")

if __name__ == "__main__":
    main()
