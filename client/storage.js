function saveAutomatonToLocalStorage(id, automaton) {
    let automatons = JSON.parse(localStorage.getItem('automatons')) || {};
    automatons[id] = automaton;
    localStorage.setItem('automatons', JSON.stringify(automatons));
}

function getAutomatonFromLocalStorage(id) {
    const automatons = JSON.parse(localStorage.getItem('automatons')) || {};
    return automatons[id] || null;
}


function setCurrentAutomatonId(id) {
    localStorage.setItem('currentAutomatonId', id);
}

function getCurrentAutomatonId() {
    return localStorage.getItem('currentAutomatonId');
}

export {
    saveAutomatonToLocalStorage,
    getAutomatonFromLocalStorage,
    getCurrentAutomatonId,
    setCurrentAutomatonId
};
