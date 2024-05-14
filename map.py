import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import colorsys

class Map:
    def __init__(self, dataset, opacity, classes, times):
        self.data = dataset
        self.opacity = opacity

        self.deck = pdk.Deck(
            map_style="mapbox://styles/mapbox/streets-v11",
            initial_view_state=pdk.ViewState(
            latitude = 49.8397,
            longitude = 24.0297,
            zoom = 11,
            pitch = 50,
            bearing = 0,
            height = 600
        ),
        layers=[
            pdk.Layer(
                'GridCellLayer',     # Change the `type` positional argument here
                self.data.get_counts_df(classes, times),
                get_position = ['longitude', 'latitude'],
                elevation_scale = 500,
                get_elevation = 'total_normal',
                auto_highlight = True,
                opacity = 1,
                cellSize = 35,          # Radius is given in meters
                get_fill_color ='fill_color',  # Set an RGBA value for fill
                pickable = True
            )
        ],
        tooltip={"text": "Sounds: {total}\n" },
        )

    def updateMap(self, classes, times):
        filtered_df = self.data.get_counts_df(classes, times)
        self.deck.layers[0].data = filtered_df
        