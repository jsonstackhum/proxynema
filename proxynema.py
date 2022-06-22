
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


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')
    tprint('        ProXynema')
    print("""
        Данный скрипт ищет временные ссылки на фильмы сайта https://kinogo.la
        посредством проксирования без VPN.
        В настоящей версии программы не реализован парсинг сериалов!
        Во избежание бана вашего ip не обновляйте список proxy слишком часто.
        кодер @jsonstackhum 

        """)


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
    options.headless = True
    driver = webdriver.Firefox(options=options, service=service)
    driver.get(link)
    sleep(2)
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
        section = soup.find('div', class_='section')
        box_visible = section.find('div', class_='box visible')
        pjsdiv = box_visible.find('pjsdiv', class_='pjscssed')
        video = pjsdiv.find('video')
        src = video.get('src')
        while True:
            try:
                clear_terminal()
                resolution = int(input('Выберите разрешение: \n1: 240\n2: 360\n3: 480\n4: 720\n'))
                src = src.strip('240.mp4')+('240.mp4' if resolution == 1 else '360.mp4' if resolution == 2 else '480.mp4' if resolution == 3 else '720.mp4' if resolution == 4 else '240.mp4')
                clear_terminal()
                print('ССЫЛКА:')
                print(src)
                try:
                    os.remove('film.html')
                except: pass
                break
            except: print("Выбрано неверное разрешение")


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
    r = session.get(main_page, timeout=3)
    if r.ok:
        print(f'Успешно подключен прокси сервер: {proxy} с юзер-агентом {agent}')
        return r, session
    else: print(r.status)


def search_film(ses, film):
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
                print(f'{cnt}: {span.text}')
            while True:
                try:
                    movie_number = int(input('Введите порядковый номер фильма: '))
                    link = links[movie_number-1 if movie_number >= 2 else 0]
                    break
                except:
                    print('Некорректная команда')
            clear_terminal()
            print('Запрос страницы фильма. Ожидайте')
            sleep(3)
            save_film_page(link, ses)
        else:
            clear_terminal() 
            print("Фильм не найден")


def get_film_name():
    ua = UserAgent()
    clear_terminal() 
    main_page = 'https://kinogo.la'
    cnt = 0
    r = None
    film_name = input('Введите название фильма: ').lower().strip() 
    for i in get_proxies_list():
        cnt+=1
        try:
            r, session = get_main_page(main_page, i, ua.random)
        except: print(f'Сервер {i} не доступен'); sleep(1); clear_terminal()

        if r is not None:
            try:
                search_film(session, film_name)
                break
            except:
                clear_terminal()
                print('ОШИБКА!\nПопробуйте повторить запрос')
                break


def main():
    clear_terminal()
    while True:
        while True:
            try:
                command = int(input('Введите номер команды: \n1: Найти фильм\n2: Обновить proxy\n3: Выход\n'))
                break
            except:
                clear_terminal()
                print('Некорректная команда')
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
            print('Некорректная команда')


if __name__ == '__main__':
    main()
