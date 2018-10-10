# API-Gateway

This gateway manages the connection to the individual services. A smart speaker instance only 
needs to know the address of their gateway and not all the addresses of each single service. It also 
enables the option to do remote changes to the services without ever touching the smart speaker instance. 

Another task of thegateway is to normalizes the output of the external services, so that they can be 
used interchangeably.


## List of APIs
* Intent Detection
    * Implemented: Rasa_nlu
    * Todo: Snips_nlu
* Speech to Text
    * Implmeneted: Bing Speech Services, Kaldi (Experimental)
    * Todo: Google STT, Mozilla Deepspeech
* Text to Speech
    * Implemented: MaryTTS
    * Todo: Google TTS, Tacotron


## Build
**Check code for API missing keys. (Errors not yet implemented)**

Install dependencies and build the project with the TypeScript compiler.

```
npm install
node_modules/.bin/tsc .
```


## Run
Run `index.js` in the build directory with node.js

```
node build/index.js
```