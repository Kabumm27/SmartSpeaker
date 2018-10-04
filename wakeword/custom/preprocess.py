import os
from os.path import isdir, join, splitext
import numpy as np
from utils import wav2mfcc


train_audio_path = 'data/validated'
# testing_audio_path = 'data/testing'
# validation_audio_path = 'data/validation'

dirs = [f for f in os.listdir(train_audio_path) if isdir(join(train_audio_path, f))]
labels = "keyword noise voice".split()

def wav2mfcc_wrapper(path, filename):
    return wav2mfcc(join(path, filename), noise_probability=0.2)

train_data = {}
for label in dirs:
    if label in labels:
        train_path = train_audio_path + '/' + label
        # testing_path = testing_audio_path + '/' + label
        # validation_path = validation_audio_path + '/' + label

        train_files = [f for f in os.listdir(train_path) if splitext(f)[1] == '.wav']
        # testing_files = [f for f in os.listdir(testing_path) if splitext(f)[1] == '.wav']
        # validation_files = [f for f in os.listdir(validation_path) if splitext(f)[1] == '.wav']

        train_features = [wav2mfcc_wrapper(train_path, f) for f in train_files]
        # testing_features = [wav2mfcc_wrapper(testing_path, f) for f in testing_files]
        # validation_features = [wav2mfcc_wrapper(validation_path, f) for f in validation_files]

        train_data[label] = {
            'training': train_features,
            # 'testing': testing_features,
            # 'validation': validation_features,
        }
        print('Label <{}> done'.format(label))


for key, values in train_data.items():
    np.save('data/featurized/training/{}_16k.npy'.format(key), values['training'])
    # np.save('data/mfcc/testing/{}_noise_16k.npy'.format(key), values['testing'])
    # np.save('data/mfcc/validation/{}_noise_16k.npy'.format(key), values['validation'])


