import React from "react";
import "../styles/AutomatonCanvas.css"

const AutomatonState = ({ state }) => {
  return (
    <div
      className="automaton-state"
      style={{ left: state.x, top: state.y }}
    >
      {state.name}
    </div>
  );
};

export default AutomatonState;
