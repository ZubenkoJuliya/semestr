import requests  # Импортируем библиотеку для выполнения HTTP-запросов


class GoogleBooksAPI:
    def search_by_title(self, title_word: str):
        # Формируем URL для запроса к Google Books API с поиском по слову в названии
        url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title_word}&maxResults=5"

        # Отправляем GET-запрос к API
        response = requests.get(url)

        # Проверяем статус ответа
        if response.status_code != 200:
            return "Ошибка при запросе к API Google Books."

        # Преобразуем ответ из JSON в словарь Python
        data = response.json()

        # Извлекаем список книг из ответа
        items = data.get('items', [])

        # Если список книг пустой, возвращаем сообщение об отсутствии результатов
        if not items:
            return "Книги с таким словом в названии не найдены."

        # Берём первую книгу из списка
        book = items[0]

        # Извлекаем информацию о книге
        info = book.get('volumeInfo', {})
        title = info.get('title', 'Нет названия')  # Название книги
        authors = ', '.join(info.get('authors', ['Неизвестный автор']))  # Список авторов
        link = info.get('infoLink', 'Ссылка отсутствует')  # Ссылка на страницу книги

        # Формируем и возвращаем строку с информацией о книге
        return f"📖 <b>{title}</b>\n👤 {authors}\n🔗 {link}"


class OpenLibraryAPI:
    def search_by_author(self, author: str):
        # Формируем URL для запроса к OpenLibrary API с поиском по автору
        search_url = f"https://openlibrary.org/search.json?q=author:{author}&limit=1"

        # Отправляем GET-запрос к API
        search_response = requests.get(search_url)

        # Проверяем статус ответа
        if search_response.status_code != 200:
            return "Ошибка при запросе к OpenLibrary."

        # Преобразуем ответ из JSON в словарь Python
        search_data = search_response.json()

        # Проверяем наличие списка книг в ответе
        if not search_data.get("docs"):
            return "Не удалось найти книгу. Попробуйте ещё раз."

        # Берём первую книгу из списка результатов
        book_data = search_data["docs"][0]

        # Извлекаем информацию о книге
        title = book_data.get("title", "Без названия")  # Название книги
        authors = ", ".join(book_data.get("author_name", ["Неизвестен"]))  # Список авторов
        year = book_data.get("first_publish_year", "Неизвестен")  # Год первого издания

        # Формируем и возвращаем строку с информацией о книге
        return f"📚 Книга автора '{author}':\nНазвание: {title}\nАвтор: {authors}\nГод: {year}"
