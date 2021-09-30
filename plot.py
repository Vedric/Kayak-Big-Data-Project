import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
import plotly.express as px
import plotly.io as pio
import plotly.offline as pyo
import os
import webbrowser


config = {
    "host": 'database-kyk.ccanbdkrmcd9.eu-west-3.rds.amazonaws.com',
    "user": 'admin',
    "passwd": 'Azerty789.',
    'db_name': 'data_kayak'
}

cnx = mysql.connector.connect(
    host=config["host"],
    user=config["user"],
    password=config["passwd"])

engine = create_engine('mysql+mysqlconnector://{}:{}@{}/{}'.format(config["user"], config["passwd"], config["host"],
                                                                   config["db_name"]))

cursor = cnx.cursor()
cursor.execute("USE {}".format(config["db_name"]))

df_good_weather_hotels = pd.read_sql('SELECT * FROM good_weather_hotels', con=cnx)
df_weather_hotels = pd.read_sql('SELECT * FROM weather_hotels', con=cnx)

token = "pk.eyJ1IjoidmVkcmljIiwiYSI6ImNrdTRmcWtlZjM4eXEycHF0aXptOGQ1eGIifQ.ERt5JGuQBhuzV2CXfn6mfQ"
token = "pk.eyJ1IjoidmVkcmljIiwiYSI6ImNrdTRmbmszbTFlMmMyb28xcWd4MGszZ3YifQ.icVXSxMkoUbkBsLqdJhaAg"


# TOP_5 plot : get 5 destination where the weather will be the best (criteria = max temperature)
df_top_5_dest = df_weather_hotels[
                    ["city", "mean_tmax", 'city_latitude', 'city_longitude']].drop_duplicates().sort_values(
    by="mean_tmax", ascending=False).iloc[:5]


pyo.init_notebook_mode()  # Set notebook mode to work in offline

px.set_mapbox_access_token(token)
fig1 = px.scatter_mapbox(df_top_5_dest, lat="city_latitude", lon="city_longitude", color="mean_tmax",
                         text='city', size='mean_tmax', title='Top 5 Cities by temperatures for the next 7 days',
                         width=1000, height=600, mapbox_style="carto-positron", zoom=4.3,
                         color_continuous_scale='Bluered', )

a = fig1.to_html()


html = a
path = os.path.abspath('temp.html')
url = 'file://' + path

with open(path, 'w') as f:
    f.write(html)
webbrowser.open(url)

# plot top 20 hotels
df_top_20 = df_good_weather_hotels.sort_values(by="hotel_rating", ascending=False).loc[:20][["city", 'hotel_name',
                                                                                             'hotel_rating',
                                                                                             'hotel_price', 'hotel_lat',
                                                                                             'hotel_long']]

l_html_figs = []  # It will contains our charts
for i, city in enumerate(df_top_20['city'].unique()):
    myhotels = df_top_20.loc[df_top_20['city'] == city]
    fig = px.scatter_mapbox(myhotels,
                            lon="hotel_long",
                            lat="hotel_lat",
                            color="hotel_rating",
                            text='city',
                            size='hotel_rating',
                            title='Top Hotels in the city ' + city,
                            width=1000, height=600,
                            mapbox_style="carto-positron",
                            zoom=12,
                            color_continuous_scale='aggrnyl')

    html_code = fig.to_html()
    l_html_figs.append(html_code)

    path = os.path.abspath('temp_{}.html'.format(i))
    url = 'file://' + path

    with open(path, 'w') as f:
        f.write(html_code)

    webbrowser.open(url)
