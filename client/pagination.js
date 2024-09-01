import { listAutomata } from './context.js';
import { importFromJson, clearCanvas } from './automato.js';
import { getCurrentAutomatonId, setCurrentAutomatonId } from './storage.js';

let automata = [];
let currentPage = 0;
let selectedAutomata = []; // Lista para armazenar IDs dos automatos marcados

export async function listAndDisplayAutomata() {
    const errorElement = document.getElementById('error');
    errorElement.textContent = '';

    try {
        const automataObj = await listAutomata();
        automata = Object.values(automataObj);

        if (automata.length > 0) {
            showPagination();
            displayAutomaton(currentPage);
        } else {
            errorElement.textContent = 'Nenhum autômato encontrado.';
            return null;
        }
    } catch (error) {
        errorElement.textContent = 'Erro ao listar autômatos: ' + error.message;
        return null;
    }
}

function showPagination() {
    document.getElementById('pagination').style.display = 'block';
    updatePageInfo();
}

function updatePageInfo() {
    const pageInfo = document.getElementById('pageInfo');
    pageInfo.textContent = `Página ${currentPage + 1} de ${automata.length}`;
}

function displayAutomaton(pageIndex) {
    const automatonJson = automata[pageIndex];
    importFromJson(automatonJson);
    const automatonId = pageIndex + 1;
    setCurrentAutomatonId(automatonId);
    updateCheckboxState(); // Atualiza o estado do checkbox
}

function updateCheckboxState() {
    const selectCheckbox = document.getElementById('select');
    const currentId = getCurrentAutomatonId();
    selectCheckbox.checked = selectedAutomata.includes(currentId);
}

document.getElementById('prev').addEventListener('click', () => {
    if (currentPage > 0) {
        currentPage--;
        displayAutomaton(currentPage);
        updatePageInfo();
    }
});

document.getElementById('next').addEventListener('click', () => {
    if (currentPage < automata.length - 1) {
        currentPage++;
        displayAutomaton(currentPage);
        updatePageInfo();
    }
});

document.getElementById('exitPagination').addEventListener('click', () => {
    document.getElementById('pagination').style.display = 'none';
    clearCanvas();
    document.getElementById('error').textContent = '';
});

// Captura o checkbox e adiciona o event listener
document.getElementById('select').addEventListener('change', (event) => {
    const currentId = getCurrentAutomatonId();

    if (event.target.checked) {
        if (selectedAutomata.length < 2) {
            selectedAutomata.push(currentId);
            localStorage.setItem('selectedAutomata', JSON.stringify(selectedAutomata));
        } else {
            alert('Você só pode selecionar até 2 autômatos.');
            event.target.checked = false;
        }
    } else {
        selectedAutomata = selectedAutomata.filter(id => id !== currentId);
        localStorage.setItem('selectedAutomata', JSON.stringify(selectedAutomata));
    }
});
