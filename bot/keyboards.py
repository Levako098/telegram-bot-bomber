from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
from bot.text import PROXY_FILES, template_file_path

def get_main_inline_keyboard(user_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton('⚙️ Настройки', callback_data='show_settings'))
    markup.add(InlineKeyboardButton('🚀 Запуск', callback_data='start_process'))
    markup.add(InlineKeyboardButton('📊 Статус', callback_data='show_status'))
    markup.add(InlineKeyboardButton('🛡️ Админ панель', callback_data='show_admin_panel'))
    return markup

def get_settings_inline_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton('🔄 Изменить циклы', callback_data='set_cycles'))
    markup.add(InlineKeyboardButton('🚀 Изменить потоки', callback_data='set_threads'))
    markup.add(InlineKeyboardButton('⏰ Изменить задержку', callback_data='set_delay'))
    markup.add(InlineKeyboardButton('🔙 Назад', callback_data='back_to_main'))
    return markup

def get_admin_inline_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton('➕ Добавить пользователя', callback_data='admin_add'))
    markup.add(InlineKeyboardButton('➖ Отнять доступ', callback_data='admin_revoke'))
    markup.add(InlineKeyboardButton('🚫 Заблокировать', callback_data='admin_block'))
    markup.add(InlineKeyboardButton('🔙 Назад', callback_data='back_to_main'))
    return markup

def get_templates_inline_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton('🚀 SUPERMODE', callback_data='supermode'))
    try:
        with open(template_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if not lines:
                logging.debug(f"Файл {template_file_path} пуст")
                markup.add(InlineKeyboardButton('❌ Шаблоны пусты', callback_data='no_templates'))
            for line in lines:
                try:
                    number, owner = line.strip().split(' - ', 1)
                    number = number.strip()
                    owner = owner.strip()
                    markup.add(InlineKeyboardButton(f"{owner} ({number})", callback_data=f'template_{number}'))
                except ValueError:
                    logging.debug(f"Неверный формат строки в {template_file_path}: {line.strip()}")
                    continue
    except FileNotFoundError:
        logging.debug(f"Файл {template_file_path} не найден")
        markup.add(InlineKeyboardButton('❌ Шаблоны не найдены', callback_data='no_templates'))
    except PermissionError:
        logging.debug(f"Нет доступа к файлу {template_file_path}")
        markup.add(InlineKeyboardButton('❌ Нет доступа к файлу шаблонов', callback_data='no_templates'))
    except Exception as e:
        logging.debug(f"Ошибка чтения {template_file_path}: {str(e)}")
        markup.add(InlineKeyboardButton('❌ Ошибка чтения шаблонов', callback_data='no_templates'))
    markup.add(InlineKeyboardButton('🔙 Назад', callback_data='back_to_main'))
    return markup

def get_proxy_inline_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton('🌐 Без прокси', callback_data='proxy_none'))
    for name in PROXY_FILES:
        display_name = name.capitalize()
        markup.add(InlineKeyboardButton(f"🌐 {display_name}", callback_data=f'proxy_{name}'))
    markup.add(InlineKeyboardButton('🔙 Назад', callback_data='back_to_phone'))
    return markup