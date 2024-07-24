export const removeState = (x, y, states) => {
    const stateToDelete = states.find(
      (state) =>
        Math.sqrt(Math.pow(state.x - x, 2) + Math.pow(state.y - y, 2)) < 25
    );
    if (stateToDelete) {
      return states.filter((state) => state.id !== stateToDelete.id);
    }
    return states;
  };
  