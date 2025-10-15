# Настройки по умолчанию
default_settings = {
    'cycles': 1,
    'threads':20,
    'delay': 0.1
}

# Хранилища для пользовательских данных
user_settings = {}
user_states = {}

# Константы состояний
STATE_PHONE = 'phone'
STATE_PROXY = 'proxy'
STATE_PROXY_SUPER = 'proxy_super'
STATE_SETTINGS_CYCLES = 'settings_cycles'
STATE_SETTINGS_THREADS = 'settings_threads'
STATE_SETTINGS_DELAY = 'settings_delay'
STATE_ADMIN_ADD_USER = 'admin_add_user'
STATE_ADMIN_REVOKE_USER = 'admin_revoke_user'
STATE_ADMIN_BLOCK_USER = 'admin_block_user'

# Путь к файлу шаблонов
template_file_path = '7E.txt'

# Файлы прокси
PROXY_FILES = {
    'russia': 'russia.txt',
    'armenia': 'armenia.txt',
    'kazakhstan': 'kazakhstan.txt',
    'china': 'china.txt',
    'japan': 'japan.txt',
    'belarus': 'belarus.txt',
    'ukraine': 'ukraine.txt'
}

# Список User-Agent'ов
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
]