const BASE_URL = 'http://localhost:8000';

// Função para listar os autômatos
async function listAutomata() {
    const response = await fetch(`${BASE_URL}/`);
    if (!response.ok) {
        throw new Error('Erro ao listar autômatos');
    }
    return response.json();
}

// Função para criar um novo autômato
async function createAutomaton(automaton) {
    const response = await fetch(`${BASE_URL}/automaton/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(automaton),
    });
    if (!response.ok) {
        throw new Error('Erro ao criar autômato');
    }
    return response.json();
}

// Função para obter um autômato pelo ID
async function readAutomaton(automatonId) {
    const response = await fetch(`${BASE_URL}/automaton/${automatonId}`);
    if (!response.ok) {
        throw new Error('Erro ao ler autômato');
    }
    return response.json();
}
// Função para reconhecer uma string usando um autômato
async function recognizeString(automatonId, inputString) {
    const response = await fetch(`${BASE_URL}/automaton/${automatonId}/recognize?input_string=${encodeURIComponent(inputString)}`, {
        method: 'POST',
    });
    if (!response.ok) {
        throw new Error('Erro ao reconhecer string');
    }
    return response.json();
}

// Função para converter um AFN para AFD
async function convertAfnToAfd(automatonId) {
    console.log(automatonId);  // Confirmação de que o ID está sendo passado corretamente
    const response = await fetch(`${BASE_URL}/automaton/${automatonId}/convert-afn-to-afd`, {
        method: 'POST',  // Alterado para POST
    });
    if (!response.ok) {
        throw new Error('Erro ao converter AFN para AFD');
    }
    return response.json();
}


// Função para minimizar um AFD
async function minifyAutomaton(automatonId) {
    const response = await fetch(`${BASE_URL}/automaton/${automatonId}/minify`);
    if (!response.ok) {
        throw new Error('Erro ao minimizar autômato');
    }
    return response.json();
}

// Função para verificar o tipo do autômato (AFD ou AFN)
async function getAutomatonType(automatonId) {
    const response = await fetch(`${BASE_URL}/automaton/${automatonId}/type`);
    if (!response.ok) {
        throw new Error('Erro ao obter tipo do autômato');
    }
    return response.json();
}

// Função para verificar a equivalência entre dois autômatos
async function checkEquivalence(automatonId1, automatonId2) {
    const response = await fetch(`${BASE_URL}/automaton/${automatonId1}/equivalence/${automatonId2}`, {
        method: 'POST',
    });
    if (!response.ok) {
        throw new Error('Erro ao verificar equivalência entre autômatos');
    }
    return response.json();
}

// Exportar funções para uso em outros módulos
export {
    listAutomata,
    createAutomaton,
    readAutomaton,
    recognizeString,
    convertAfnToAfd,
    minifyAutomaton,
    getAutomatonType,
    checkEquivalence,
};
