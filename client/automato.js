const canvas = document.getElementById('automatoCanvas');
const ctx = canvas.getContext('2d',  {willReadFrequently: true });
let states = [];
let transitions = [];
let startState = null;
let finalStates = [];
let dragging = false;
let selectedState = null;
let isMoving = false;
let isDeleting = false; 

canvas.addEventListener('dblclick', createState);
canvas.addEventListener('mousedown', startDragging);
canvas.addEventListener('mousemove', drag);
canvas.addEventListener('mouseup', endDragging);
canvas.addEventListener('contextmenu', deleteStateOrTransition);
document.addEventListener('keydown', handleKeyDown);
document.addEventListener('keyup', handleKeyUp);
canvas.addEventListener('mousedown', deleteStateOrTransition); 

function createState(event) {
    const x = event.offsetX;
    const y = event.offsetY;
    const id = `q${states.length}`;
    const newState = { id, x, y, radius: 30 };
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
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(state.x, state.y, state.radius, 0, Math.PI * 2);
    ctx.stroke();
    if (state === startState) {
        ctx.beginPath();
        ctx.moveTo(state.x - 50, state.y);
        ctx.lineTo(state.x - 35, state.y);
        ctx.stroke();
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(state.x - 45, state.y - 5);
        ctx.lineTo(state.x - 35, state.y);
        ctx.lineTo(state.x - 45, state.y + 5);
        ctx.fill();
    }
    if (finalStates.includes(state.id)) {
        ctx.beginPath();
        ctx.arc(state.x, state.y, state.radius - 6, 0, Math.PI * 2);
        ctx.stroke();
    }
    ctx.font = "20px Arial"; 
    ctx.fillText(state.id, state.x - 15, state.y + 7);
}


function drawArrow(from, to, text) {
    const headlen = 10;
    const dx = to.x - from.x;
    const dy = to.y - from.y;
    const angle = Math.atan2(dy, dx);

    if (from === to) {
        const loopRadius = 30;
        const centerX = from.x;
        const centerY = from.y - loopRadius;

        // Filtrar todas as transições cíclicas para este estado
        const cyclicTransitions = transitions.filter(t => t.current_state === from.id && t.next_state === to.id);
        
        // Concatena as transições cíclicas, separados por vírgula
        const combinedText = cyclicTransitions.map(t => t.symbol).join(", ");

        // Desenhar um arco semicircular para a auto-transição
        ctx.beginPath();
        ctx.arc(centerX, centerY, loopRadius, 0.75 * Math.PI, 2.25 * Math.PI);
        ctx.stroke();

        // Desenhar a ponta da seta no final do arco
        const arrowX = centerX + loopRadius * Math.cos(0.75 * Math.PI);
        const arrowY = centerY + loopRadius * Math.sin(0.75 * Math.PI);

        ctx.beginPath();
        ctx.moveTo(arrowX, arrowY);
        ctx.lineTo(arrowX - headlen, arrowY - headlen);
        ctx.lineTo(arrowX + headlen, arrowY - headlen);
        ctx.closePath();
        ctx.fill();

        // Desenhar o texto da transição próximo ao meio do arco
        ctx.font = "16px Arial";
        ctx.fillText(combinedText, centerX + loopRadius + 10, centerY);
    } else {
        const dist = Math.sqrt(dx * dx + dy * dy);
        const offset = 30;
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

        ctx.font = "16px Arial";
        ctx.fillText(text, (x1 + x2) / 2, (y1 + y2) / 2);
    }
}

function handleKeyDown(event) {
    if (event.code === 'Space') {
        isDeleting = true;
        canvas.style.cursor = 'crosshair';
    }
}

function handleKeyUp(event) {
    if (event.code === 'Space') {
        isDeleting = false;
        canvas.style.cursor = 'default'; 
    }
}

