from typing import List, Dict, Set, Tuple
from fastapi import HTTPException
from automaton import Automaton, Transition
from itertools import chain, combinations
from collections import deque

# Banco de dados simulado
automata_db: Dict[int, Automaton] = {}
next_id = 1


def list_automata() -> Dict[int, Automaton]:
    return automata_db

def create_automaton(automaton: Automaton):    
    global next_id
    automata_db[next_id] = automaton
    next_id += 1
    automaton_id = next_id - 1
    raise HTTPException(
        status_code=201,
        detail={"automaton_id": automaton_id}
    )

def read_automaton(automaton_id: int) -> Automaton:
    if automaton_id in automata_db:
        return automata_db[automaton_id]
    raise HTTPException(status_code=404, detail="Automaton not found")

def recognize_string(automaton: Automaton, input_string: str) -> bool:
    current_states = {automaton.start_state}

    for symbol in input_string:
        if symbol not in automaton.alphabet:
            raise HTTPException(status_code=400, detail=f"Invalid symbol '{symbol}' in input string")
        
        next_states = set()
        for state in current_states:
            for transition in automaton.transitions:
                if transition.current_state == state and transition.symbol == symbol:
                    next_states.add(transition.next_state)
        current_states = next_states
    
    return any(state in automaton.accept_states for state in current_states)

def is_afd(automaton: Automaton) -> bool:
    transition_count = {}
    for transition in automaton.transitions:
        key = (transition.current_state, transition.symbol)
        if key in transition_count:
            transition_count[key] += 1
        else:
            transition_count[key] = 1
    
    for count in transition_count.values():
        if count > 1:
            return False
    return True

def montar_tabela(afn: Automaton) -> Automaton:
    # Gerar todos os novos estados como combinações de estados do AFN
    novos_estados = []
    for r in range(1, len(afn.states) + 1):
        novos_estados.extend([''.join(sorted(comb)) for comb in combinations(afn.states, r)])
    
    # Gerar todas as transições combinadas
    transicoes_combinadas = []
    for estado_atual_comb in novos_estados:
        for simbolo in afn.alphabet:
            estados_destino = set()
            for transicao in afn.transitions:
                if transicao.current_state in estado_atual_comb and transicao.symbol == simbolo:
                    estados_destino.add(transicao.next_state)

            # Se houver estados de destino, criar uma nova transição
            if estados_destino:
                estado_destino_comb = ''.join(sorted(estados_destino))
                transicoes_combinadas.append(Transition(
                    current_state=estado_atual_comb,
                    symbol=simbolo,
                    next_state=estado_destino_comb
                ))
    
    # Definir os novos estados de aceitação
    novos_estados_de_aceitacao = [estado for estado in novos_estados if any(estado.find(accept_state) != -1 for accept_state in afn.accept_states)]
    
    return Automaton(
        states=novos_estados,
        alphabet=afn.alphabet,
        transitions=transicoes_combinadas,
        start_state=afn.start_state,
        accept_states=novos_estados_de_aceitacao
    )

def eliminar_estados(afd: Automaton) -> Automaton:
    # Função para encontrar todos os estados acessíveis a partir do estado inicial
    def estados_acessiveis(estado_inicial: str, transicoes: List[Transition]) -> Set[str]:
        estados_visitados = set()
        fila = deque([estado_inicial])
        
        while fila:
            estado_atual = fila.popleft()
            if estado_atual not in estados_visitados:
                estados_visitados.add(estado_atual)
                # Enfileirar todos os próximos estados alcançáveis
                for transicao in transicoes:
                    if transicao.current_state == estado_atual and transicao.next_state not in estados_visitados:
                        fila.append(transicao.next_state)
        
        return estados_visitados
    
    # Encontrar todos os estados acessíveis
    estados_acessiveis_set = estados_acessiveis(afd.start_state, afd.transitions)
    
    # Filtrar transições para manter apenas as que têm estados acessíveis
    transicoes_filtradas = [
        transicao for transicao in afd.transitions
        if transicao.current_state in estados_acessiveis_set and transicao.next_state in estados_acessiveis_set
    ]
    
    # Filtrar estados para manter apenas os acessíveis
    estados_filtrados = [estado for estado in afd.states if estado in estados_acessiveis_set]
    
    # Filtrar estados de aceitação para manter apenas os acessíveis
    estados_de_aceitacao_filtrados = [estado for estado in afd.accept_states if estado in estados_acessiveis_set]

    return Automaton(
        states=estados_filtrados,
        alphabet=afd.alphabet,
        transitions=transicoes_filtradas,
        start_state=afd.start_state,
        accept_states=estados_de_aceitacao_filtrados
    )
    
