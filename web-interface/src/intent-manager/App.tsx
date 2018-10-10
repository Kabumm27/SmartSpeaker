import * as React from 'react';
import './App.css';

import { IntentDataView } from "./components/IntentDataView"

class App extends React.Component {
    public render() {
        return (
            <div className="App">
              <IntentDataView />
            </div>
        );
    }
}

export default App;
