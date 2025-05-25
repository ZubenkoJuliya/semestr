import requests  # Для выполнения HTTP-запросов к сайту
from bs4 import BeautifulSoup  # Для парсинга HTML-страниц
import random  # Для выбора случайной книги из списка

class BookScraper:
    def scrape_books_from_site(self):
        """
        Метод для парсинга книг с сайта books.toscrape.com.
        Собирает данные о книгах с первой и нескольких следующих страниц.
        Возвращает список словарей с информацией о книгах.
        """
        base_url = "http://books.toscrape.com/catalogue/page-{}.html"  # Шаблон URL для страниц с книгами (со 2-й по 5-ю)
        books_data = []  # Список для хранения информации о книгах

        # Первая страница - index.html, остальные страницы - page-2.html, page-3.html и т.д.
        # Поэтому формируем список URL: сначала index.html, затем страницы с 2 по 5
        urls = ["http://books.toscrape.com/index.html"] + [base_url.format(i) for i in range(2, 6)]

        headers = {"User-Agent": "Mozilla/5.0"}  # Заголовок User-Agent для имитации запроса от браузера

        # Проходим по каждому URL из списка
        for url in urls:
            try:
                # Выполняем GET-запрос к странице с таймаутом 10 секунд
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()  # Проверяем, что запрос успешен (код 200)
            except requests.RequestException as e:
                # Если возникла ошибка запроса, возвращаем список с одним элементом — описанием ошибки,
                # чтобы не прерывать работу программы
                return [{"title": "Ошибка запроса", "price": "-", "availability": "-", "rating": str(e)}]

            # Парсим HTML-код страницы с помощью BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            # Находим все элементы книг - они находятся в тегах <article> с классом product_pod
            book_elements = soup.select("article.product_pod")

            # Проходим по каждой книге на странице
            for book in book_elements:
                # Получаем название книги из атрибута title тега <a> внутри <h3>
                title = book.h3.a["title"]
                # Получаем цену книги (текст внутри элемента с классом price_color)
                price = book.select_one(".price_color").text
                # Получаем информацию о наличии книги, убирая лишние пробелы
                availability = book.select_one(".availability").text.strip()
                # Получаем список классов тега <p> с классом star-rating, например ["star-rating", "Three"]
                rating_class = book.select_one("p.star-rating")["class"]

                # Находим слово рейтинга, исключая "star-rating"
                rating_word = next((cls for cls in rating_class if cls != "star-rating"), "No rating")

                # Сопоставляем словесный рейтинг с числовым значением
                rating_map = {
                    "One": 1,
                    "Two": 2,
                    "Three": 3,
                    "Four": 4,
                    "Five": 5
                }
                rating = rating_map.get(rating_word, 0)  # Если рейтинг не найден, ставим 0

                # Добавляем словарь с данными книги в общий список
                books_data.append({
                    "title": title,
                    "price": price,
                    "availability": availability,
                    "rating": rating
                })

        # Возвращаем список всех собранных книг
        return books_data

    def get_random_book(self):
        """
        Метод для получения информации о случайной книге.
        Выбирает случайную книгу из списка, полученного методом scrape_books_from_site.
        Возвращает форматированную строку с данными книги.
        """
        books = self.scrape_books_from_site()  # Получаем список книг
        if books:
            random_book = random.choice(books)  # Выбираем случайную книгу
            # Формируем строку с информацией о книге для вывода
            return (f"📚 Случайная книга:\n"
                    f"Название: {random_book['title']}\n"
                    f"Цена: {random_book['price']}\n"
                    f"Наличие: {random_book['availability']}\n"
                    f"Рейтинг: {random_book['rating']}")
        # Если список книг пустой, возвращаем сообщение об ошибке
        return "Не удалось получить случайную книгу."
