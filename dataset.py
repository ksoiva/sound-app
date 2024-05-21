import pandas as pd
import numpy as np
from datetime import datetime

class DataSet:
    def __init__(self, db, classes):

        self.db = db
        response = db.table('sound_count_view').select("*").execute()
        self.CLASSES = classes

        self.tb = pd.DataFrame(response.data)
        self.data = pd.DataFrame(db.table("dataset_view").select("*").execute().data)

    
    def get_filtered_data(self, classes, times):

        classes = list(classes)

        # Create an empty DataFrame to store the results
        filtered_df = pd.DataFrame(columns=['latitude', 'longitude'] + list(self.CLASSES["name"]))

        # Filter the DataFrame by the given classes
        filtered_df[['latitude', 'longitude', 'time_period', 'date']] = self.tb[['latitude', 'longitude', 'time_period', 'date']]

        for class_name in classes:
            filtered_df[class_name] = self.tb[class_name]

        # Filter DataFrame by time periods
        filtered_df = filtered_df[filtered_df['time_period'].isin(times)]

        # Group by latitude and longitude, summing occurrences of each class
        result_df = filtered_df.groupby(['latitude', 'longitude'])[list(self.CLASSES["name"])].sum().reset_index()

        result_df['total'] = result_df[classes].sum(axis=1)

        min_count = result_df['total'].min()
        max_count = result_df['total'].max()

        def fill_color(total):
            color_range = [[26,152,80],[145,207,96],[217,239,139],[254,224,139],[252,141,89],[215,48,39]]

            normalized_total = (total - min_count) / (max_count - min_count)

            color_index = int(normalized_total * (len(color_range) - 1))
            return color_range[color_index] + [255] 


        result_df['fill_color'] = result_df['total'].apply(fill_color)

        result_df['total_normal'] = (result_df['total'] - min_count+5) / (max_count - min_count)

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


    def get_classes_result(self, posibilities):
        # Перетворюємо масив CLASSES на словник для зручності доступу
        class_dict = pd.Series(self.CLASSES.name.values, index=self.CLASSES.id).to_dict()

        # Створюємо новий масив з 'class' та 'posibility'
        result = []
        for row in posibilities:
            max_index = np.argmax(row)  # Знаходимо індекс з максимальною ймовірністю
            result.append({
                'class': class_dict[max_index],
                'posibility': row[max_index]
            })
        filtered_result = [item for item in result if item['posibility'] >= 0.85]

        return filtered_result
    
    def get_or_create_location(self, latitude, longitude):

        latitude = round(latitude, 3)
        longitude = round(longitude, 3)
        # Перевіряємо, чи існує запис із заданими широтою і довготою
        response = self.db.table("location").select("id").eq("latitude", latitude).eq("longitude", longitude).execute()
        
        # Якщо запис існує, повертаємо його id
        if response.data:
            return response.data[0]["id"]
        
        # Якщо запису не існує, створюємо новий і повертаємо його id
        response = self.db.table("location").insert({"latitude": latitude, "longitude": longitude}).execute()
        return response.data[0]["id"]
    
    def create_audio_record(self):
        max_id_response = self.db.table('audio_record').select('id').order('id', desc=True).limit(1).execute()
        max_id = max_id_response.data[0]['id'] if max_id_response.data else 0

        # Вставка нового запису в таблицю audio_record
        new_id = max_id + 1
        new_record = {'id': new_id, 'file_name': f'file_{new_id}', 'length': 4}
        insert_response = self.db.table('audio_record').insert(new_record).execute()

        return insert_response.data[0]['id']
    
    def get_class_id_by_name(self, class_name):
    
        response = self.db.table('class').select('id').eq('name', class_name).execute()
        
        return response.data[0]['id']
       

    def insert_data(self, long, lat, results):
        location_id = self.get_or_create_location(lat, long)
        date = datetime.now().date().isoformat()
        time = datetime.now().time().isoformat()

        for result in results:
            class_name = result["class"]
            
            # Get class_id for the class name
            class_id = self.get_class_id_by_name(class_name)

            
            # Create new audio record and get its id
            audio_record_id = self.create_audio_record()
            
            # Insert data into sound table
            sound_data = {
                "audio_record_id": audio_record_id,
                "class_id": class_id,
                "location_id": location_id,
                "date": date,
                "time": time
            }
            self.db.table("sound").insert(sound_data).execute()
    
        