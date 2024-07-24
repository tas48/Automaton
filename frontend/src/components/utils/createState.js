export const createState = (x, y, states) => {
    return {
      id: states.length + 1,
      name: `q${states.length}`,
      x: x,
      y: y,
    };
  };
  