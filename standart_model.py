import pickle
import librosa
import numpy as np
from io import BytesIO

class StandartModel:
    def __init__(self):
        with open('standart_model.pkl', 'rb') as file:
            self.model = pickle.load(file)

    def classify(self, audio_record):
        data_to_predict = self.get_data_from_audio(audio_record)
        predictions = self.model.predict_proba(data_to_predict)
        
        return predictions
    
    def get_data_from_audio(self, audio_record):
        # Convert audio_record to numpy array

        audio_record, sample_rate = librosa.core.load(BytesIO(audio_record), sr=44100)

        segment_duration = 4  # in seconds
        sample_rate = 44100
        segment_samples = segment_duration * sample_rate

        segments = [audio_record[i:i+segment_samples] for i in range(0, len(audio_record), segment_samples)]

        # Initialize a list to store the results
        results = []

        # Extract features for each segment
        for segment in segments:

            # Compute MFCC features
            mfccs_features = librosa.feature.mfcc(y=segment, sr=sample_rate, n_mfcc=256)
            mfccs_features_scaled = np.mean(mfccs_features.T, axis=0)

            # Compute zero-crossing rate
            zcr = librosa.feature.zero_crossing_rate(segment)
            zcr_mean = np.mean(zcr)

            # Combine features
            combined_features = np.hstack((mfccs_features_scaled, zcr_mean))
            
            # Append the combined features to the results list
            results.append(combined_features)

        # Convert the results list to a numpy array
        results = np.array(results)
        return results
