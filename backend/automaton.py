from typing import List
from pydantic import BaseModel

class Transition(BaseModel):
    current_state: str
    symbol: str
    next_state: str

class Automaton(BaseModel):
    states: List[str]
    alphabet: List[str]
    transitions: List[Transition]
    start_state: str
    accept_states: List[str]

#Define uma classe para representar as transições da Máquina de Turing
class Transition(BaseModel):
    current_state: str  # Estado atual
    symbol: str  # Símbolo lido na fita
    next_state: str  # Próximo estado
    write_symbol: str  # Símbolo a ser escrito na fita
    move_direction: str  # Direção do movimento da cabeça: 'L' para esquerda, 'R' para direita

# Define a classe principal para a Máquina de Turing
class TuringMachine(BaseModel):
    states: List[str]  # Lista de todos os estados da máquina
    input_alphabet: List[str]  # Alfabeto de entrada
    tape_alphabet: List[str]  # Alfabeto da fita
    blank_symbol: str  # Símbolo em branco da fita
    transitions: List[Transition]  # Lista de transições
    initial_state: str  # Estado inicial
    accept_state: str  # Estado de aceitação
    reject_state: str  # Estado de rejeição
    tape: List[str] = []  # A fita da máquina, inicializada como uma lista vazia
    head_position: int = 0  # Posição da cabeça de leitura/escrita, começando no início da fita
    
# Define um modelo para a entrada da rota, que inclui a máquina de Turing e a palavra de entrada
class TuringMachineInput(BaseModel):
    turing_machine: TuringMachine  # A Máquina de Turing
    input_word: str  # A palavra de entrada