def converter_afn_para_afd(afn: Automaton) -> Automaton:
    tabela_AFD = montar_tabela(afn)
    
    AFD_estados_inalcancaveis_eliminados = eliminar_estados(tabela_AFD)
    
    return AFD_estados_inalcancaveis_eliminados

def minimize_automaton(automaton: Automaton) -> Automaton:
    # Completar o autômato (adicionar estado D se necessário)
    complete_automaton(automaton)
    
    # Passo 1: Construir a tabela triangular para estados equivalentes
    pairs = create_state_pairs(automaton.states)
    
    # Passo 2: Marcar pares trivialmente não-equivalentes (estado final vs estado não-final)
    marked = mark_trivial_pairs(pairs, automaton.accept_states)
    
    # Passo 3: Marcar pares não-equivalentes baseados nas transições
    mark_non_equivalent_pairs(pairs, marked, automaton)
    
    # Passo 4: Unificar os estados equivalentes (não-marcados)
    unified_states, new_transitions = unify_equivalent_states(pairs, marked, automaton)
    
    # Passo 5: Construir o autômato minimizado
    minimized_automaton = Automaton(
        states=list(unified_states),
        alphabet=automaton.alphabet,
        transitions=new_transitions,
        start_state=automaton.start_state,
        accept_states=[state for state in unified_states if state in automaton.accept_states]
    )
    
    # Passo 6: Excluir estados inúteis
    minimized_automaton = eliminate_unreachable_states(minimized_automaton)
    
    return minimized_automaton

def complete_automaton(automaton: Automaton):
    missing_transitions = []
    d_state = "D"
    if d_state not in automaton.states:
        automaton.states.append(d_state)
    
    for state in automaton.states:
        for symbol in automaton.alphabet:
            if not any(t.current_state == state and t.symbol == symbol for t in automaton.transitions):
                missing_transitions.append(Transition(current_state=state, symbol=symbol, next_state=d_state))
    
    automaton.transitions.extend(missing_transitions)

def create_state_pairs(states: List[str]) -> List[Tuple[str, str]]:
    pairs = []
    for i in range(len(states)):
        for j in range(i + 1, len(states)):
            pairs.append((states[i], states[j]))
    return pairs

def mark_trivial_pairs(pairs: List[Tuple[str, str]], accept_states: List[str]) -> Dict[Tuple[str, str], bool]:
    marked = {}
    for q1, q2 in pairs:
        if (q1 in accept_states and q2 not in accept_states) or (q1 not in accept_states and q2 in accept_states):
            marked[(q1, q2)] = True
        else:
            marked[(q1, q2)] = False
    return marked

def mark_non_equivalent_pairs(pairs: List[Tuple[str, str]], marked: Dict[Tuple[str, str], bool], automaton: Automaton):
    changed = True
    while changed:
        changed = False
        for q1, q2 in pairs:
            if not marked[(q1, q2)]:
                for symbol in automaton.alphabet:
                    p1 = next((t.next_state for t in automaton.transitions if t.current_state == q1 and t.symbol == symbol), None)
                    p2 = next((t.next_state for t in automaton.transitions if t.current_state == q2 and t.symbol == symbol), None)
                    if p1 and p2 and p1 != p2:
                        if (p1, p2) in marked and marked[(p1, p2)]:
                            marked[(q1, q2)] = True
                            changed = True
                            break

def unify_equivalent_states(pairs: List[Tuple[str, str]], marked: Dict[Tuple[str, str], bool], automaton: Automaton) -> Tuple[set, List[Transition]]:
    equivalent_classes = {state: state for state in automaton.states}
    for q1, q2 in pairs:
        if not marked[(q1, q2)]:
            equivalent_classes[q2] = equivalent_classes[q1]
    
    new_states = set(equivalent_classes.values())
    new_transitions = []
    for t in automaton.transitions:
        current_state = equivalent_classes[t.current_state]
        next_state = equivalent_classes[t.next_state]
        new_transition = Transition(current_state=current_state, symbol=t.symbol, next_state=next_state)
        if new_transition not in new_transitions:
            new_transitions.append(new_transition)
    
    return new_states, new_transitions

def eliminate_unreachable_states(automaton: Automaton) -> Automaton:
    reachable = set()
    to_explore = {automaton.start_state}
    
    while to_explore:
        state = to_explore.pop()
        if state not in reachable:
            reachable.add(state)
            for t in automaton.transitions:
                if t.current_state == state:
                    to_explore.add(t.next_state)
    
    reachable_states = list(reachable)
    new_transitions = [t for t in automaton.transitions if t.current_state in reachable and t.next_state in reachable]
    
    return Automaton(
        states=reachable_states,
        alphabet=automaton.alphabet,
        transitions=new_transitions,
        start_state=automaton.start_state,
        accept_states=[s for s in automaton.accept_states if s in reachable]
    )