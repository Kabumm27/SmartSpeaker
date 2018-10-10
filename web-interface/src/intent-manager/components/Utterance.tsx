import * as React from 'react';
import './Utterance.css';


export interface IUtteranceProps {
    removeMarking: (intent: string, dataIndex: number, textIndex: number) => void,
    updateJsonState: () => void,
    entities: string[],
    intent: string,
    index: number,
    data: Array<{
        text: string
        entity?: string,
        slotName?: string,
    }>
}
// interface IntentState {}

export class Utterance extends React.Component<IUtteranceProps, {}> {
    public render() {
        const intent = this.props.intent;
        const index = this.props.index;

        const colors = [
            'yellow',
            'orange'
        ];

        const texts = [];
        for (let i = 0; i < this.props.data.length; i++) {
            const d = this.props.data[i];
            if (d.entity) {
                const entityIndex = this.props.entities.indexOf(d.entity);
                const key = intent + '_' + index + '_' + i;
                texts.push(<span key={key} onClick={e => this.props.removeMarking(intent, index, i)}
                                style={{backgroundColor: colors[entityIndex % colors.length]}}
                                className='Utterance-entity'>{d.text}</span>);
            }
            else {
                texts.push(d.text);
            }
        }

        // const text = this.props.data.reduce((prev, curr) => prev + curr.text, '')

        return (
            <div className="Utterance" contentEditable={true}
                data-intent={intent} data-index={index}
                suppressContentEditableWarning={true}
                onInput={e => this.onChange(e)} onBlur={this.props.updateJsonState}>{texts}</div>
        );
    }

    private onChange(e: React.FormEvent<HTMLDivElement>) {
        const selection = window.getSelection();
        const anchor = selection.anchorNode;
        
        // Cancel if not caret
        if (selection.type !== 'Caret') {
            return;
        }
        
        const parent = anchor.parentElement;
        if (parent == null) {
            return;
        }
        
        let index = 0;
        let el = parent.classList.contains('Utterance') ? anchor : parent;
        while (el.previousSibling) {
            el = el.previousSibling;
            index += 1
        }

        const utterance = this.props.data;
        utterance[index].text = anchor.textContent as string;
    }
}
