import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import random
from map import Map
from dataset import DataSet
import datetime

from st_audiorec import st_audiorec

from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client

st. set_page_config(layout="wide")

# Initialize connection
db: Client = create_client(st.secrets["SUPABASE_URL"], 
                                st.secrets["SUPABASE_KEY"])

TIMES = ("morning", "afternoon", "evening", "night")
CLASSES = ("dog_bark", "children_playing", "air_conditioner", "street_music", "engine_idling", "jackhammer", "drilling", "siren", "car_horn")

dataset = DataSet(db)
    
# dataset.df

map = Map(dataset, 1, CLASSES, TIMES)
deck = map.deck

container = st.container()

col1, col2 = container.columns([1, 2.2])




date = col1.date_input("Date", datetime.date(2024, 5, 24))
all_data = col1.checkbox("All dates")

if(not all_data):
   dataset.set_df_by_date(date)

time_select = col1.multiselect(
    "Parts of day",
    TIMES, default=TIMES)

classes_select = col1.multiselect(
    "Classes",
    CLASSES, default=CLASSES)

if col1.button('Update map'):
    map.updateMap(classes_select, time_select) 

col2.pydeck_chart(deck)




def get_metrics(count_now, count_on_date, label):
    return st.metric(label=label, value = count_now, delta = count_now - count_on_date,
        delta_color="inverse")


metrics_container = st.container()

date1, date2 = metrics_container.columns([1, 1])

date_compare = date1.date_input("Compare", datetime.date(2024, 5, 24))
date_with = date2.date_input("with", datetime.date(2024, 5, 20))

with metrics_container:
    get_metrics(dataset.get_count_by_date(date_compare), dataset.get_count_by_date(date_with), "Noise")

metr1, metr2, metr3 = metrics_container.columns([1, 1, 1])

with metr1:
    get_metrics(dataset.get_count_by_date_class(date_compare, "dog_bark"), dataset.get_count_by_date_class(date_with,"dog_bark"), "dog_bark")
    get_metrics(dataset.get_count_by_date_class(date_compare, "street_music"), dataset.get_count_by_date_class(date_with,"street_music"), "street_music")
    get_metrics(dataset.get_count_by_date_class(date_compare, "engine_idling"), dataset.get_count_by_date_class(date_with,"engine_idling"), "engine_idling")
with metr2:
    get_metrics(dataset.get_count_by_date_class(date_compare, "children_playing"), dataset.get_count_by_date_class(date_with,"children_playing"), "children_playing")
    get_metrics(dataset.get_count_by_date_class(date_compare, "jackhammer"), dataset.get_count_by_date_class(date_with,"jackhammer"), "jackhammer")
    get_metrics(dataset.get_count_by_date_class(date_compare, "drilling"), dataset.get_count_by_date_class(date_with,"drilling"), "drilling")
with metr3:
    get_metrics(dataset.get_count_by_date_class(date_compare, "air_conditioner"), dataset.get_count_by_date_class(date_with,"air_conditioner"), "air_conditioner")
    get_metrics(dataset.get_count_by_date_class(date_compare, "siren"), dataset.get_count_by_date_class(date_with,"siren"), "siren")
    get_metrics(dataset.get_count_by_date_class(date_compare, "car_horn"), dataset.get_count_by_date_class(date_with,"car_horn"), "car_horn")



tb_counts = dataset.get_filtered_data(CLASSES, TIMES)

tb_counts


sound_container = st.container()
with sound_container:
    wav_audio_data = st_audiorec()




css='''
/*center metric label*/
[data-testid="stMetric"] {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%; /* Ensure the container takes up the full height */
        text-align: center; /* Center text horizontally */
        flex-direction: column;
    }
    [data-testid="stMetric"] > div:nth-child(1) {
        margin-bottom: 5px; /* Optional: Add some spacing between "Noise" and the numbers */
        padding-right: 50px;
    }
'''

# I usually dump any scripts at the bottom of the page to avoid adding unwanted blank lines
col1.markdown(f'<style>{css}</style>',unsafe_allow_html=True)