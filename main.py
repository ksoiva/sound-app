import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import random
from map import Map
from dataset import DataSet

from st_audiorec import st_audiorec

from st_supabase_connection import SupabaseConnection

st. set_page_config(layout="wide")

# Initialize connection.
conn = st.connection("supabase",type=SupabaseConnection)

TIMES = ("morning", "afternoon", "evening", "night")
CLASSES = ("dog_bark", "children_playing", "air_conditioner", "street_music", "engine_idling", "jackhammer", "drilling", "siren", "car_horn")

dataset = DataSet("prepared_data.csv")
# dataset.df

map = Map(dataset, 1, CLASSES, TIMES,)
deck = map.deck

container = st.container()

col1, col2 = container.columns([1, 2.2])

time_select = col1.multiselect(
    "Parts of day",
    TIMES, default=TIMES)

classes_select = col1.multiselect(
    "Classes",
    CLASSES, default=CLASSES)

if col1.button('Update map'):
    map.updateMap(classes_select, time_select) 

col2.pydeck_chart(deck)


with col1:
    sound_container = st.container()
    col1_sound, col2_sound = sound_container.columns([1, 2])
    with sound_container:
        wav_audio_data = st_audiorec()

dataset.df