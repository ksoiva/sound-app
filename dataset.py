import pandas as pd
from datetime import datetime, time
import streamlit as st

CLASSES = ("dog_bark", "children_playing", "air_conditioner", "street_music", "engine_idling", "jackhammer", "drilling", "siren", "car_horn")

class DataSet:
    def __init__(self, db):

        self.db = db
        response = db.table('sound_count_view').select("*").execute()

        self.tb = pd.DataFrame(response.data)

    
    def get_filtered_data(self, classes, times):

        classes = list(classes)

        # Create an empty DataFrame to store the results
        filtered_df = pd.DataFrame(columns=['latitude', 'longitude'] + list(CLASSES))

        # Filter the DataFrame by the given classes
        filtered_df[['latitude', 'longitude', 'time_period']] = self.tb[['latitude', 'longitude', 'time_period']]

        for class_name in classes:
            filtered_df[class_name] = self.tb[class_name]

        # Filter DataFrame by time periods
        filtered_df = filtered_df[filtered_df['time_period'].isin(times)]

        # Group by latitude and longitude, summing occurrences of each class
        result_df = filtered_df.groupby(['latitude', 'longitude'])[list(CLASSES)].sum().reset_index()

        result_df['total'] = result_df[classes].sum(axis=1)

        min_count = result_df['total'].min()
        max_count = result_df['total'].max()

        def fill_color(total):
            color_range = [[26,152,80],[145,207,96],[217,239,139],[254,224,139],[252,141,89],[215,48,39]]

            normalized_total = (total - min_count) / (max_count - min_count)

            color_index = int(normalized_total * (len(color_range) - 1))
            return color_range[color_index] + [255] 


        result_df['fill_color'] = result_df['total'].apply(fill_color)

        result_df['total_normal'] = (result_df['total'] - min_count+10) / (max_count - min_count)

        return result_df
    

    def get_count_by_date(self, date):
        response = self.db.table('sound').select("count").eq("date", date).execute()
        return response.data[0]["count"]
    
    def get_count_by_date_class(self, date, class_name):
        classes = self.db.table('class').select("*").execute().data
        class_id = [class_item['id'] for class_item in classes if class_item['name'] == class_name][0]
        response = self.db.table('sound').select("count").eq("date", date).eq("class_id", class_id).execute()
        return response.data[0]["count"]
    
    def set_df_by_date(self, date):
        response = self.db.table('sound_count_view').select("*").eq("date", date).execute()

        self.tb = pd.DataFrame(response.data)