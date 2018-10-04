import keras
import numpy as np
from utils import audio2mfcc
from scipy.io import wavfile
import os
from shutil import move
from argparse import ArgumentParser


def load_model(model_path):
    return keras.models.load_model(model_path)

def predict(samples, sample_rate, model):
    mfcc = audio2mfcc(samples, sample_rate)

    features = np.array([mfcc])
    features = mfcc.reshape(features.shape[0], features.shape[1], features.shape[2], 1)


    prediction = model.predict_classes(features)[0]
    # Classes:
    #  0 - Keyword
    #  1 - Noise
    #  2 - Voice

    return prediction


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-m", "--model", dest="model", required=True,
                        help="trained model for prediction")
    parser.add_argument("-a", "--audio",
                        required=True, dest="audio_file",
                        help="audio (wav) file to predict")

    args = parser.parse_args()

    # Load model and file
    model = load_model(args.model)
    sr, samples = wavfile.read(args.audio_file)

    # Predict file
    prediction = predict(samples, sr, model)
    
    if prediction == 0:
        print('Keyword detected')
    elif prediction == 1:
        print('Only noise detected')
    else:
        print('Voice, but no keyword detected')
