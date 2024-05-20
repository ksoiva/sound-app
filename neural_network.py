import pickle
import librosa
import numpy as np
from io import BytesIO

import tensorflow as tf
from tensorflow.keras.models import load_model

import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

class NeuralNetwork:
    def __init__(self):

        self.model = load_model('neural_network_model.keras', compile=False)
        self.model.load_weights('neural_network_model_weights.h5')

    def classify(self, audio_record):
        data_to_predict = self.get_data_from_audio(audio_record)
        predictions = self.model.predict(data_to_predict)
        
        return predictions
    
    def get_data_from_audio(self, audio_record):
        # Convert audio_record to numpy array

        audio_record, sample_rate = librosa.core.load(BytesIO(audio_record), sr=44100)
        
        # Mean length of the segments
        mean_length = 81479

        # Number of segments
        num_segments = int(np.ceil(len(audio_record) / mean_length))

        # Create a list to hold the segments
        segments = []

        # Loop to divide the audio into segments
        for i in range(num_segments):
            start = i * mean_length
            end = start + mean_length
            segment = audio_record[start:end]
            
            # If the segment is shorter than mean_length, pad it with zeros
            if len(segment) < mean_length:
                # Pad with zeros
                pad_start = (mean_length - len(segment)) // 2
                pad_end = mean_length - len(segment) - pad_start
                segment = np.pad(segment, (pad_start, pad_end), mode='constant')
            
            segments.append(segment)

        # Initialize a list to store the results
        results = []

        # Extract features for each segment
        for segment in segments:

            # Convert audio to spectrogram
            spectrogram = librosa.feature.melspectrogram(y=segment, sr=sample_rate)
            
            # Convert to decibels
            spectrogram_db = librosa.power_to_db(spectrogram, ref=np.max)
            
            # Append the combined features to the results list
            results.append(spectrogram_db)

        # Convert the results list to a numpy array
        results = np.array(results)
        return results
