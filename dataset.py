import pandas as pd
from datetime import datetime, time
import streamlit as st

class DataSet:
    def __init__(self, filepath):
        self.df = pd.read_csv(filepath)
        
    
    def get_counts_df(self, classes, times):

        times_dict = {
            'morning': [(5, 0), (12, 0)],
            'afternoon': [(12, 0), (17, 0)],
            'evening': [(17, 0), (21, 0)],
            'night': [(21, 0), (5, 0)] 
        }

        filtered_data = self.df[self.df['class'].isin(classes)]

        time_columns = pd.to_datetime(self.df['time'])

        time_filtered_data = pd.DataFrame()
        for time_range in times:
            start_time, end_time = times_dict[time_range]

            if time_range == 'night':
                mask = (time_columns.dt.hour >= start_time[0]) & (time_columns.dt.hour < 24)  | \
                    (time_columns.dt.hour < end_time[0]) & (time_columns.dt.hour >= 0)
            else:
                mask = (time_columns.dt.hour >= start_time[0]) & \
                    (time_columns.dt.hour < end_time[0])
            time_filtered_data = pd.concat([time_filtered_data, filtered_data[mask]])


        grouped_df = time_filtered_data.groupby(['longitude', 'latitude', 'class']).size().reset_index(name='count')

        counts_df = grouped_df.pivot_table(index=['longitude', 'latitude'], columns='class', values='count', fill_value=0).reset_index()
        counts_df['total'] = counts_df.iloc[:, 2:].sum(axis=1)

        self.min_count = counts_df['total'].min()
        self.max_count = counts_df['total'].max()
        counts_df['fill_color'] = counts_df['total'].apply(self.get_fill_color)

        counts_df['total_normal'] = (counts_df['total'] - self.min_count+0.5) / (self.max_count - self.min_count)
        return counts_df


    def get_fill_color(self,total):
        color_range = [[237,248,251],[191,211,230],[158,188,218],[140,150,198],[136,86,167],[129,15,124]]

        normalized_total = (total - self.min_count) / (self.max_count - self.min_count)

        color_index = int(normalized_total * (len(color_range) - 1))
        return color_range[color_index] + [255] 
    