import logging
import sys
import os
import time
from telebot import TeleBot

# Добавляем текущую директорию в sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Настройка логирования в консоль
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Проверяем наличие необходимых файлов
bot_dir = os.path.join(current_dir, 'bot')
keyboards_file = os.path.join(bot_dir, 'keyboards.py')
if not os.path.exists(bot_dir):
    print(f"Ошибка: Папка 'bot' не найдена в {current_dir}")
    sys.exit(1)
if not os.path.exists(keyboards_file):
    print(f"Ошибка: Файл 'keyboards.py' не найден в {bot_dir}")
    sys.exit(1)

logging.debug(f"Текущая рабочая директория: {os.getcwd()}")
logging.debug(f"Пути поиска Python: {sys.path}")

# Импортируем модули
try:
    from handlers import register_handlers
    from bot.keyboards import get_main_inline_keyboard
    from database.db import init_databases
except ImportError as e:
    logging.error(f"Ошибка импорта модулей: {str(e)}")
    sys.exit(1)

# Инициализация баз данных
init_databases()

# Токен бота
TOKEN = ''
bot = TeleBot(TOKEN)

def start_bot():
    logging.info("Запуск HSQ Bot...")
    # Регистрируем обработчики
    register_handlers(bot)
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {str(e)}")
        time.sleep(10)
        bot.polling(none_stop=True)

if __name__ == '__main__':

    start_bot()
