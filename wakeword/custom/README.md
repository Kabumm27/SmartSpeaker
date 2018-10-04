# Custom Wakeword engine
A CNN based wakeword engine. MFCCs are extracted from the audio files and fed into the network.


## Install
`pip install keras tensorflow `



## Data
Expects 1 second long audio files in 3 categories (Keyword, Voice, Noise)



## Training
```
python train.py
```


## Run
You can run per python interface 
```
from predict import load_model, predict
model = load_model('path_to_model')

# audio_samples as array of 16 bit int (like np.array([...]).astype(np.int16))
sample_rate = 16000

predict(audio_samples, sample_rate, model)
```

or by calling predict.py with path to audio file
```
python predict.py -m path_to_model -a path_to_audio_file
```



