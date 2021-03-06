
import os
from art import tprint  # pip3 install art==5.6
import requests  # pip install requests
from bs4 import BeautifulSoup # pip install beautifulsoup4, lxml 
from time import sleep
from fake_useragent import UserAgent  # pip install fake_useragent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.proxy import Proxy, ProxyType
import getprx
import colorama
from colorama import Fore, Back, Style
colorama.init()


def clear_terminal():
    print(Fore.GREEN+Back.BLACK+''+Style.BRIGHT)
    os.system('cls' if os.name == 'nt' else 'clear')
    tprint('      Proxynema', font="cybermedium")
    print(Fore.YELLOW+Back.BLACK+Style.NORMAL+
        """
        _____________________________________________________________________

        Данный скрипт ищет временные ссылки на фильмы сайта https://kinogo.la
        посредством проксирования без VPN.
        В настоящей версии программы не реализован парсинг сериалов!
        Во избежание бана вашего ip не обновляйте список proxy слишком часто.
        кодер @jsonstackhum
        _____________________________________________________________________

        """+Fore.GREEN)


def save_film_page(link, ses):
    proxy = ses.proxies["https"] 
    user_agent = ses.headers['user-agent']
    ip = proxy.split(':')[0]
    port = int(proxy.split(':')[1])
    service = Service(os.path.abspath('geckodriver'))
    options = Options()
    options.set_preference('general.useragent.override', user_agent)
    options.set_preference('network.proxy.type', 1)
    options.set_preference('network.proxy.http', ip)
    options.set_preference('network.proxy.http_port', port)
    options.set_preference('network.proxy.https', ip)
    options.set_preference('network.proxy.https_port', port)
    options.set_preference('network.proxy.ssl', ip)
    options.set_preference('network.proxy.ssl_port', port)
    print('Прокси и user-agent подключены')
    options.headless = True
    driver = webdriver.Firefox(options=options, service=service)
    driver.get(link)
    print('GET-запрос выполнен')
    sleep(4)
    html = driver.page_source
    with open('film.html','w') as f:
        f.write(html)
        clear_terminal()
        print('Страница записана на диск')
    driver.close()
    driver.quit()
    get_mp4('film.html')


def get_mp4(file):
    clear_terminal()
    print('Поиск ссылки на файл')
    with open(file, 'r') as f:
        html = f.read()
        soup = BeautifulSoup(html, 'lxml')
        selector = str(soup.select('div:nth-child(12) > a:nth-child(2)'))
        src = selector[21:].split()[0].strip('"')

        while True:
            if 'download' in selector:
                try:
                    clear_terminal()
                    resolution = int(input(f'{Style.BRIGHT}Выберите разрешение: {Style.NORMAL}\
                        \n[{Style.BRIGHT}1{Style.NORMAL}] 240\
                        \n[{Style.BRIGHT}2{Style.NORMAL}] 360\
                        \n[{Style.BRIGHT}3{Style.NORMAL}] 480\
                        \n[{Style.BRIGHT}4{Style.NORMAL}] 720\n'))
                    src = src.strip('240.mp4')+('240.mp4' if resolution == 1 else '360.mp4' if resolution == 2 else '480.mp4' if resolution == 3 else '720.mp4' if resolution == 4 else '240.mp4')
                    clear_terminal()
                    print(f'{Style.BRIGHT}ССЫЛКА:{Style.NORMAL}')
                    print(f'{Fore.CYAN}{src}')
                    try:
                        os.remove('film.html')
                    except: pass
                    break
                except: print(Fore.RED+"Выбрано неверное разрешение"+Fore.RESET)
            else: 
                clear_terminal()
                print('Ссылка не найдена. Возможно, вы пытались найти сериал.')
                break


def get_proxies_list()->list:
    with open('https_proxy.txt', 'r') as f:
        proxies_list = f.read().strip().split('\n')
        clear_terminal()
        print(f'Найдено {len(proxies_list)} https прокси')
        sleep(1)
        clear_terminal()
        print('Ищу рабочий прокси-сервер. Ожидайте')
        sleep(1)
        clear_terminal()
        return proxies_list


