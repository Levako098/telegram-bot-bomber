import logging
import time
import threading
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.text import (
    default_settings, user_settings, user_states, 
    STATE_PHONE, STATE_PROXY, STATE_PROXY_SUPER,
    STATE_SETTINGS_CYCLES, STATE_SETTINGS_THREADS, STATE_SETTINGS_DELAY,
    STATE_ADMIN_ADD_USER, STATE_ADMIN_REVOKE_USER, STATE_ADMIN_BLOCK_USER,
    template_file_path, PROXY_FILES
)
from bot.keyboards import (
    get_main_inline_keyboard, get_settings_inline_keyboard,
    get_admin_inline_keyboard, get_templates_inline_keyboard
)
from helper.sendcode import (
    run_main_process, load_templates, get_chat_results, get_chat_logs, urls
)
from proxy.helper import load_proxies
from database.db import add_user, add_message, get_user_language, set_user_language

# Словарь переводов для интерфейса
TRANSLATIONS = {
    'ru': {
        'select_language': '🇷🇺 Выбери язык',
        'russian': '🇷🇺 Русский',
        'english': '🇺🇸 English',
        'main_menu': '🪪 Главное меню hsq бомбера',
        'spam': '🗡️ Рассылка',
        'settings': '⚙️ Настройки',
        'enter_phone': '☎️ Введите номер для рассылки',
        'template': '💉 Шаблон',
        'select_proxy': '🗞️ Выберете страну прокси',
        'no_proxy': '🏳️ Без прокси',
        'russia': '🇷🇺 Россия',
        'armenia': '🇦🇲 Армения',
        'kazakhstan': '🇰🇿 Казахстан',
        'china': '🇨🇳 Китай',
        'japan': '🇯🇵 Япония',
        'belarus': '🇧🇾 Беларусь',
        'ukraine': '🇺🇦 Украина',
        'spam_completed': '✅ Рассылка завершена, желаете посмотреть логи?',
        'view_logs': '🚨 Да, желаю',
        'back_to_menu': '⛔️ Нет, в меню',
        'cycles_set': '✅ Циклы установлены: {}',
        'threads_set': '✅ Потоки установлены: {}',
        'delay_set': '✅ Задержка установлена: {} сек',
        'invalid_number': '❌ Введите число!',
        'invalid_phone': '❌ Введите номер телефона как число!',
        'admin_disabled': '❌ Функции управления доступом отключены, бот доступен всем.',
        'state_reset': '✅ Состояние сброшено.',
        'state_empty': 'ℹ️ Состояние уже пустое.',
        'chat_cleared': '🧹 Чат очищен!',
        'chat_clear_error': '❌ Ошибка при очистке чата: {}',
        'invalid_proxy': '❌ Неверный файл прокси!',
        'no_phone': '❌ Номер телефона не найден!',
        'no_templates': '❌ Шаблоны не найдены или файл недоступен!',
        'no_numbers_supermode': '❌ Нет номеров для SUPERMODE!',
        'invalid_template_phone': '❌ Неверный формат номера телефона!',
        'spam_started': '⚡️ Рассылка запущена\n🪪 Номер: {}\n📰 Кол-во сервисов: {}\n🧬 Прокси: {}',
        'supermode_started': '⚡️ SUPERMODE запущен!\n🪪 Номеров: {}\n📰 Кол-во сервисов: {}\n🧬 Прокси: {}'
    },
    'en': {
        'select_language': '🇺🇸 Select language',
        'russian': '🇷🇺 Russian',
        'english': '🇺🇸 English',
        'main_menu': '🪪 Main menu of hsq bomber',
        'spam': '🗡️ Spam',
        'settings': '⚙️ Settings',
        'enter_phone': '☎️ Enter phone number for spam',
        'template': '💉 Template',
        'select_proxy': '🗞️ Select proxy country',
        'no_proxy': '🏳️ No proxy',
        'russia': '🇷🇺 Russia',
        'armenia': '🇦🇲 Armenia',
        'kazakhstan': '🇰🇿 Kazakhstan',
        'china': '🇨🇳 China',
        'japan': '🇯🇵 Japan',
        'belarus': '🇧🇾 Belarus',
        'ukraine': '🇺🇦 Ukraine',
        'spam_completed': '✅ Spam completed, would you like to view logs?',
        'view_logs': '🚨 Yes, I want to',
        'back_to_menu': '⛔️ No, back to menu',
        'cycles_set': '✅ Cycles set: {}',
        'threads_set': '✅ Threads set: {}',
        'delay_set': '✅ Delay set: {} sec',
        'invalid_number': '❌ Enter a number!',
        'invalid_phone': '❌ Enter phone number as a number!',
        'admin_disabled': '❌ Access management functions are disabled, bot is available to everyone.',
        'state_reset': '✅ State reset.',
        'state_empty': 'ℹ️ State is already empty.',
        'chat_cleared': '🧹 Chat cleared!',
        'chat_clear_error': '❌ Error clearing chat: {}',
        'invalid_proxy': '❌ Invalid proxy file!',
        'no_phone': '❌ Phone number not found!',
        'no_templates': '❌ Templates not found or file unavailable!',
        'no_numbers_supermode': '❌ No numbers for SUPERMODE!',
        'invalid_template_phone': '❌ Invalid phone number format!',
        'spam_started': '⚡️ Spam started\n🪪 Number: {}\n📰 Number of services: {}\n🧬 Proxy: {}',
        'supermode_started': '⚡️ SUPERMODE started!\n🪪 Numbers: {}\n📰 Number of services: {}\n🧬 Proxy: {}'
    }
}

