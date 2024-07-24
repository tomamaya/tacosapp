import pandas as pd
import dash
from dash import dcc, html, Input, Output
from dash.dash_table import DataTable
import folium
from folium.plugins import MarkerCluster

# Read csv data
df = pd.read_csv("places-of-taqueria-in-japan2.csv")

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Define the layout of the app
app.layout = html.Div([
    html.H1('Taquerias en Japon -Proyecto Tacos el Pata Japon-', style={'textAlign': 'center', 'color': '#503D36', 'font-size': 30}),
    
    html.Label("Filtrar por Rating"),
    dcc.RangeSlider(
        id='rating-slider',
        min=df['rating'].min(),
        max=df['rating'].max(),
        marks={i: str(i) for i in range(int(df['rating'].min()), int(df['rating'].max()) + 1)},
        value=[df['rating'].min(), df['rating'].max()],
    ),
    
    html.Label("Filtrar por # de Reviews"),
    dcc.RangeSlider(
        id='review-slider',
        min=df['reviews'].min(),
        max=df['reviews'].max(),
        marks={i: str(i) for i in range(int(df['reviews'].min()), int(df['reviews'].max()) + 1, 500)},
        value=[df['reviews'].min(), df['reviews'].max()],
    ),
    
    html.Div(id='map-and-search-container', children=[
        html.Div(id='map-container'),
    ]),
    
    html.H1('Datos Generales', style={'textAlign': 'center', 'color': '#503D36', 'font-size': 30}),
    
    html.Div([
        DataTable(
            id='data-table',
            columns=[
                {'name': 'Nombre en Japones', 'id': 'name'},
                {'name': 'Nombre en Espanol', 'id': 'name_2'},
                {'name': 'Direccion en Japones', 'id': 'address'},
                {'name': 'Direccion en Espanol', 'id': 'address_2'},
                {'name': 'Rating', 'id': 'rating'},
                {'name': 'Reviews', 'id': 'reviews'},
                {'name': 'Webpage', 'id': 'webpage'}
            ],
            page_size=10,  # Number of rows per page
            style_table={'overflowX': 'auto'},
            sort_action='native',  # Enables sorting
            sort_mode='multi',  # Allows multi-column sorting
            filter_action='native',  # Enables filtering
        ),
    ]),
    
    html.Div(id='search-container', children=[
        html.Label('Buscar por nombre de restaurante:'),
        dcc.Input(id='name-search-input', type='text', placeholder='Buscar por Nombre en Espanol'),
    ]),
    
    html.Footer("Hecho por Japano ©", style={'textAlign': 'center', 'color': '#503D36', 'font-size': 14}),
])

# Callback to update the map and data table based on filters and search
@app.callback(
    [Output('map-container', 'children'),
     Output('data-table', 'data')],
    [Input('rating-slider', 'value'),
     Input('review-slider', 'value'),
     Input('name-search-input', 'value')]
)
def update_map_and_table(selected_rating, selected_review, search_value):
    filtered_df = df[(df['rating'] >= selected_rating[0]) & (df['rating'] <= selected_rating[1])]
    
    if selected_review:
        filtered_df = filtered_df[(filtered_df['reviews'] >= selected_review[0]) & (filtered_df['reviews'] <= selected_review[1])]

    # Update table based on search in name_2 column
    if search_value:
        filtered_df = filtered_df[filtered_df['name_2'].str.contains(search_value, case=False, na=False)]

    # Create a folium Map centered at the mean of all coordinates
    map_center = [filtered_df['coordinatex'].mean(), filtered_df['coordinatey'].mean()]
    my_map = folium.Map(location=map_center, tiles="OpenStreetMap", zoom_start=5)

    # Create a MarkerCluster layer
    marker_cluster = MarkerCluster().add_to(my_map)

    # Add markers for each coordinate to the MarkerCluster layer
    for index, row in filtered_df.iterrows():
        coord = (row['coordinatex'], row['coordinatey'])
        name_jp = row['name']
        name_es = row['name_2']
        address_jp = f"{row['address']} {row['address_2']}"
        address_es = row['address_2']
        rating = row['rating']
        reviews = row['reviews']
        webpage = row['webpage']

        # Create popup with information
        popup_text = f"<b>Nombre en Japones:</b> {name_jp}<br>" \
                     f"<b>Nombre en Espanol:</b> {name_es}<br>" \
                     f"<b>Direccion en Japones:</b> {address_jp}<br>" \
                     f"<b>Direccion en Espanol:</b> {address_es}<br>" \
                     f"<b>Rating:</b> {rating}<br>" \
                     f"<b>Reviews:</b> {reviews}<br>" \
                     f"<b>Webpage:</b> <a href='{webpage}' target='_blank'>{webpage}</a>"

        # Create a Marker for each point, with the popup
        folium.Marker(location=coord, popup=folium.Popup(html=popup_text, max_width=300)).add_to(marker_cluster)

    # Return the map and filtered data for the data table
    return html.Iframe(srcDoc=my_map._repr_html_(), width='100%', height='600px'), filtered_df.to_dict('records')

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
