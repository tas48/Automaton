from typing import List, Dict, Set
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

def minimizar_afd(afd: Automaton) -> Automaton:
    estados = afd.states
    estados_finais = set(afd.accept_states)
    alfabeto = afd.alphabet
    transicoes = { (t.current_state, t.symbol): t.next_state for t in afd.transitions }

    P = [estados_finais, set(estados) - estados_finais]
    W = [estados_finais.copy()]

    while W:
        A = W.pop()
        for simbolo in alfabeto:
            X = {estado for estado in estados if (estado, simbolo) in transicoes and transicoes[(estado, simbolo)] in A}
            new_P = []
            for Y in P:
                intersecao = Y & X
                diferenca = Y - X
                if intersecao and diferenca:
                    new_P.extend([intersecao, diferenca])
                    if Y in W:
                        W.remove(Y)
                        W.extend([intersecao, diferenca])
                    else:
                        if len(intersecao) <= len(diferenca):
                            W.append(intersecao)
                        else:
                            W.append(diferenca)
                else:
                    new_P.append(Y)
            P = new_P

    novo_estado = {}
    for particao in P:
        representacao = frozenset(particao)
        for estado in particao:
            novo_estado[estado] = representacao

    novos_estados = set(novo_estado.values())
    novo_estado_inicial = novo_estado[afd.start_state]
    novos_estados_finais = {novo_estado[estado] for estado in afd.accept_states}
    novas_transicoes = {}
    for (estado, simbolo), prox_estado in transicoes.items():
        novas_transicoes[(novo_estado[estado], simbolo)] = novo_estado[prox_estado]

    return Automaton(
        states=["_".join(sorted(e)) for e in novos_estados],
        alphabet=alfabeto,
        transitions=[Transition(current_state="_".join(sorted(k[0])), symbol=k[1], next_state="_".join(sorted(v))) for k, v in novas_transicoes.items()],
        start_state="_".join(sorted(novo_estado_inicial)),
        accept_states=["_".join(sorted(e)) for e in novos_estados_finais]
    )