def get_translation(user_id, key):
    """Получение перевода для указанного ключа в зависимости от языка пользователя"""
    language = get_user_language(user_id)
    return TRANSLATIONS.get(language, TRANSLATIONS['ru']).get(key, key)

def register_handlers(bot: TeleBot):
    """Регистрация всех обработчиков для бота"""
    
    @bot.message_handler(commands=['start'])
    def start(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        username = message.from_user.username or message.from_user.first_name or message.from_user.last_name or "Unknown"
        
        # Проверяем, есть ли пользователь в базе
        language = get_user_language(user_id)
        add_user(user_id, username, language)
        add_message(user_id, "/start")
        
        if language == 'ru':  # Если язык не выбран или русский, показываем выбор языка
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton('🇷🇺 Русский', callback_data='lang_ru'),
                InlineKeyboardButton('🇺🇸 English', callback_data='lang_en')
            )
            bot.send_message(chat_id, "🇷🇺 Выбери язык", reply_markup=markup)
            logging.debug(f"Пользователь {user_id} запрошен выбор языка")
        else:
            show_main_menu(bot, chat_id, user_id)

    @bot.message_handler(commands=['reset'])
    def reset_state(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        add_message(user_id, "/reset")
        
        if chat_id in user_states:
            del user_states[chat_id]
            bot.send_message(chat_id, get_translation(user_id, 'state_reset'), 
                           reply_markup=get_main_inline_keyboard(user_id))
            logging.debug(f"Состояние сброшено для чата {chat_id}")
        else:
            bot.send_message(chat_id, get_translation(user_id, 'state_empty'), 
                           reply_markup=get_main_inline_keyboard(user_id))

    @bot.message_handler(commands=['clear'])
    def clear_chat(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        add_message(user_id, "/clear")
        
        logging.debug(f"Пользователь {user_id} отправил /clear в чат {chat_id}")
        try:
            for i in range(1, 100):
                try:
                    bot.delete_message(chat_id, message.message_id - i)
                except Exception:
                    break
            bot.send_message(chat_id, get_translation(user_id, 'chat_cleared'), 
                           reply_markup=get_main_inline_keyboard(user_id))
            logging.debug(f"Чат {chat_id} очищен, отправлено главное меню")
        except Exception as e:
            bot.send_message(chat_id, get_translation(user_id, 'chat_clear_error').format(str(e)), 
                           reply_markup=get_main_inline_keyboard(user_id))
            logging.error(f"Ошибка очистки чата {chat_id}: {str(e)}")

    @bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == STATE_PHONE)
    def run_process(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        add_message(user_id, message.text)
        
        logging.debug(f"run_process вызван для пользователя {user_id}, чат {chat_id}, ввод: {message.text}")
        try:
            phone_number = int(message.text)
            user_states[chat_id] = {'state': STATE_PROXY, 'phone_number': phone_number}
            logging.debug(f"Пользователь {user_id} ввел номер телефона: {phone_number}, переход к STATE_PROXY")
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton(get_translation(user_id, 'no_proxy'), callback_data='proxy_none'),
                InlineKeyboardButton(get_translation(user_id, 'russia'), callback_data='proxy_russia')
            )
            markup.add(
                InlineKeyboardButton(get_translation(user_id, 'armenia'), callback_data='proxy_armenia'),
                InlineKeyboardButton(get_translation(user_id, 'kazakhstan'), callback_data='proxy_kazakhstan')
            )
            markup.add(
                InlineKeyboardButton(get_translation(user_id, 'china'), callback_data='proxy_china'),
                InlineKeyboardButton(get_translation(user_id, 'japan'), callback_data='proxy_japan')
            )
            markup.add(
                InlineKeyboardButton(get_translation(user_id, 'belarus'), callback_data='proxy_belarus'),
                InlineKeyboardButton(get_translation(user_id, 'ukraine'), callback_data='proxy_ukraine')
            )
            bot.send_message(chat_id, get_translation(user_id, 'select_proxy'), reply_markup=markup)
        except ValueError:
            logging.debug(f"Пользователь {user_id} ввел неверный номер телефона: {message.text}")
            bot.send_message(chat_id, get_translation(user_id, 'invalid_phone'))

    @bot.message_handler(func=lambda message: True)
    def handle_all_messages(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        add_message(user_id, message.text)
        
        logging.debug(f"handle_all_messages вызван для пользователя {user_id}, чат {chat_id}, ввод: {message.text}, состояние: {user_states.get(chat_id)}")
        current_state = user_states.get(chat_id, {}).get('state') if isinstance(user_states.get(chat_id), dict) else user_states.get(chat_id)
        
        if current_state == STATE_SETTINGS_CYCLES:
            set_cycles(bot, message)
        elif current_state == STATE_SETTINGS_THREADS:
            set_threads(bot, message)
        elif current_state == STATE_SETTINGS_DELAY:
            set_delay(bot, message)
        elif current_state in [STATE_ADMIN_ADD_USER, STATE_ADMIN_REVOKE_USER, STATE_ADMIN_BLOCK_USER]:
            handle_admin_actions(bot, message)
        else:
            bot.send_message(chat_id, get_translation(user_id, 'main_menu'), 
                           reply_markup=get_main_inline_keyboard(user_id))

    @bot.callback_query_handler(func=lambda call: True)
    def callback_handler(call):
        chat_id = call.message.chat.id
        user_id = call.from_user.id
        add_message(user_id, f"Callback: {call.data}")
        
        logging.debug(f"Callback от пользователя {user_id}, чат {chat_id}, данные: {call.data}")
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except Exception as e:
            logging.debug(f"Не удалось удалить сообщение {call.message.message_id}: {str(e)}")

        if call.data.startswith('lang_'):
            language = call.data.replace('lang_', '')
            set_user_language(user_id, language)
            show_main_menu(bot, chat_id, user_id)
            bot.answer_callback_query(call.id)
        elif call.data == 'show_settings':
            show_settings_inline(bot, chat_id, user_id)
            bot.answer_callback_query(call.id)
        elif call.data == 'start_process':
            user_states[chat_id] = {'state': STATE_PHONE}
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(get_translation(user_id, 'template'), callback_data='show_templates'))
            bot.send_message(chat_id, get_translation(user_id, 'enter_phone'), reply_markup=markup)
            bot.answer_callback_query(call.id)
        elif call.data == 'show_status':
            show_status_inline(bot, chat_id, user_id)
            bot.answer_callback_query(call.id)
        elif call.data == 'show_admin_panel':
            bot.send_message(chat_id, "🛡️ Admin panel:", reply_markup=get_admin_inline_keyboard())
            bot.answer_callback_query(call.id)
        elif call.data == 'set_cycles':
            user_states[chat_id] = {'state': STATE_SETTINGS_CYCLES}
            bot.send_message(chat_id, "Enter number of cycles (1-50):" if get_user_language(user_id) == 'en' else "Введите количество циклов (1-50):")
            bot.answer_callback_query(call.id)
            logging.debug(f"Установлено состояние STATE_SETTINGS_CYCLES для чата {chat_id}")
        elif call.data == 'set_threads':
            user_states[chat_id] = {'state': STATE_SETTINGS_THREADS}
            bot.send_message(chat_id, "Enter number of threads (1-20):" if get_user_language(user_id) == 'en' else "Введите количество потоков (1-20):")
            bot.answer_callback_query(call.id)
            logging.debug(f"Установлено состояние STATE_SETTINGS_THREADS для чата {chat_id}")
        elif call.data == 'set_delay':
            user_states[chat_id] = {'state': STATE_SETTINGS_DELAY}
            bot.send_message(chat_id, "Enter delay in seconds:" if get_user_language(user_id) == 'en' else "Введите задержку в секундах:")
            bot.answer_callback_query(call.id)
            logging.debug(f"Установлено состояние STATE_SETTINGS_DELAY для чата {chat_id}")
        elif call.data == 'admin_add':
            user_states[chat_id] = {'state': STATE_ADMIN_ADD_USER}
            bot.answer_callback_query(call.id, "Enter user ID to add:" if get_user_language(user_id) == 'en' else "Введите ID пользователя для добавления:")
            logging.debug(f"Установлено состояние STATE_ADMIN_ADD_USER для чата {chat_id}")
        elif call.data == 'admin_revoke':
            user_states[chat_id] = {'state': STATE_ADMIN_REVOKE_USER}
            bot.answer_callback_query(call.id, "Enter user ID to revoke access:" if get_user_language(user_id) == 'en' else "Введите ID пользователя для отзыва доступа:")
            logging.debug(f"Установлено состояние STATE_ADMIN_REVOKE_USER для чата {chat_id}")
        elif call.data == 'admin_block':
            user_states[chat_id] = {'state': STATE_ADMIN_BLOCK_USER}
            bot.answer_callback_query(call.id, "Enter user ID to block:" if get_user_language(user_id) == 'en' else "Введите ID пользователя для блокировки:")
            logging.debug(f"Установлено состояние STATE_ADMIN_BLOCK_USER для чата {chat_id}")
        elif call.data == 'show_templates':
            markup = get_templates_inline_keyboard()
            bot.send_message(chat_id, get_translation(user_id, 'template'), reply_markup=markup)
            bot.answer_callback_query(call.id)
            logging.debug(f"Показаны шаблоны для чата {chat_id}")
        elif call.data == 'supermode':
            templates = load_templates()
            if not templates:
                bot.send_message(chat_id, get_translation(user_id, 'no_templates'))
                bot.answer_callback_query(call.id)
                return
            user_states[chat_id] = {'state': STATE_PROXY_SUPER, 'templates': templates}
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton(get_translation(user_id, 'no_proxy'), callback_data='proxy_none'),
                InlineKeyboardButton(get_translation(user_id, 'russia'), callback_data='proxy_russia')
            )
            markup.add(
                InlineKeyboardButton(get_translation(user_id, 'armenia'), callback_data='proxy_armenia'),
                InlineKeyboardButton(get_translation(user_id, 'kazakhstan'), callback_data='proxy_kazakhstan')
            )
            markup.add(
                InlineKeyboardButton(get_translation(user_id, 'china'), callback_data='proxy_china'),
                InlineKeyboardButton(get_translation(user_id, 'japan'), callback_data='proxy_japan')
            )
            markup.add(
                InlineKeyboardButton(get_translation(user_id, 'belarus'), callback_data='proxy_belarus'),
                InlineKeyboardButton(get_translation(user_id, 'ukraine'), callback_data='proxy_ukraine')
            )
            bot.send_message(chat_id, get_translation(user_id, 'select_proxy'), reply_markup=markup)
            bot.answer_callback_query(call.id)
            logging.debug(f"Активирован SUPERMODE для чата {chat_id} с {len(templates)} номерами")
        elif call.data.startswith('template_'):
            phone_number = call.data.replace('template_', '')
            try:
                phone_number = int(phone_number)
                user_states[chat_id] = {'state': STATE_PROXY, 'phone_number': phone_number}
                markup = InlineKeyboardMarkup()
                markup.add(
                    InlineKeyboardButton(get_translation(user_id, 'no_proxy'), callback_data='proxy_none'),
                    InlineKeyboardButton(get_translation(user_id, 'russia'), callback_data='proxy_russia')
                )
                markup.add(
                    InlineKeyboardButton(get_translation(user_id, 'armenia'), callback_data='proxy_armenia'),
                    InlineKeyboardButton(get_translation(user_id, 'kazakhstan'), callback_data='proxy_kazakhstan')
                )
                markup.add(
                    InlineKeyboardButton(get_translation(user_id, 'china'), callback_data='proxy_china'),
                    InlineKeyboardButton(get_translation(user_id, 'japan'), callback_data='proxy_japan')
                )
                markup.add(
                    InlineKeyboardButton(get_translation(user_id, 'belarus'), callback_data='proxy_belarus'),
                    InlineKeyboardButton(get_translation(user_id, 'ukraine'), callback_data='proxy_ukraine')
                )
                bot.send_message(chat_id, get_translation(user_id, 'select_proxy'), reply_markup=markup)
                logging.debug(f"Пользователь {user_id} выбрал номер {phone_number} из шаблона, переход к STATE_PROXY")
                bot.answer_callback_query(call.id)
            except ValueError:
                bot.answer_callback_query(call.id, get_translation(user_id, 'invalid_template_phone'))
                logging.debug(f"Неверный формат номера телефона в шаблоне: {phone_number}")
        elif call.data.startswith('proxy_'):
            proxy_name = call.data.replace('proxy_', '')
            user_state = user_states.get(chat_id, {})
            if 'state' not in user_state:
                bot.answer_callback_query(call.id, "❌ State not found!" if get_user_language(user_id) == 'en' else "❌ Состояние не найдено!")
                return
            if proxy_name == 'none':
                proxy_file = None
                proxy_display = get_translation(user_id, 'no_proxy')
            elif proxy_name not in PROXY_FILES:
                bot.answer_callback_query(call.id, get_translation(user_id, 'invalid_proxy'))
                logging.debug(f"Выбран неверный файл прокси: {proxy_name}")
                return
            else:
                proxy_file = PROXY_FILES[proxy_name]
                proxy_display = get_translation(user_id, proxy_name)
            
            current_settings = user_settings.get(chat_id, default_settings)
            
            if user_state['state'] == STATE_PROXY:
                phone_number = user_state.get('phone_number')
                if not phone_number:
                    bot.answer_callback_query(call.id, get_translation(user_id, 'no_phone'))
                    logging.debug(f"Номер телефона не найден в состоянии для чата {chat_id}")
                    return
                bot.send_message(chat_id, 
                               get_translation(user_id, 'spam_started').format(phone_number, len(urls), proxy_display))
                process_thread = threading.Thread(target=run_main_process, 
                                                args=(chat_id, phone_number, proxy_file, bot, user_settings, user_id))
                process_thread.start()
                logging.debug(f"Пользователь {user_id} выбрал файл прокси {proxy_file} для номера {phone_number}")
            elif user_state['state'] == STATE_PROXY_SUPER:
                templates = user_state.get('templates', [])
                if not templates:
                    bot.answer_callback_query(call.id, get_translation(user_id, 'no_numbers_supermode'))
                    return
                bot.send_message(chat_id, 
                               get_translation(user_id, 'supermode_started').format(len(templates), len(urls), proxy_display))
                for phone_number in templates:
                    process_thread = threading.Thread(target=run_main_process, 
                                                    args=(chat_id, phone_number, proxy_file, bot, user_settings, user_id))
                    process_thread.start()
                logging.debug(f"SUPERMODE: Пользователь {user_id} выбрал файл прокси {proxy_file} для {len(templates)} номеров")
            del user_states[chat_id]
            bot.answer_callback_query(call.id)
        elif call.data == 'no_templates':
            bot.answer_callback_query(call.id, get_translation(user_id, 'no_templates'))
            logging.debug(f"Шаблоны недоступны для чата {chat_id}")
        elif call.data == 'back_to_phone':
            user_states[chat_id] = {'state': STATE_PHONE}
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(get_translation(user_id, 'template'), callback_data='show_templates'))
            bot.send_message(chat_id, get_translation(user_id, 'enter_phone'), reply_markup=markup)
            bot.answer_callback_query(call.id)
            logging.debug(f"Пользователь {user_id} вернулся к вводу номера, состояние STATE_PHONE")
        elif call.data == 'view_logs':
            logs = get_chat_logs(chat_id)
            log_text = "\n".join(logs)
            with open(f'logs_{chat_id}.txt', 'w', encoding='utf-8') as f:
                f.write(log_text)
            with open(f'logs_{chat_id}.txt', 'rb') as f:
                bot.send_document(chat_id, f, caption="Logs" if get_user_language(user_id) == 'en' else "Логи")
            import os
            os.remove(f'logs_{chat_id}.txt')
            show_main_menu(bot, chat_id, user_id)
            bot.answer_callback_query(call.id)
        elif call.data == 'back_to_main':
            show_main_menu(bot, chat_id, user_id)
            bot.answer_callback_query(call.id)

    def set_cycles(bot: TeleBot, message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        add_message(user_id, message.text)
        
        logging.debug(f"set_cycles вызван для пользователя {user_id}, чат {chat_id}, ввод: {message.text}")
        try:
            value = int(message.text)
            user_settings[chat_id]['cycles'] = max(1, min(50, value))
            bot.send_message(chat_id, get_translation(user_id, 'cycles_set').format(user_settings[chat_id]['cycles']), 
                           reply_markup=get_settings_inline_keyboard())
            del user_states[chat_id]
            logging.debug(f"Циклы установлены на {user_settings[chat_id]['cycles']} для чата {chat_id}, состояние очищено")
        except ValueError:
            bot.send_message(chat_id, get_translation(user_id, 'invalid_number'))
            logging.debug(f"Неверный ввод для циклов: {message.text}")

    @bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == STATE_SETTINGS_CYCLES)
    def set_cycles_handler(message):
        set_cycles(bot, message)

    def set_threads(bot: TeleBot, message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        add_message(user_id, message.text)
        
        logging.debug(f"set_threads вызван для пользователя {user_id}, чат {chat_id}, ввод: {message.text}")
        try:
            value = int(message.text)
            user_settings[chat_id]['threads'] = max(1, min(20, value))
            bot.send_message(chat_id, get_translation(user_id, 'threads_set').format(user_settings[chat_id]['threads']), 
                           reply_markup=get_settings_inline_keyboard())
            del user_states[chat_id]
            logging.debug(f"Потоки установлены на {user_settings[chat_id]['threads']} для чата {chat_id}, состояние очищено")
        except ValueError:
            bot.send_message(chat_id, get_translation(user_id, 'invalid_number'))
            logging.debug(f"Неверный ввод для потоков: {message.text}")

    @bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == STATE_SETTINGS_THREADS)
    def set_threads_handler(message):
        set_threads(bot, message)

    def set_delay(bot: TeleBot, message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        add_message(user_id, message.text)
        
        logging.debug(f"set_delay вызван для пользователя {user_id}, чат {chat_id}, ввод: {message.text}")
        try:
            value = float(message.text)
            user_settings[chat_id]['delay'] = value
            bot.send_message(chat_id, get_translation(user_id, 'delay_set').format(user_settings[chat_id]['delay']), 
                           reply_markup=get_settings_inline_keyboard())
            del user_states[chat_id]
            logging.debug(f"Задержка установлена на {user_settings[chat_id]['delay']} для чата {chat_id}, состояние очищено")
        except ValueError:
            bot.send_message(chat_id, get_translation(user_id, 'invalid_number'))
            logging.debug(f"Неверный ввод для задержки: {message.text}")

    @bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == STATE_SETTINGS_DELAY)
    def set_delay_handler(message):
        set_delay(bot, message)

    def handle_admin_actions(bot: TeleBot, message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        add_message(user_id, message.text)
        
        logging.debug(f"handle_admin_actions вызван для пользователя {user_id}, чат {chat_id}, ввод: {message.text}")
        bot.send_message(chat_id, get_translation(user_id, 'admin_disabled'))
        del user_states[chat_id]
        logging.debug(f"Состояние очищено для чата {chat_id}")

    @bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') in [STATE_ADMIN_ADD_USER, STATE_ADMIN_REVOKE_USER, STATE_ADMIN_BLOCK_USER])
    def handle_admin_actions_handler(message):
        handle_admin_actions(bot, message)

    def show_main_menu(bot: TeleBot, chat_id, user_id):
        if chat_id not in user_settings:
            user_settings[chat_id] = default_settings.copy()
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton(get_translation(user_id, 'spam'), callback_data='start_process'),
            InlineKeyboardButton(get_translation(user_id, 'settings'), callback_data='show_settings')
        )
        bot.send_message(chat_id, get_translation(user_id, 'main_menu'), reply_markup=markup)
        logging.debug(f"Показано главное меню для чата {chat_id}")

    def show_settings_inline(bot: TeleBot, chat_id, user_id):
        current_settings = user_settings.get(chat_id, default_settings)
        settings_text = (f"{'Current settings' if get_user_language(user_id) == 'en' else 'Текущие настройки'}:\n"
                        f"🔄 {'Cycles' if get_user_language(user_id) == 'en' else 'Циклы'}: {current_settings['cycles']} (1-50)\n"
                        f"🚀 {'Threads' if get_user_language(user_id) == 'en' else 'Потоки'}: {current_settings['threads']} (1-20)\n"
                        f"⏰ {'Delay' if get_user_language(user_id) == 'en' else 'Задержка'}: {current_settings['delay']} {'sec' if get_user_language(user_id) == 'en' else 'сек'}")
        bot.send_message(chat_id, settings_text, reply_markup=get_settings_inline_keyboard())
        logging.debug(f"Показаны настройки для чата {chat_id}: {settings_text}")

    def show_status_inline(bot: TeleBot, chat_id, user_id):
        bot.send_message(chat_id, f"📊 {'Current status: Program is ready. Use buttons to proceed.' if get_user_language(user_id) == 'en' else 'Текущий статус: Программа готова. Используйте кнопки для действий.'}", 
                        reply_markup=get_main_inline_keyboard(user_id))
        logging.debug(f"Показан статус для чата {chat_id}")

    bot.start_process_inline = lambda chat_id: bot.send_message(chat_id, get_translation(user_id, 'enter_phone'), reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(get_translation(user_id, 'template'), callback_data='show_templates')))
    bot.show_settings_inline = show_settings_inline
    bot.show_status_inline = show_status_inline
    bot.set_cycles = set_cycles
    bot.set_threads = set_threads
    bot.set_delay = set_delay
    bot.handle_admin_actions = handle_admin_actions

    logging.info("Все обработчики зарегистрированы успешно")