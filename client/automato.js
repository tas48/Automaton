const canvas = document.getElementById('automatoCanvas');
const ctx = canvas.getContext('2d');
let states = [];
let transitions = [];
let startState = null;
let finalStates = [];
let dragging = false;
let selectedState = null;
let isMoving = false;

canvas.addEventListener('dblclick', createState);
canvas.addEventListener('mousedown', startDragging);
canvas.addEventListener('mousemove', drag);
canvas.addEventListener('mouseup', endDragging);

function createState(event) {
    const x = event.offsetX;
    const y = event.offsetY;
    const id = `q${states.length}`;
    const newState = { id, x, y, radius: 20 };
    states.push(newState);
    draw();
}

function startDragging(event) {
    const state = getStateAtPosition(event.offsetX, event.offsetY);

    if (event.ctrlKey && event.button === 2) {
        setFinalState(event);
    } else if (event.ctrlKey && event.button === 0) {
        setStartState(event);
    } else if (event.button === 0 && state) {
        dragging = true;
        selectedState = state;
        isMoving = true;
    } else if (event.button === 2 && state) {
        dragging = true;
        selectedState = state;
        isMoving = false;
    }
}

function drag(event) {
    if (dragging && selectedState) {
        if (isMoving) {
            selectedState.x = event.offsetX;
            selectedState.y = event.offsetY;
            draw();
        } else {
            draw();
            ctx.beginPath();
            ctx.moveTo(selectedState.x, selectedState.y);
            ctx.lineTo(event.offsetX, event.offsetY);
            ctx.stroke();
        }
    }
}

function endDragging(event) {
    if (dragging && selectedState && !isMoving) {
        const targetState = getStateAtPosition(event.offsetX, event.offsetY);
        if (targetState) {
            const symbol = prompt('Digite o símbolo da transição:');
            if (symbol) {
                const newTransition = {
                    current_state: selectedState.id,
                    symbol: symbol,
                    next_state: targetState.id
                };
                transitions.push(newTransition);
            }
        }
    }
    dragging = false;
    selectedState = null;
    draw();
}

function setStartState(event) {
    startState = getStateAtPosition(event.offsetX, event.offsetY);
    draw();
}

function setFinalState(event) {
    const state = getStateAtPosition(event.offsetX, event.offsetY);
    if (state) {
        finalStates.push(state.id);
    }
    draw();
}

function getStateAtPosition(x, y) {
    return states.find(state => Math.sqrt((x - state.x) ** 2 + (y - state.y) ** 2) < state.radius);
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    transitions.forEach(transition => {
        const fromState = states.find(s => s.id === transition.current_state);
        const toState = states.find(s => s.id === transition.next_state);
        drawArrow(fromState, toState, transition.symbol);
    });
    states.forEach(state => {
        drawState(state);
    });
}

function drawState(state) {
    ctx.beginPath();
    ctx.arc(state.x, state.y, state.radius, 0, Math.PI * 2);
    ctx.stroke();
    if (state === startState) {
        ctx.beginPath();
        ctx.moveTo(state.x - 30, state.y);
        ctx.lineTo(state.x - 10, state.y);
        ctx.stroke();
    }
    if (finalStates.includes(state.id)) {
        ctx.beginPath();
        ctx.arc(state.x, state.y, state.radius - 5, 0, Math.PI * 2);
        ctx.stroke();
    }
    ctx.fillText(state.id, state.x - 5, state.y + 5);
}

function drawArrow(from, to, text) {
    const headlen = 10;
    const dx = to.x - from.x;
    const dy = to.y - from.y;
    const angle = Math.atan2(dy, dx);
    
    if (from === to) {
        // Self-loop
        const loopRadius = 30;
        ctx.beginPath();
        ctx.arc(from.x, from.y - loopRadius, loopRadius, 0, Math.PI * 2);
        ctx.stroke();
        ctx.fillText(text, from.x + loopRadius + 5, from.y - loopRadius);
        ctx.beginPath();
        ctx.moveTo(from.x, from.y - loopRadius * 2);
        ctx.lineTo(from.x - headlen, from.y - loopRadius * 2 + headlen);
        ctx.lineTo(from.x + headlen, from.y - loopRadius * 2 + headlen);
        ctx.lineTo(from.x, from.y - loopRadius * 2);
        ctx.fill();
    } else {
        const dist = Math.sqrt(dx * dx + dy * dy);
        const offset = 20;
        const x1 = from.x + (offset * dy) / dist;
        const y1 = from.y - (offset * dx) / dist;
        const x2 = to.x + (offset * dy) / dist;
        const y2 = to.y - (offset * dx) / dist;

        ctx.beginPath();
        ctx.moveTo(from.x, from.y);
        ctx.quadraticCurveTo((x1 + x2) / 2, (y1 + y2) / 2, to.x, to.y);
        ctx.stroke();

        const arrowX = to.x - headlen * Math.cos(angle - Math.PI / 6);
        const arrowY = to.y - headlen * Math.sin(angle - Math.PI / 6);

        ctx.beginPath();
        ctx.moveTo(to.x, to.y);
        ctx.lineTo(arrowX, arrowY);
        ctx.lineTo(to.x - headlen * Math.cos(angle + Math.PI / 6), to.y - headlen * Math.sin(angle + Math.PI / 6));
        ctx.lineTo(to.x, to.y);
        ctx.fill();
        ctx.fillText(text, (x1 + x2) / 2, (y1 + y2) / 2);
    }
}

function exportToJson() {
    const automaton = {
        states: states.map(s => s.id),
        alphabet: Array.from(new Set(transitions.map(t => t.symbol))),
        transitions: transitions,
        start_state: startState ? startState.id : null,
        accept_states: finalStates
    };
    document.getElementById('output').textContent = JSON.stringify(automaton, null, 2);
}

