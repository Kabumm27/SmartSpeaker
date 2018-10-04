import logging
import json
import six
import os
import re

from rasa_nlu.training_data import load_data
from rasa_nlu.model import Trainer
from rasa_nlu import config


def train_nlu_en():
    # training_data = load_data('data/en/data_nlu.json')
    # trainer = Trainer(RasaNLUConfig('data/en/config_nlu.json'))
    # trainer.train(training_data)
    # model_directory = trainer.persist('models/nlu/', fixed_model_name=model_name)
    # return model_directory
    pass


def train_nlu_de():
    combine_json('../data/de/')
    training_data = load_data('data_de.json')
    trainer = Trainer(config.load('config_de.yml'))
    trainer.train(training_data)
    model_directory = trainer.persist('models/', fixed_model_name='current')


def combine_json(json_dir):
    intents = {}

    regex_features = []
    entity_synonyms = []
    common_examples = []

    maxNumberOfExamples = 30 # Set minimum value (should be at least 30)

    for filename in os.listdir(json_dir):
        with open(json_dir + filename, 'r') as json_file:
            try:
                data = json.load(json_file).get('rasa_nlu_data')
                nrOfExamples = len(data['common_examples'])

                for example in data['common_examples']:
                    examples = expand_examples(example)
                    intent = example['intent']
                    if intent in intents:
                        intents[intent].extend(examples)
                    else:
                        intents[intent] = examples

                regex_features.extend(data['regex_features'])
                entity_synonyms.extend(data['entity_synonyms'])

            except json.JSONDecodeError:
                print('\033[93mIgnoring file \'{}\' due to JSON parsing error!\033[0m'.format(filename))
                continue

    print()
    print(' INTENT          SAMPLES ')
    print('=========================')

    for key, examples in sorted(intents.items()):
        nrOfExamples = len(examples)
        fullCopies = (maxNumberOfExamples // nrOfExamples) - 1
        partialCopy = maxNumberOfExamples % nrOfExamples

        # Full copies
        copy = []
        for i in range(0, fullCopies):
            copy.extend(examples)

        # Partial copy
        for i in range(0, partialCopy):
            copy.append(examples[i])

        # examples += copy
        common_examples.extend(examples + copy)
        print(' {:20} {:2d}'.format(key, nrOfExamples))

    output = {
        'rasa_nlu_data': {
            'regex_features': regex_features,
            'entity_synonyms': entity_synonyms,
            'common_examples': common_examples
        }
    }

    with open('data_de.json', 'w') as output_file:
        output_file.write(json.dumps(output, indent=4, sort_keys=True, ensure_ascii=False))

    # return output


def expand_examples(example):
    # Add empty entities if missing
    if not 'entities' in example:
        example['entities'] = []

    # Expand text
    text = example['text'].lower()
    bracket_open = text.count('(')
    bracket_closed = text.count(')')

    if bracket_open != bracket_closed:
        raise Exception('Text expansion error!')

    if bracket_open > 0:
        possibilities = list(map(lambda s: s.strip(), filter(None, re.split('[()]', text))))
        lines = []

        iterator = []
        counter = []
        nr_of_perms = 1

        for i in range(0, len(possibilities)):
            possibilities[i] = possibilities[i].split('|')
            iterator.append(0)
            counter.append(len(possibilities[i]))
            nr_of_perms *= len(possibilities[i])

        for i in range(0, nr_of_perms):
            lines.append('')
            for j, part in enumerate(possibilities):
                if part[iterator[j]]:
                    lines[i] += ' ' + part[iterator[j]]

            # increment iterator
            carry = 1
            for j in range(0, len(iterator)):
                iterator[j] += carry
                carry = 0

                if iterator[j] >= counter[j]:
                    iterator[j] -= counter[j]
                    carry = 1

        examples = []
        for line in lines:
            examples.append({
                'intent': example['intent'],
                'entities': list(example['entities']),
                'text': line.strip()
            })

        return examples
    else:
        return [example]

    # print('{}'.format(text))

if __name__ == '__main__':
    logging.basicConfig(level='INFO')
    # train_nlu_en()
    train_nlu_de()
