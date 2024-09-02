const BASE_URL = 'http://localhost:8000';

async function listAutomata() {
    const response = await fetch(`${BASE_URL}/`);
    if (!response.ok) {
        throw new Error('Erro ao listar autômatos');
    }
    return response.json();
}

async function createAutomaton(automaton) {
    const response = await fetch(`${BASE_URL}/automato/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(automaton),
    });
    if (!response.ok) {
        throw new Error('Erro ao criar autômato');
    }
    return response.json();
}


async function readAutomaton(automatonId) {
    const response = await fetch(`${BASE_URL}/automato/${automatonId}`);
    if (!response.ok) {
        throw new Error('Erro ao ler autômato');
    }
    return response.json();
}

async function recognizeString(automatonId, inputString) {
    const response = await fetch(`${BASE_URL}/automato/${automatonId}/reconhecer?cadeia=${encodeURIComponent(inputString)}`, {
        method: 'POST',
    });
    if (!response.ok) {
        throw new Error('Erro ao reconhecer string');
    }
    return response.json();
}


async function convertAfnToAfd(automatonId) {
    const response = await fetch(`${BASE_URL}/automato/${automatonId}/converter-afn-para-afd`, {
        method: 'POST', 
    });
    if (!response.ok) {
        throw new Error('Erro ao converter AFN para AFD');
    }
    return response.json();
}



async function minifyAutomaton(automatonId) {
    const response = await fetch(`${BASE_URL}/automato/${automatonId}/minimizar`);
    if (!response.ok) {
        const errorDetails = await response.json();
        console.log(errorDetails.detail)
        throw new Error(`Erro ao minimizar autômato: ${errorDetails.detail}`);
    }

    return response.json();
}


async function getAutomatonType(automatonId) {
    const response = await fetch(`${BASE_URL}/automato/${automatonId}/tipo`);
    if (!response.ok) {
        throw new Error('Erro ao obter tipo do autômato');
    }
    return response.json();
}

async function checkEquivalence(automatonId1, automatonId2) {
    const response = await fetch(`${BASE_URL}/automato/${automatonId1}/equivalencia/${automatonId2}`, {
        method: 'POST',
    });
    if (!response.ok) {
        throw new Error('Erro ao verificar equivalência entre autômatos');
    }
    return response.json();
}

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
