import { exportToJson, importFromJson, isCanvasEmpty } from './automato.js';
import { createAutomaton, readAutomaton } from './context.js';
import { minifyAutomaton, listAutomata, recognizeString, convertAfnToAfd } from './context.js';
import { listAndDisplayAutomata } from './pagination.js';
import { saveAutomatonToLocalStorage, getAutomatonFromLocalStorage } from './storage.js';



// Selecionar elementos da interface
const canvas = document.getElementById('automatoCanvas');
const minifyButton = document.getElementById('minify');
const listButton = document.getElementById('list');
const wordButton = document.getElementById('word');
const convertButton = document.getElementById('convert');
const equalButton = document.getElementById('equal');
const errorElement = document.getElementById('error');
const saveButton = document.getElementById('save');
let automatonJson = null;
let currentAutomatonId = null;

disableButtons();
// Listener para monitorar o desenho no canvas e gerar o JSON
canvas.addEventListener('mouseup', () => {
    automatonJson = exportToJson(); 
    console.log(automatonJson)
    if (automatonJson) {
        enableButtons(); // Habilita os botões se o JSON for gerado
    }
});

// Função para desabilitar os botões
function disableButtons() {
    minifyButton.disabled = true;
    wordButton.disabled = true;
    convertButton.disabled = true;
    equalButton.disabled = true;
}

// Função para habilitar os botões
function enableButtons() {
    minifyButton.disabled = false;
    wordButton.disabled = false;
    convertButton.disabled = false;
    equalButton.disabled = true;
}



async function handleButtonClick(operation) {
    errorElement.textContent = ''; // Limpa mensagens de erro anteriores

    // if (!currentAutomatonId) {
    //     alert('Nenhum autômato ativo. Salve um autômato primeiro.');
    //     return;
    // }

    try {
        switch (operation) {
            case 'minify':
                try {
                    const minifiedAutomaton = await minifyAutomaton(currentAutomatonId);
                    importFromJson(minifiedAutomaton);
                    saveAutomatonToLocalStorage(currentAutomatonId, minifiedAutomaton); // Atualizar no localStorage
                } catch (error) {
                    console.error('Erro ao minimizar o autômato:', error);
                    errorElement.textContent = error.message;
                }
                break;

            case 'list':
                try {
                    const automataList = await listAutomata();
                    listAndDisplayAutomata();

                } catch (error) {
                    errorElement.textContent = 'Erro ao listar autômatos: ' + error.message;
                }
                break;

            case 'word':
                try {
                    const inputString = prompt("Digite a cadeia a ser reconhecida:");
                    const recognitionResult = await recognizeString(currentAutomatonId, inputString);
                 
                    if(recognitionResult.recognized){
                        errorElement.style.color = 'green';
                        errorElement.textContent = 'A cadeia foi reconhecida com sucesso!';
                    }
                    else {
                        errorElement.style.color = 'red';
                        errorElement.textContent = 'A cadeia não foi aceita!';
                    }
                    
                } catch (error) {
                    errorElement.textContent = 'Erro no servidor';
                }
                break;

            case 'convert':
                try {
                    const convertedAutomatonId = await convertAfnToAfd(currentAutomatonId);
                    
                    currentAutomatonId = convertedAutomatonId; // Atualizar o ID do autômato ativo
                    const convertedAutomaton = await readAutomaton(convertedAutomatonId);
                    importFromJson(convertedAutomaton);
                    saveAutomatonToLocalStorage(currentAutomatonId, convertedAutomaton); // Atualizar no localStorage
                } catch (error) {
                    console.error('Erro ao converter AFN para AFD:', error);
                }
                break;

            default:
                console.error('Operação desconhecida:', operation);
        }
    } catch (error) {
        console.error('Erro ao salvar ou ler o autômato:', error);
    }
}


async function saveAutomaton() {
    try {
        const response = await createAutomaton(JSON.parse(automatonJson));
        currentAutomatonId = response.detail.automaton_id; // Definir como autômato ativo
        const automatonFromBackend = await readAutomaton(currentAutomatonId);
        saveAutomatonToLocalStorage(currentAutomatonId, automatonFromBackend);
        alert(`Autômato salvo com sucesso! ID: ${currentAutomatonId}`);
    } catch (error) {
        document.getElementById('error').textContent = `Erro ao salvar autômato: ${error.message}`;
    }
}


// Adiciona os listeners para os botões
minifyButton.addEventListener('click', () => handleButtonClick('minify'));
listButton.addEventListener('click', () => handleButtonClick('list'));
wordButton.addEventListener('click', () => handleButtonClick('word'));
convertButton.addEventListener('click', () => handleButtonClick('convert'));
saveButton.addEventListener('click', () => saveAutomaton());