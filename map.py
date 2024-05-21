import pydeck as pdk

class Map:
    def __init__(self, dataset, opacity, classes, times):
        self.data = dataset
        self.opacity = opacity

        self.deck = pdk.Deck(
            map_style="mapbox://styles/mapbox/streets-v11",
            initial_view_state=pdk.ViewState(
            latitude = 49.8397,
            longitude = 24.0297,
            zoom = 12.5,
            pitch = 50,
            bearing = 0,
        ),
        layers=[
            pdk.Layer(
                'GridCellLayer',     # Change the `type` positional argument here
                self.data.get_filtered_data(classes, times),
                get_position = ['longitude', 'latitude'],
                elevation_scale = 400,
                get_elevation = 'total_normal',
                auto_highlight = True,
                opacity = 1,
                cellSize = 35,          # Radius is given in meters
                get_fill_color ='fill_color',  # Set an RGBA value for fill
                pickable = True
            )
        ],
        tooltip= {
            "html": "<b>Location:</b> {longitude}, {latitude}<br>"
                  +"<b>Sounds:</b> {total}<br>"
                  + "<b>dog bark:</b>    {dog_bark}<br>"
                  + "<b>clidren play:</b>    {children_playing}<br>"
                  + "<b>air conditioner:</b>    {air_conditioner}<br>"
                  + "<b>street music:</b>    {street_music}<br>"
                  + "<b>engine idling:</b>    {engine_idling}<br>"
                  + "<b>jackhammer:</b>    {jackhammer}<br>"
                  + "<b>drilling:</b>    {drilling}<br>"
                  + "<b>siren:</b>    {siren}<br>"
                  + "<b>car horn:</b>    {car_horn}",
            "style": {
                    "backgroundColor": "white",
                    "color": "grey"
            }
            }
        )

    def updateMap(self, classes, times):
        filtered_df = self.data.get_filtered_data(classes, times)
        self.deck.layers[0].data = filtered_df
        return filtered_df
    

        