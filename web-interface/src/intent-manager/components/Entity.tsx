import * as React from 'react';


export interface IEntityProps {
    updateJsonState: () => void,
    name: string,
    examples: {
        automatically_extensible: boolean,
        use_synonyms: boolean,
        data: Array<{
            value: string,
            synonyms: string[]
        }>
    }
}
// interface IntentState {}

export class Entity extends React.Component<IEntityProps, {}> {
    public render() {
        // console.log(this.props.examples);

        const examples = [];

        for (const example of this.props.examples.data) {
            examples.push(
                <div key={example.value}>
                    {example.value} - {example.synonyms.join(', ')}
                    <input type='text' placeholder='Add new synonym' id={'add-synonym-' + this.props.name + '-' + example.value} />
                    <button onClick={e => this.addSynonym(example.value)}>Add</button>
                </div>
            );
        }

        return (
            <div className='entity'>
                <h3>{this.props.name}</h3>

                <label>
                    <input type={'checkbox'} defaultChecked={this.props.examples.automatically_extensible}/>
                    Automatically Extensible
                </label>
                <br />
                <label>
                    <input type={'checkbox'} defaultChecked={this.props.examples.use_synonyms}/>
                    Use Synonyms
                </label>
                <br />

                {examples}

                <div>
                    <input type='text' placeholder='Add new example' id={'add-example-' + this.props.name} />
                    <button onClick={e => this.addExample()}>Add</button>
                </div>
            </div>
        );
    }

    private addSynonym(example: string) {
        const input = document.getElementById('add-synonym-' + this.props.name + '-' + example) as HTMLInputElement;
        const synonym = input.value.trim()

        if (synonym.length > 2) {
            input.value = '';

            for (const d of this.props.examples.data) {
                if (d.value === example) {
                    d.synonyms.push(synonym);
                    break;
                }
            }

            this.props.updateJsonState();
        }
    }

    private addExample() {
        const input = document.getElementById('add-example-' + this.props.name) as HTMLInputElement;
        const exampleName = input.value.trim()

        if (exampleName.length > 2) {
            input.value = '';

            this.props.examples.data.push({
                synonyms: [],
                value: exampleName
            });

            this.props.updateJsonState();
        }
    }
}
