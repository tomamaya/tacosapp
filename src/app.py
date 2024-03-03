#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 14:22:20 2024

@author: tomamaya
"""

import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import folium
from folium.plugins import MarkerCluster

#read csv data

df = pd.read_csv("places-of-taqueria-in-japan1.csv")
df_cor= df[["coordinatex","coordinatey","name","rating","reviews"]]
cor_list=[]
info_list=[]

for i in df_cor.index:
    #print(df_cor["coordinatex"][i],df_cor["coordinatey"][i])
    cor_list.append((df_cor["coordinatex"][i],df_cor["coordinatey"][i]))
    info_list.append((df_cor["name"][i],df_cor["rating"][i],df_cor["reviews"][i]))

# Create a DataFrame for easy filtering
import pandas as pd
df = pd.DataFrame({
    'Coordinates': cor_list,
    'Name': [info[0] for info in info_list],
    'Rating': [info[1] for info in info_list],
    'Review': [info[2] for info in info_list]
})
# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Define the layout of the app
app.layout = html.Div([
    html.H1('Taquerias en Japon', style={'textAlign': 'center', 'color': '#503D36','font-size': 30}),
    html.Label("Filtrar por Rating"),
    dcc.RangeSlider(
        id='rating-slider',
        min=df['Rating'].min(),
        max=df['Rating'].max(),
        marks={i: str(i) for i in range(int(df['Rating'].min()), int(df['Rating'].max())+1)},
        value=[df['Rating'].min(), df['Rating'].max()],
    ),
    html.Label("Filtrar por # de Reviews"),
    dcc.RangeSlider(
        id='review-slider',
        min=df['Review'].min(),
        max=df['Review'].max(),
        marks={i: str(i) for i in range(int(df['Review'].min()), int(df['Review'].max())+1, 500)},
        value=[df['Review'].min(), df['Review'].max()],
    ),
    html.Div(id='map-container'),
    html.H1('by A&T Consulting LLC', style={'textAlign': 'center', 'color': '#503D36','font-size': 30})
])

# Define callback to update the map based on filters
@app.callback(
    Output('map-container', 'children'),
    [Input('rating-slider', 'value'),
     Input('review-slider', 'value')]
)
def update_map(selected_rating, selected_review):
    filtered_df = df[(df['Rating'] >= selected_rating[0]) & (df['Rating'] <= selected_rating[1])]
    
    if selected_review:
        filtered_df = filtered_df[(filtered_df['Review'] >= selected_review[0]) & (filtered_df['Review'] <= selected_review[1])]

    # Create a folium Map centered at the mean of all coordinates
    map_center = [sum(coord[0] for coord in filtered_df['Coordinates']) / len(filtered_df),
                  sum(coord[1] for coord in filtered_df['Coordinates']) / len(filtered_df)]

    my_map = folium.Map(location=map_center, zoom_start=5)

    # Create a MarkerCluster layer
    marker_cluster = MarkerCluster().add_to(my_map)

    # Add markers for each coordinate to the MarkerCluster layer
    for index, row in filtered_df.iterrows():
        coord = row['Coordinates']
        name, rating, review = row['Name'], row['Rating'], row['Review']

        # Create a popup with information
        popup_text = f"Name: {name}<br>Rating: {rating}<br>Review: {review}"
        popup = folium.Popup(popup_text, parse_html=True)

        # Add the marker with the popup to the MarkerCluster layer
        folium.Marker(location=coord, popup=popup).add_to(marker_cluster)

    return html.Iframe(srcDoc=my_map._repr_html_(), width='100%', height='600px')


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)