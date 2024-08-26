import { listAutomata } from './context.js';
import { importFromJson, clearCanvas } from './automato.js';

let automata = [];  // Lista de autômatos
let currentPage = 0;  // Página atual

// Função para listar e exibir os autômatos
export async function listAndDisplayAutomata() {
    const errorElement = document.getElementById('error');
    errorElement.textContent = '';  // Limpa mensagens de erro anteriores

    try {
        const automataObj = await listAutomata();  // Obter a lista de autômatos do backend
        
        // Converte o objeto em um array
        automata = Object.values(automataObj);

        if (automata.length > 0) {
            showPagination();  // Mostrar a estrutura de paginação
            displayAutomaton(currentPage);  // Exibir o primeiro autômato
        } else {
            errorElement.textContent = 'Nenhum autômato encontrado.';
        }
    } catch (error) {
        errorElement.textContent = 'Erro ao listar autômatos: ' + error.message;
    }
}

// Função para mostrar a estrutura de paginação
function showPagination() {
    document.getElementById('pagination').style.display = 'block';  // Revelar a estrutura de paginação
    updatePageInfo();
}

// Função para atualizar as informações da página
function updatePageInfo() {
    const pageInfo = document.getElementById('pageInfo');
    pageInfo.textContent = `Página ${currentPage + 1} de ${automata.length}`;
}

// Função para exibir o autômato no canvas
function displayAutomaton(pageIndex) {
    const automatonJson = automata[pageIndex];
    importFromJson(automatonJson);  // Desenha o autômato no canvas
}

// Configuração dos botões de navegação
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
    document.getElementById('pagination').style.display = 'none'; // Oculta a estrutura de paginação
    clearCanvas(); // Limpa o canvas para remover o autômato desenhado
    document.getElementById('error').textContent = ''; // Limpa mensagens de erro
});
