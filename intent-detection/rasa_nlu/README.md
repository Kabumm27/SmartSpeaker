# Rasa NLU
Intent detection


## Install
`pip install rasa_nlu sklearn spacy bottle`
`python -m spacy download de`


## Train
Train with
```
python train.py
```

## Run
Start the server with
```
python server.py
```

Send request to server via 
```
http://localhost:5000/parse?q=Music on
```
