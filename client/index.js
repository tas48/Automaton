import { exportToJson, importFromJson, isCanvasEmpty } from './automato.js';
import { createAutomaton, readAutomaton } from './context.js';
import { minifyAutomaton, recognizeString, convertAfnToAfd, checkEquivalence } from './context.js';
import { listAndDisplayAutomata } from './pagination.js';
import { saveAutomatonToLocalStorage, getCurrentAutomatonId } from './storage.js';



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


//Listener para monitorar o desenho no canvas e gerar o JSON
canvas.addEventListener('mouseup', () => {
    automatonJson = exportToJson(); 
    //console.log(automatonJson)
});


function disableButtons() {
    minifyButton.disabled = true;
    wordButton.disabled = true;
    convertButton.disabled = true;
    equalButton.disabled = true;
}

function enableButtons() {
    minifyButton.disabled = false;
    wordButton.disabled = false;
    convertButton.disabled = false;
    equalButton.disabled = true;
}



async function handleButtonClick(operation) {
    errorElement.textContent = '';

    if (operation !== 'list' && !currentAutomatonId) {
        alert('Nenhum automato selecionado!');
        return;
    }

    try {
        switch (operation) {
            case 'minify':
                try {
                    const minifiedAutomaton = await minifyAutomaton(currentAutomatonId);
                    importFromJson(minifiedAutomaton);
                } catch (error) {
                    console.error('Erro ao minimizar o autômato:', error);
                    errorElement.textContent = error.message;
                }
                break;

            case 'list':
                listAndDisplayAutomata();
                setupAutomatonIdWatch();
                break;

            case 'word':
                try {
                    const inputString = prompt("Digite a cadeia a ser reconhecida:");
                    const recognitionResult = await recognizeString(currentAutomatonId, inputString);
                 
                    if (recognitionResult.reconhecido) {
                        errorElement.style.color = 'green';
                        errorElement.textContent = 'A cadeia foi reconhecida com sucesso!';
                    } else {
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
                    currentAutomatonId = convertedAutomatonId.detail.id_automato; 
                    const convertedAutomaton = await readAutomaton(currentAutomatonId);
                    importFromJson(convertedAutomaton);
                    saveAutomatonToLocalStorage(currentAutomatonId, convertedAutomaton);
                } catch (error) {
                    console.error('Erro ao converter AFN para AFD:', error);
                }
                break;

            case 'equal':
                try {
                    const selectedAutomata = JSON.parse(localStorage.getItem('selectedAutomata'));
                    
                    if (!selectedAutomata || selectedAutomata.length < 2) {
                        alert('Por favor, selecione dois autômatos para comparar.');
                        return;
                    }
                    const automatonId1 = selectedAutomata[0];  
                    const automatonId2 = selectedAutomata[1]; 

                    const isEqual = await checkEquivalence(automatonId1, automatonId2);

                    if (isEqual) {
                        errorElement.style.color = 'green';
                        errorElement.textContent = 'Os autômatos são equivalentes.';
                    } else {
                        errorElement.style.color = 'red';
                        errorElement.textContent = 'Os autômatos não são equivalentes.';
                    }

                } catch (error) {
                    console.error('Erro ao verificar equivalência dos autômatos:', error);
                    errorElement.textContent = 'Erro ao verificar equivalência dos autômatos: ' + error.message;
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
        currentAutomatonId = response.detail.id_automato;
        const automatonFromBackend = await readAutomaton(currentAutomatonId);
        saveAutomatonToLocalStorage(currentAutomatonId, automatonFromBackend);
        alert(`Autômato salvo com sucesso! ID: ${currentAutomatonId}`);
    } catch (error) {
        document.getElementById('error').textContent = `Erro ao salvar autômato: ${error.message}`;
    }
}



minifyButton.addEventListener('click', () => handleButtonClick('minify'));
listButton.addEventListener('click', () => handleButtonClick('list'));
wordButton.addEventListener('click', () => handleButtonClick('word'));
convertButton.addEventListener('click', () => handleButtonClick('convert'));
equalButton.addEventListener('click', () => handleButtonClick('equal'));
saveButton.addEventListener('click', () => saveAutomaton());

function setupAutomatonIdWatch() { 
    listButton.addEventListener('click', () => {

        currentAutomatonId = getCurrentAutomatonId();

        if (currentAutomatonId) {
            console.log('ID do autômato atual após listButton:', currentAutomatonId);
        } else {
        console.error('Erro: currentAutomatonId é nulo ou indefinido.');
    }
    });
    
    document.getElementById('prev').addEventListener('click', () => {
        currentAutomatonId = getCurrentAutomatonId();
    });

    document.getElementById('next').addEventListener('click', () => {
        currentAutomatonId = getCurrentAutomatonId();
    });
    
    
    
}
