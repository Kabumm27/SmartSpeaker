from __future__ import unicode_literals, print_function

import io
import json

from snips_nlu import SnipsNLUEngine, load_resources
from snips_nlu.default_configs import CONFIG_EN, CONFIG_DE

with io.open("lights_dataset_de.json") as f:
    sample_dataset = json.load(f)

# load_resources("en")
# nlu_engine = SnipsNLUEngine(config=CONFIG_EN)
load_resources("de")
nlu_engine = SnipsNLUEngine(config=CONFIG_DE)
nlu_engine.fit(sample_dataset)
nlu_engine.persist("models/current")

