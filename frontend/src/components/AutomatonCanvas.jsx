import React, { useState } from "react";
import AutomatonState from "./AutomatonState.jsx";
import "../styles/AutomatonCanvas.css";
import { createState } from "./utils/createState.js";
import { removeState } from "./utils/removeState.js";

const AutomatonCanvas = () => {
  const [states, setStates] = useState([]);

  const handleDoubleClick = (e) => {
    const canvasRect = e.target.getBoundingClientRect();
    const clickX = e.clientX - canvasRect.left;
    const clickY = e.clientY - canvasRect.top;

    if (e.ctrlKey) {
      // Se Ctrl está pressionada, remove o estado
      const updatedStates = removeState(clickX, clickY, states);
      setStates(updatedStates);
    } else {
      // Caso contrário, cria um novo estado
      const newState = createState(clickX, clickY, states);
      setStates([...states, newState]);
    }
  };

  return (
    <div className="automaton-canvas" onDoubleClick={handleDoubleClick}>
      {states.map((state) => (
        <AutomatonState key={state.id} state={state} />
      ))}
    </div>
  );
};

export default AutomatonCanvas;
