# Zoe Agent
The Zoe agent combines the previous technologies into a working product, 
it listens to a trained wakeword, records the audio after the wakeword and 
sends it to the gateway to traslate the audio into text and extract the 
intent. Depending on the result, an skill is activated.

The latest model in the wakeword directory is trained (with my voice) to 
listen for the wakeword `Zoe`. 


## Run
```
python zoe_agent.py
```