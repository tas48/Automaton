// Função para salvar o autômato no localStorage
function saveAutomatonToLocalStorage(id, automaton) {
    let automatons = JSON.parse(localStorage.getItem('automatons')) || {};
    automatons[id] = automaton;
    localStorage.setItem('automatons', JSON.stringify(automatons));
}

// Função para recuperar um autômato do localStorage pelo ID
function getAutomatonFromLocalStorage(id) {
    const automatons = JSON.parse(localStorage.getItem('automatons')) || {};
    return automatons[id] || null;
}

export {
    saveAutomatonToLocalStorage,
    getAutomatonFromLocalStorage
};
