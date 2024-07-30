from typing import List, Dict
from fastapi import HTTPException
from automaton import Automaton, Transition

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

def converter_afn_para_afd(afn: Automaton) -> Automaton:
    def obter_closure(estados, transicoes):
        closure = set(estados)
        pilha = list(estados)
        while pilha:
            estado = pilha.pop()
            if (estado, '') in transicoes:
                for prox_estado in transicoes[(estado, '')]:
                    if prox_estado not in closure:
                        closure.add(prox_estado)
                        pilha.append(prox_estado)
        return closure

    def mover(estados, simbolo, transicoes):
        resultado = set()
        for estado in estados:
            if (estado, simbolo) in transicoes:
                resultado.update(transicoes[(estado, simbolo)])
        return resultado

    transicoes_afn = {}
    for t in afn.transitions:
        if (t.current_state, t.symbol) not in transicoes_afn:
            transicoes_afn[(t.current_state, t.symbol)] = set()
        transicoes_afn[(t.current_state, t.symbol)].add(t.next_state)

    estados_afd = []
    transicoes_afd = {}
    estados_finais_afd = set()
    estado_inicial_afd = frozenset(obter_closure({afn.start_state}, transicoes_afn))
    estados_afd.append(estado_inicial_afd)
    if any(estado in afn.accept_states for estado in estado_inicial_afd):
        estados_finais_afd.add(estado_inicial_afd)
    pilha = [estado_inicial_afd]

    while pilha:
        estado_atual = pilha.pop()
        for simbolo in afn.alphabet:
            prox_estados = obter_closure(mover(estado_atual, simbolo, transicoes_afn), transicoes_afn)
            if prox_estados:
                prox_estados_frozen = frozenset(prox_estados)
                if prox_estados_frozen not in estados_afd:
                    estados_afd.append(prox_estados_frozen)
                    pilha.append(prox_estados_frozen)
                    if any(estado in afn.accept_states for estado in prox_estados_frozen):
                        estados_finais_afd.add(prox_estados_frozen)
                transicoes_afd[(estado_atual, simbolo)] = prox_estados_frozen

    estados_afd = ["_".join(sorted(e)) for e in estados_afd]
    estados_finais_afd = ["_".join(sorted(e)) for e in estados_finais_afd]
    transicoes_afd = {(tuple(sorted(k[0])), k[1]): list(sorted(v)) for k, v in transicoes_afd.items()}

    return Automaton(
        states=estados_afd,
        alphabet=afn.alphabet,
        transitions=[Transition(current_state="_".join(sorted(k[0])), symbol=k[1], next_state="_".join(sorted(v))) for k, v in transicoes_afd.items()],
        start_state="_".join(sorted(estado_inicial_afd)),
        accept_states=estados_finais_afd
    )

def eliminar_estados_inalcancaveis(afd: Automaton) -> Automaton:
    estados_alcancaveis = set()
    pilha = [afd.start_state]
    while pilha:
        estado = pilha.pop()
        if estado not in estados_alcancaveis:
            estados_alcancaveis.add(estado)
            for t in afd.transitions:
                if t.current_state == estado and t.next_state not in estados_alcancaveis:
                    pilha.append(t.next_state)

    estados_finais_afd = [estado for estado in afd.accept_states if estado in estados_alcancaveis]
    transicoes_afd = [t for t in afd.transitions if t.current_state in estados_alcancaveis and t.next_state in estados_alcancaveis]

    return Automaton(
        states=list(estados_alcancaveis),
        alphabet=afd.alphabet,
        transitions=transicoes_afd,
        start_state=afd.start_state,
        accept_states=estados_finais_afd
    )

def converter_afn_para_afd_completo(afn: Automaton) -> Automaton:
    afd = converter_afn_para_afd(afn)
    afd = eliminar_estados_inalcancaveis(afd)
    return afd


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