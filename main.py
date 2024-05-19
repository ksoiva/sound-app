import streamlit as st
import pandas as pd
import datetime

from st_audiorec import st_audiorec
from supabase import create_client, Client

from map import Map
from dataset import DataSet
from standart_model import StandartModel
from neural_network import NeuralNetwork

st. set_page_config(layout="wide")

db: Client = create_client(st.secrets["SUPABASE_URL"], 
                                    st.secrets["SUPABASE_KEY"])

TIMES = ("morning", "afternoon", "evening", "night")
if 'classes' not in st.session_state or st.session_state.classes is None:
        st.session_state.classes = pd.DataFrame(db.table("class").select("*").execute().data)
CLASSES = st.session_state.classes


def get_dataset():
    dataset = DataSet(db)
    st.session_state.dataset = dataset 
    return st.session_state.dataset


def create_map(dataset):
    map = Map(dataset, 1, list(CLASSES["name"]), TIMES)
    if 'map' not in st.session_state or st.session_state.map is None:
        st.session_state.map = map
    return st.session_state.map

def main(): 

    tb = get_dataset()

    #MAP BLOCK

    map = create_map(tb)
    deck = map.deck

    container = st.container()
    container.header('Sound Map', divider='red')

    col1, col2 = container.columns([1, 2.2])

    form_map = col1.form('parameters_form')

    with form_map:
        date = st.date_input("Date", datetime.date(2024, 5, 24))
        all_data = st.checkbox("All dates", value = True)

        if(not all_data):
            tb.set_df_by_date(date)

        time_select = st.multiselect(
            "Parts of day",
            TIMES, default=TIMES)

        classes_select = st.multiselect(
            "Classes",
            CLASSES["name"], default=CLASSES["name"])

        if st.form_submit_button('Update map'):
            map.updateMap(classes_select, time_select)
            st.session_state.map = map
            deck = st.session_state.map.deck
    
    col2.pydeck_chart(deck)


    #SOUND CLASSIFICATION BLOCK

    standart_model = StandartModel()

    neural_network = NeuralNetwork()

    sound_container = st.container()

    sound_container.header('Classification', divider='red')
    

    form_class = sound_container.form('classification_form')

    with form_class:

        classf1,d1, classf2,d2, classf3 = st.columns([3, 1, 3, 1, 3])

        with classf1:
            st.subheader("Record your sounds")
            wav_audio_data = st_audiorec()
            if 'sound_record' not in st.session_state or st.session_state.sound_record is None:
                st.session_state.sound_record = classf1

        with classf2:
            st.subheader("Choose the model")
            model = st.selectbox(
            "Model:",
            ("XGBClassifier", "Neural network"),
            index=None,
            label_visibility='collapsed',
            placeholder="Select model..."
        )

        with classf3:
            st.subheader("Get the results")
            if st.form_submit_button('Classify'):
                class_results = standart_model.classify(wav_audio_data)
                st.session_state.class_results = class_results
            if 'class_results' in st.session_state:
                st.session_state.class_results





    #STATISTICS BLOCK

    def get_metrics(count_now, count_on_date, label):
        return st.metric(label=label, value = count_now, delta = count_now - count_on_date,
            delta_color="inverse")

    statistic_container = st.container()

    statistic_container.header('Data', divider='red')
    c1, metrics_container, c2 = statistic_container.columns([1, 3, 1])


    date1, date2 = metrics_container.columns([1, 1])

    date_compare = date1.date_input("Compare", datetime.date(2024, 5, 24))
    date_with = date2.date_input("with", datetime.date(2024, 5, 20))

    with metrics_container:
        get_metrics(tb.get_count_by_date(date_compare), tb.get_count_by_date(date_with), "Noise")

    metr1, metr2, metr3 = metrics_container.columns([1, 1, 1])

    # Розрахунок розміру кожного підсписку
    n = len(CLASSES["name"]) // 3
    remainder = len(CLASSES["name"]) % 3

    # Індекси для підсписків
    end1 = n + (1 if remainder > 0 else 0)
    end2 = end1 + n + (1 if remainder > 1 else 0)

    # Розподіл на підсписки
    classes_metr1 = CLASSES["name"][:end1]
    classes_metr2 = CLASSES["name"][end1:end2]
    classes_metr3 = CLASSES["name"][end2:]

    def process_metrics(metr, classes):
        with metr:
            for cls in classes:
                get_metrics(
                    tb.get_count_by_date_class(date_compare, cls),
                    tb.get_count_by_date_class(date_with, cls),
                    cls
                )

    # Обробка підсписків
    process_metrics(metr1, classes_metr1)
    process_metrics(metr2, classes_metr2)
    process_metrics(metr3, classes_metr3)


    statistic_container.divider()

    form_data = statistic_container.form('dataset_form')
    with form_data:
        st.dataframe(tb.data, use_container_width = True)
        if st.form_submit_button('Update'):
            get_dataset()

    
        

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
  

    
  
# Using the special variable  
# __name__ 
if __name__=="__main__": 
    main() 