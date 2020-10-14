import folium
from folium.plugins import MarkerCluster, Search, BeautifyIcon
import pandas as pd
from geojson import Feature, FeatureCollection, Point
import json
###Экспорт данных в GeoJson для использования в картах
#Для подстанций
df = pd.read_excel('data.xlsx')
features = df.apply(
    lambda row: Feature(properties={'name':row['Unnamed: 0'], 'ref':row['Ссылка'], 'Unom':row['Номинальное напряжение']}, geometry=Point((float(row['Долгота']), float(row['Широта'])))),
    axis=1).tolist()
feature_collection = FeatureCollection(features=features)
with open('file.geojson', 'w', encoding='utf-8') as f:
  json.dump(feature_collection, f, ensure_ascii = False)
#Для объектов генерации
df_gen = pd.read_excel('gen_data.xlsx')
features_gen = df_gen.apply(
    lambda row: Feature(properties={'name':row['Unnamed: 0'], 'ref':row['Ссылка']}, geometry=Point((float(row['Долгота']), float(row['Широта'])))),
    axis=1).tolist()
feature_collection_gen = FeatureCollection(features=features_gen)
with open('file_gen.geojson', 'w', encoding='utf-8') as f:
  json.dump(feature_collection_gen, f, ensure_ascii = False)
#Построение карты
def color_change(Unom):
  U = [1150, 800, 750, 500, 400, 330, 220, 150, 110, 35, 20, 10, 6]
  colors = ['#CD8AFF', '#0000C8', '#0000C8', '#A50F0A', '#F0961E', '#008C00', '#C8C800', '#AA9600', '#00B4C8', '#826432', '#826432', '#640064', '#C89664']
  Unom_colors = dict(zip(U,colors))
  if Unom not in U:
      return 'black'
  return Unom_colors[Unom]


m = folium.Map(location=[63, 92], zoom_start=4)
marker_cluster = MarkerCluster(name='Objects').add_to(m)
#Создание слоев для ПС и генерации из geojson
layer = folium.GeoJson(
    feature_collection,
    name='PS',
    show=False
).add_to(m)

layer_gen = folium.GeoJson(
    feature_collection_gen,
    name='Generation',
    show=False
).add_to(layer)

gj = folium.GeoJson('file.geojson')
#Создание маркеров
for feature in gj.data['features']:
    if feature['geometry']['type'] == 'Point':
        folium.CircleMarker(
            location=list(reversed(feature['geometry']['coordinates'])),
            color='grey',
            fill_color=color_change(feature['properties']['Unom']),
            fill_opacity=1,
            popup=folium.Popup(feature['properties']['name'] + '<p><a href=' + feature['properties'][
                'ref'] + '>Ссылка на energybase.ru</a><p>', max_width=200),
        ).add_to(marker_cluster)

gj_gen = folium.GeoJson('file_gen.geojson')
for feature in gj_gen.data['features']:
    if feature['geometry']['type'] == 'Point':
        icon = BeautifyIcon(
            icon='adjust',
            inner_icon_style='color:black;font-size:30px;',
            background_color='transparent',
            border_color='transparent',
        )
        folium.Marker(
            location=list(reversed(feature['geometry']['coordinates'])),
            icon=icon,
            popup=folium.Popup(feature['properties']['name'] + '<p><a href=' + feature['properties'][
                'ref'] + '>Ссылка на energybase.ru</a><p>', max_width=200),
        ).add_to(marker_cluster)
#Добавление строки поиска
substation_search = Search(layer=layer,
                           geom_type='Point',
                           placeholder='Search',
                           search_label='name',
                           search_zoom=11
                           ).add_to(m)
folium.LayerControl().add_to(m)
m.save('map.html')