function deleteStateOrTransition(event) {
    if (isDeleting && event.button === 0) {
        event.preventDefault();

        const x = event.offsetX;
        const y = event.offsetY;

        // Verificar se um estado foi clicado
        const stateToDelete = getStateAtPosition(x, y);
        if (stateToDelete) {
            // Remover o estado
            states = states.filter(state => state !== stateToDelete);
            
            // Remover todas as transições associadas ao estado
            transitions = transitions.filter(transition => transition.current_state !== stateToDelete.id && transition.next_state !== stateToDelete.id);
            
            draw();
            return;
        }

        // Verificar se uma transição foi clicada
        const transitionToDelete = getTransitionAtPosition(x, y);
        if (transitionToDelete) {
            // Remover a transição
            transitions = transitions.filter(transition => transition !== transitionToDelete);
            draw();
        }
    }
}


function getTransitionAtPosition(x, y) {
    // Encontrar a transição mais próxima ao clique
    for (const transition of transitions) {
        const fromState = states.find(s => s.id === transition.current_state);
        const toState = states.find(s => s.id === transition.next_state);

        if (fromState && toState) {
            // Calcular o ponto médio da linha da transição
            const midX = (fromState.x + toState.x) / 2;
            const midY = (fromState.y + toState.y) / 2;

            // Verificar se o clique está próximo ao ponto médio
            const distance = Math.sqrt((x - midX) ** 2 + (y - midY) ** 2);
            if (distance < 10) { // Tolerância para considerar a transição clicada
                return transition;
            }
        }
    }
    return null;
}


export function isCanvasEmpty() {
    const pixelData = ctx.getImageData(0, 0, canvas.width, canvas.height).data;

    // Verificar se todos os pixels são transparentes
    for (let i = 0; i < pixelData.length; i += 4) {
        if (pixelData[i + 3] !== 0) { // Se o valor de alpha (transparência) não for 0
            return false;
        }
    }

    return true;
}



export function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    states = [];
    transitions = [];
    startState = null;
    finalStates = [];
    selectedState = null;
    isMoving = false;
    dragging = false;
}


//funcões pra comunicação com o backend

export function exportToJson() {
    const automaton = {
        estados: states.map(s => s.id),
        alfabeto: Array.from(new Set(transitions.map(t => t.symbol))),
        transicoes: transitions.map(t => ({
            estado_atual: t.current_state,
            simbolo: t.symbol,
            proximo_estado: t.next_state
        })),
        estado_inicial: startState ? startState.id : null,
        estados_de_aceitacao: finalStates
    };

    return JSON.stringify(automaton, null, 2);
}

export function importFromJson(json) {
    states = [];
    transitions = [];
    startState = null;
    finalStates = [];

    const automaton = typeof json === "string" ? JSON.parse(json) : json;

    automaton.estados.forEach((id, index) => {
        const state = {
            id: id,
            x: 150 + index * 150, // Ajuste das posições para espaçamento horizontal
            y: 150 + (index % 2) * 200, // Alternar y para espaçamento vertical
            radius: 30
        };
        states.push(state);
    });

    // Restaurar transições
    automaton.transicoes.forEach((transition, index) => {
        const fromState = states.find(s => s.id === transition.estado_atual);
        const toState = states.find(s => s.id === transition.proximo_estado);

        if (fromState && toState) {
            // Calcular ponto de controle para espaçar as linhas de transição
            const controlPoint = {
                x: (fromState.x + toState.x) / 2 + (index % 2 === 0 ? 50 : -50),
                y: (fromState.y + toState.y) / 2 + (index % 2 === 0 ? -50 : 50)
            };

            const newTransition = {
                current_state: transition.estado_atual,
                symbol: transition.simbolo,
                next_state: transition.proximo_estado,
                controlPoint: controlPoint
            };
            transitions.push(newTransition);
        }
    });

    // Restaurar estado inicial
    if (automaton.estado_inicial) {
        startState = states.find(s => s.id === automaton.estado_inicial);
    }

    // Restaurar estados finais
    automaton.estados_de_aceitacao.forEach(finalStateId => {
        const finalState = states.find(s => s.id === finalStateId);
        if (finalState) {
            finalStates.push(finalState.id);
        }
    });

    draw();
}
