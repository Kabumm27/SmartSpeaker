import * as React from 'react';

import { Utterance } from "./Utterance"


export interface IIntentProps {
    removeMarking: (intent: string, dataIndex: number, textIndex: number) => void,
    updateJsonState: () => void,
    entities: string[],
    intent: string,
    utterances: Array<{
        data: Array<{
            text: string
            entity?: string,
            slot_name?: string,
        }>
    }>
}
// interface IntentState {}

export class Intent extends React.Component<IIntentProps, {}> {
    public render() {
        const intent = this.props.intent;

        const utterances = [];
        let i = 0;
        for (const utter of this.props.utterances) {
            const key = intent + '_' + i;
            utterances.push(<Utterance key={key} entities={this.props.entities} intent={intent} index={i} updateJsonState={this.props.updateJsonState} removeMarking={this.props.removeMarking} data={utter.data} />)
            i++;
        }

        return (
            <div className="Intent">
                <h3>{intent}</h3>
                {utterances}

                <div>
                    <input type='text' placeholder='Add new example' id={'add-example-' + this.props.intent} />
                    <button onClick={e => this.addExample()}>Add</button>
                </div>
            </div>
        );
    }

    private addExample() {
        const input = document.getElementById('add-example-' + this.props.intent) as HTMLInputElement;
        const exampleText = input.value.trim()

        if (exampleText.length > 3) {
            input.value = '';

            this.props.utterances.push({
                data: [{
                    text: exampleText
                }]
            });

            console.log(this.props.utterances)
            
            this.props.updateJsonState();
        }
    }
}
