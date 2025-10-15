import os
import logging

def load_proxies(proxy_file):
    """
    Загружает прокси из указанного файла в формате {login}:{password}@{ip}:{port}
    Возвращает список словарей с ключами 'http' и 'socks5' или пустой список, если файл не найден
    """
    proxies = []
    if not proxy_file:
        return proxies
    
    try:
        proxy_path = os.path.join('proxy', proxy_file)
        if not os.path.exists(proxy_path):
            logging.error(f"Файл прокси {proxy_path} не найден")
            return proxies
        
        with open(proxy_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    login, rest = line.split(':')
                    password, host = rest.split('@')
                    ip, port = host.split(':')
                    proxy_dict = {
                        'http': f'http://{login}:{password}@{ip}:{port}',
                        'socks5': f'socks5://{login}:{password}@{ip}:{port}'
                    }
                    proxies.append(proxy_dict)
                except ValueError:
                    logging.error(f"Неверный формат строки прокси: {line}")
                    continue
        logging.debug(f"Загружено {len(proxies)} прокси из файла {proxy_file}")
    except Exception as e:
        logging.error(f"Ошибка загрузки прокси из {proxy_file}: {str(e)}")
    
    return proxies