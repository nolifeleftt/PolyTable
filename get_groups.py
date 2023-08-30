from bs4 import BeautifulSoup
import requests


url = 'https://ruz.spbstu.ru'
response = requests.get(url)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'lxml')
inst = soup.find_all('a', class_='faculty-list__link')
d = {}
for i in inst:
    url_2 = url + i['href']
    response = requests.get(url_2)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    l = soup.find_all('a', class_='groups-list__link')
    for link in l:
        d[link.text] = link['href'].split('/')[-1]
        #print(link.text, '---', link['href'])
with open('groups.txt','w') as out:
    for key,val in d.items():
        out.write('{}:{}\n'.format(key,val))