import telebot
from logger import Logger
from api import GoogleBooksAPI, OpenLibraryAPI
from scraper import BookScraper
import requests
import random

API_TOKEN = '7812297707:AAG7kKywnWPqN4aeVGc7aCw3TR7rc2HOags'  # Замените на ваш токен

# Создаем экземпляр бота и логгера
bot = telebot.TeleBot(API_TOKEN)
logger = Logger()

# Инициализация API
google_books_api = GoogleBooksAPI()
open_library_api = OpenLibraryAPI()

# Инициализация парсера
book_scraper = BookScraper()

# Обработчик кнопки start
@bot.message_handler(commands=['start'])
def cmd_start(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(telebot.types.KeyboardButton("📖 Случайная книга"),
                 telebot.types.KeyboardButton("📚 Выбрать жанр"),
                 telebot.types.KeyboardButton("🔍 Поиск книги по слову"),
                 telebot.types.KeyboardButton("👨‍📚 Поиск книги по автору"),
                 telebot.types.KeyboardButton("❓ Помощь"))  # Добавляем кнопку помощи
    welcome_text = "Привет! Я BookBot. Выберите опцию:"
    log_and_send(message.chat.id, welcome_text, message.from_user.username, reply_markup=keyboard)

# Обработчик кнопки помощи
@bot.message_handler(func=lambda message: message.text == "❓ Помощь")
def cmd_help(message):
    help_text = (
        "Я могу помочь вам найти книги! Вот что я умею:\n"
        "1. 📖 Случайная книга - Получите информацию о случайной книге.\n"
        "2. 📚 Выбрать жанр - Выберите жанр книги, чтобы просмотреть доступные книги.\n"
        "3. 🔍 Поиск книги по слову - Введите слово для поиска книг по названию.\n"
        "4. 👨‍📚 Поиск книги по автору - Введите имя автора для поиска книг.\n"
    )
    log_and_send(message.chat.id, help_text, message.from_user.username)

# Обработчик выбора жанра
@bot.message_handler(func=lambda message: message.text == "📚 Выбрать жанр")
def cmd_select_genre(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    genres = {
        "Фантастика": "http://books.toscrape.com/catalogue/category/books/science-fiction_16/index.html",
        "Роман": "http://books.toscrape.com/catalogue/category/books/romance_8/index.html",
        "Детектив": "http://books.toscrape.com/catalogue/category/books/mystery_3/index.html",
        "Фэнтези": "http://books.toscrape.com/catalogue/category/books/fantasy_19/index.html"
    }

    for genre, url in genres.items():
        keyboard.add(telebot.types.InlineKeyboardButton(genre, url=url))

    log_and_send(message.chat.id, "Выберите жанр:", message.from_user.username, reply_markup=keyboard)

# Обработчик кнопки поиска книги по слову
@bot.message_handler(func=lambda message: message.text == "🔍 Поиск книги по слову")
def cmd_search_by_word(message):
    log_and_send(message.chat.id, "Введите слово для поиска:", message.from_user.username)
    bot.register_next_step_handler(message, search_book_by_word)

def search_book_by_word(message):
    title_word = message.text
    log_and_send(message.chat.id, f"Вы искали: {title_word}", "BOT")  # Показываем, что ввел пользователь
    result = google_books_api.search_by_title(title_word)
    log_and_send(message.chat.id, result, "BOT")

# Обработчик кнопки поиска книги по автору
@bot.message_handler(func=lambda message: message.text == "👨‍📚 Поиск книги по автору")
def cmd_search_by_author(message):
    log_and_send(message.chat.id, "Введите фамилию и имя автора на английском:", message.from_user.username)
    bot.register_next_step_handler(message, search_book_by_author)

def search_book_by_author(message):
    author = message.text
    log_and_send(message.chat.id, f"Вы искали книги автора: {author}", "BOT")  # Показываем, что ввел пользователь
    result = open_library_api.search_by_author(author)
    log_and_send(message.chat.id, result, "BOT")

# Обработчик случайной книги
@bot.message_handler(func=lambda message: message.text == "📖 Случайная книга")
def cmd_random_book(message):
    try:
        random_seed = str(random.randint(1, 100000))
        search_url = f"https://openlibrary.org/search.json?q={random_seed}&limit=1"
        search_response = requests.get(search_url)
        search_response.raise_for_status()

        search_data = search_response.json()
        if not search_data.get("docs"):
            log_and_send(message.chat.id, "Не удалось найти случайную книгу. Попробуйте ещё раз.", "BOT")
            return

        book_data = search_data["docs"][0]
        work_id = book_data.get("key")
        if work_id:
            book_url = f"https://openlibrary.org{work_id}.json"
            book_response = requests.get(book_url)
            book_response.raise_for_status()
            full_data = book_response.json()
        else:
            full_data = book_data

        title = full_data.get("title", "Без названия")
        authors = ", ".join(book_data.get("author_name", ["Неизвестен"]))
        year = book_data.get("first_publish_year", "Неизвестен")
        isbn = ", ".join(book_data.get("isbn", ["Нет данных"]))[:50]

        cover_id = book_data.get("cover_i")
        cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else None

        reply_text = (
            f"📚 Случайная книга:\n"
            f"Название: {title}\n"
            f"Автор: {authors}\n"
            f"Год: {year}\n"
        )

        if cover_url:
            bot.send_photo(message.chat.id, cover_url, caption=reply_text)
        else:
            log_and_send(message.chat.id, reply_text, "BOT")

    except requests.exceptions.HTTPError as http_err:
        log_and_send(message.chat.id, "Ошибка при получении данных с OpenLibrary.", "BOT")
        print(f"HTTP error: {http_err}")
    except Exception as e:
        log_and_send(message.chat.id, "Произошла непредвиденная ошибка.", "BOT")
        print(f"Error: {e}")

def log_and_send(chat_id, text, username=None, **kwargs):
    """
    Логирует и отправляет сообщение
    :param chat_id: ID чата
    :param text: Текст сообщения
    :param username: Имя пользователя (для логирования)
    :param kwargs: Доп. параметры для send_message
    """
    try:
        # Логируем исходящее сообщение
        logger.log_message(
            user_id=chat_id,
            username=username or "BOT",
            message=text,
            is_bot=(username == "BOT")
        )

        # Отправляем сообщение
        return bot.send_message(chat_id, text, **kwargs)
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")

# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)

