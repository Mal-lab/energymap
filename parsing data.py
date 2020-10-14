import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
#Получение ссылок на каждый объект электроэнергетики
#Выполняется отдельно для каждого фильтра
def get_refs(number_of_pages,url_of_page): #41 для фильтра по Центральному федеральному округу (ПС)
  list_of_refs = []
  for page_number in range(1, number_of_pages + 1):
    url  = url_of_page[:-1] + str(page_number)
    page = requests.get(url)
    new_soup = BeautifulSoup(page.content,'html.parser')
    attempt = new_soup.find_all('div',{'class':'name'})
    for stroka in attempt:
      list_of_refs.append(str(stroka.find('a').get('href')))
  return list_of_refs
#Получение данных по заданному фильтру
list_of_refs = get_refs(8, 'https://energybase.ru/power-plant/index?PowerPlantSearch%5Bcountry_id%5D=&PowerPlantSearch%5Bdistrict_id%5D=28&PowerPlantSearch%5Bname%5D=&PowerPlantSearch%5Btype_name%5D=&PowerPlantSearch%5Bcity_id%5D=&PowerPlantSearch%5Bstate%5D=&page=1')
k = 0
data = {}
for ref in list_of_refs:
  print('progress:',k+1,'/',len(list_of_refs))
  url = 'https://energybase.ru' + ref
  page = requests.get(url)
  #Download page
  soup = BeautifulSoup(page.content,'html.parser')
  name_of_substation = soup.title.string
  latitude = soup.find_all(string=re.compile('Широта',flags = re.I))
  longitude = soup.find_all(string=re.compile('Долгота',flags = re.I))
  if len(latitude) > 0 or len(longitude) > 0:
    latitude = float(latitude[0].replace('Широта: ',''))
    longitude = float(longitude[0].replace('Долгота: ',''))
  data[name_of_substation] = {'Широта':latitude, 'Долгота':longitude, 'Ссылка':url}
  name_of_substation
  k += 1
  exporting_data = pd.DataFrame(data).T
  exporting_data.to_excel('data.xlsx')