def get_main_page(main_page, proxy, agent)->tuple:
    proxies={'http': proxy, 'https': proxy}
    headers={'user-agent': agent}
    session = requests.Session()
    session.proxies.update(proxies)
    session.headers.update(headers)
    r = session.get(main_page, timeout=4)
    if r.ok:
        print(f'Успешно подключен прокси сервер: {proxy} с юзер-агентом {agent}')
        return r, session
    else: print(r.status)


def search_film(ses:requests.Session, film:str)->None:
    links = []
    print('Выполняется поиск')
    payload = {'query': film}
    r = ses.post('https://kinogo.la/engine/ajax/search.php', data=payload)
    if r.ok:
        soup = BeautifulSoup(r.text, 'lxml')
        if soup.text != 'Похожих статей на сайте не найдено.Расширенный поиск':
            a = soup.find_all('a')
            cnt = 0
            for i in a[:-1] if len(a) > 1 else a:
                href = i.get('href')
                cnt+=1
                span = i.find('span', class_="searchheading")
                links.append(href)
                print(f'[{Style.BRIGHT}{cnt}{Style.NORMAL}] {span.text}')
            while True:
                try:
                    movie_number = int(input(f'{Style.BRIGHT}Введите порядковый номер фильма: {Style.NORMAL}'))
                    if movie_number != 0:
                        link = links[movie_number-1 if movie_number >= 2 else 0]
                        break
                except:
                    print(Fore.RED+'Некорректная команда'+Fore.GREEN)
            clear_terminal()
            print('Запрос страницы фильма. Ожидайте')
            sleep(3)
            save_film_page(link, ses)
        else:
            clear_terminal()
            print("Фильм не найден")


def get_film_name()->None:
    ua = UserAgent()
    clear_terminal()
    main_page = 'https://kinogo.la'
    r = None
    while True:
        film_name = input(f'{Style.BRIGHT}Введите название фильма: {Style.NORMAL}').lower().strip()
        film_name = ' '.join([i for i in film_name.split() if (i.isspace() or i.isalnum())]).strip()
        if film_name:
            for i in get_proxies_list():
                try: r, session = get_main_page(main_page, i, ua.random)
                except: print(f'{Fore.RED}Сервер {i} не доступен{Fore.RESET}'); sleep(1); clear_terminal()

                if r is not None:
                    try: 
                        search_film(session, film_name); break
                    except:
                        clear_terminal()
                        print(Fore.RED+'ОШИБКА!\nПопробуйте повторить запрос'+Fore.RESET)
                        break
            else:
                print(Fore.RED+'На данный момент все прокси недоступны'+Fore.RESET)
                break
            break
        else: print(Fore.RED+'Некорректное название'+Fore.GREEN)


def main():
    clear_terminal()
    while True:
        while True:
            try:
                command = int(input(f'{Fore.GREEN}{Back.BLACK}{Style.BRIGHT}Введите номер команды:{Style.NORMAL}\
                \n[{Style.BRIGHT}1{Style.NORMAL}] Найти фильм\
                \n[{Style.BRIGHT}2{Style.NORMAL}] Обновить proxy\
                \n[{Style.BRIGHT}3{Style.NORMAL}] Выход\n'))
                break
            except:
                clear_terminal()
                print(Fore.RED+'Некорректная команда'+Fore.RESET)
        if command == 1:
            get_film_name()
        elif command == 2:
            clear_terminal()
            getprx.update_proxy()
            print('Прокси успешно обновлены')
        elif command == 3:
            clear_terminal()
            print('Всего доброго!')
            sleep(3)
            break
        elif command not in (1, 2, 3):
            clear_terminal()
            print(Fore.RED+'Некорректная команда'+Fore.RESET)


if __name__ == '__main__':
    main()
