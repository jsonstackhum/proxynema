import requests
from bs4 import BeautifulSoup


def get_page():
	url = 'https://free-proxy-list.net'
	r = requests.get(url)
	return r


def write_to_file(text):
	with open('my_proxy.txt', 'w') as f:
		f.write(text)


def get_proxy(r)->str:
	soup = BeautifulSoup(r.text, 'lxml')
	div = soup.find_all('tr')
	cnt=0
	lines = ''
	for i in div:
		cnt+=1
		td = i.find_all('td')
		if len(td) > 0:
			IP = td[0].text
			PORT = td[1].text
			CODE = td[2].text
			COUNTRY = td[3].text
			ANON = td[4].text
			GOOGLE = 'google+' if td[5].text == 'yes' else 'google-'
			HTTPS = 'https' if td[6].text == 'yes' else 'http' 
			LAST_CHECKED = td[7].text
			lines += f'{IP}:{PORT} {CODE} {COUNTRY} {ANON} {GOOGLE} {HTTPS} {LAST_CHECKED}\n'

		if cnt == 301:
			return lines


def https_to_file():
	cnt = 0
	with open('https_proxy.txt', 'w') as f:
		with open('my_proxy.txt', 'r') as all_proxy:
			text = all_proxy.readlines()
			for i in text:
				if 'https' in i:
					cnt+=1
					f.writelines(i.split()[0]+'\n')
		print(f'Получено {cnt} Https прокси')


def update_proxy():
	write_to_file(get_proxy(get_page()))
	https_to_file()


def main():
	update_proxy()


if __name__ == '__main__':
	main()
