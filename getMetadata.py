import requests
from bs4 import BeautifulSoup
import webbrowser

url = 'https://onlinelibrary.wiley.com/doi/full/10.1002/anie.201504227'
req_head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
response = requests.get(url, headers = req_head)
soup = BeautifulSoup(response.text,'html.parser')

metas = soup.find_all('meta')

f = open('response_metas.txt','w')
for meta in metas:
    if 'content' in meta.attrs.keys() and len(meta.attrs['content'])< 250:
        f.write(str(meta))
    
f.close()

f = open('response_page.html','w')

message = response.text

f.write(message)
f.close()

paras = soup.find_all('p')
heywords=['funding', "thank", "acknowledge", "grant"]
likely = 0
for para in paras:
    for keyword in heywords:
        if keyword in str(para).lower():
            likely += 1
    if likely > 0:
        print(str(para))
        likely = 0

