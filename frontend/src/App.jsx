import React from "react";
import AutomatonCanvas from "./components/AutomatonCanvas";
import "./styles/App.css"
import "./styles/AutomatonCanvas.css"
import "./styles/AutomatonState.css"


function App() {
  return (
    <div className="App">
      <h1>Automaton Editor</h1>
      <AutomatonCanvas />
    </div>
  );
}

export default App;
