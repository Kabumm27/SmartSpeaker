import * as React from 'react';
import './IntentDataView.css';

import { Entity } from './Entity'
import { Intent } from './Intent'

// export interface IntentDataViewProps {}
interface IIntentDataViewState {
    activeTab: string
    data: any,
}

export class IntentDataView extends React.Component<{}, IIntentDataViewState> {
    public constructor(props: {}) {
        super(props);

        this.state = {
            activeTab: 'intents',
            data: ''
        }
    }

    public componentDidMount() {
        fetch('./lights_dataset_en.json')
            .then(response => {
                return response.json()
            })
            .then(json => {
                json.entities.room.data[0].synonyms.push('house', 'carport');
                this.setState({
                    data: json
                })
            });
    }

    public render() {
        const entities = [];
        const intents = [];

        if (this.state.data) {
            for (const key of Object.keys(this.state.data.intents)) {
                const value = this.state.data.intents[key];
                intents.push(<Intent key={key} entities={Object.keys(this.state.data.entities)} updateJsonState={() => this.updateState()} removeMarking={(i, d, t) => this.removeMarking(i, d, t)} intent={key} utterances={value.utterances} />);
            }

            // Entity[]
            //    Color
            //    Entity example[]
            //        Entity example synonym[]

            for (const k of Object.keys(this.state.data.entities)) {
                entities.push(<Entity key={k} updateJsonState={() => this.updateState()} name={k} examples={this.state.data.entities[k]} />);
            }
        }

        return (
            <div className='IntentDataView'>
                <div>
                    <button onClick={e => this.activeTab('entities')}>Entities</button>
                    <button onClick={e => this.activeTab('intents')}>Intents</button>
                    <button onClick={e => this.markEntity(e, 'room')}>Mark Entity</button>
                    <button onClick={e => this.saveFile()}>Export JSON</button>
                </div>

                {this.state.activeTab === 'entities' ?
                <div>
                    <h1>Entities</h1>
                    {entities}

                    <hr />
                    <div>
                        <input type='text' placeholder='Add new entity' id='add-entity' />
                        <button onClick={e => this.addNewEntity()}>Add</button>
                    </div>
                </div>
                : null}

                {this.state.activeTab === 'intents' ?
                <div>
                    <h1>Intents</h1>
                    {intents}

                    <hr />
                    <div>
                        <input type='text' placeholder='Add new intent' id='add-intent' />
                        <button onClick={e => this.addNewIntent()}>Add</button>
                    </div>
                </div>
                : null}
            </div>
        );
    }

    private activeTab(tab: string) {
        const tabs = ['intents', 'entities'];
        if (tabs.indexOf(tab) < 0) {
            return;
        }

        this.setState({
            activeTab: tab
        });
    }

    private addNewEntity() {
        const input = document.getElementById('add-entity') as HTMLInputElement;
        const name = input.value.trim()

        if (name.length > 3) {
            input.value = '';

            this.state.data.entities[name] = {
                automatically_extensible: true,
                data: [],
                parser_threshold: 1,
                use_synonyms: true
            }

            this.setState({
                data: this.state.data
            })
        }
    }

    private addNewIntent() {
        const input = document.getElementById('add-intent') as HTMLInputElement;
        const name = input.value.trim()

        if (name.length > 3) {
            input.value = '';

            this.state.data.intents[name] = {
                utterances: []
            }

            this.setState({
                data: this.state.data
            });
        }
    }

    private saveFile() {
        const blob = new Blob(
            [JSON.stringify(this.state.data)],
            { type: 'application/json;charset=utf-8' }
        )

        const a = document.createElement('a');
        a.download = 'data.json';
        a.rel = 'noopener';
        a.href = window.URL.createObjectURL(blob);

        a.dispatchEvent(new MouseEvent('click'));
    }

    private updateState() {        
        this.setState({
            data: this.state.data
        });
    }

    private markEntity(e: React.MouseEvent<HTMLButtonElement>, entityType: string) {
        const selection = window.getSelection();
        const anchor = selection.anchorNode;
        const focus = selection.focusNode;

        // Cancel if the selections spans more than a single element
        if (anchor !== focus) {
            return;
        }

        const parent = anchor.parentElement;
        if (parent == null || !parent.classList.contains('Utterance')) {
            return;
        }
        
        // console.log(parent.innerHTML);
        const text = anchor.textContent; // parent.innerText;
        if (text == null || text.trim().length === 0) {
            return;
        }

        let start = selection.anchorOffset;
        let end = selection.focusOffset;

        // Ignore whitespace at the beginning and end
        while (/\s/.test(text[start])) {
            start += 1;
        }
        while (/\s/.test(text[end -1])) {
            end -= 1;
        }

        // Ignore only whitespace selections
        if (start >= end) {
            return;
        }


        const intent = parent.getAttribute('data-intent') as string;
        const utteranceIndex = parent.getAttribute('data-index') as string;
        const utterances = this.state.data.intents[intent].utterances;
        const utterance = utterances[utteranceIndex].data;
        
        let index = 0;
        let el = anchor;
        while (el.previousSibling) {
            el = el.previousSibling;
            index += 1
        }

        const newData = [];
        if (start > 0) {
            newData.push({
                text: text.slice(0, start)
            });
        }
        newData.push({
            entity: entityType,
            slot_name: entityType,
            text: text.slice(start, end)
        });

        if (end < text.length) {
            newData.push({
                text: text.slice(end)
            });
        }

        utterance.splice(index, 1, ...newData);

        
        this.setState({
            data: this.state.data
        });
    }

    private removeMarking(intent: string, dataIndex: number, textIndex: number) {
        const utterances = this.state.data.intents[intent].utterances;
        const utterance = utterances[dataIndex].data;

        const prev = textIndex > 0 ? utterance[textIndex -1] : null;
        const next = textIndex < utterance.length ? utterance[textIndex +1] : null;
        const curr = utterance[textIndex];

        const newData = {
            text: curr.text
        }

        utterance[textIndex] = newData;
        
        if (prev && !prev.entity) {
            newData.text = prev.text + newData.text;
            utterance.splice(textIndex -1, 1);
            textIndex -= 1;
        }

        if (next && !next.entity) {
            newData.text = newData.text + next.text;
            utterance.splice(textIndex +1, 1);
            textIndex -= 1;
        }

        this.setState({
            data: this.state.data
        })

    }
}
