from typing import List, Dict
from fastapi import HTTPException
from automaton import Automaton, Transition

# Banco de dados simulado
automata_db: Dict[int, Automaton] = {}
next_id = 1


def list_automata() -> Dict[int, Automaton]:
    return automata_db

def create_automaton(automaton: Automaton) -> int:
    global next_id
    automata_db[next_id] = automaton
    next_id += 1
    return next_id - 1

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

def afd_to_afn(afd: Automaton) -> Automaton:
    afn_transitions = [Transition(
        current_state=transition.current_state,
        symbol=transition.symbol,
        next_state=transition.next_state
    ) for transition in afd.transitions]

    return Automaton(
        states=afd.states,
        alphabet=afd.alphabet,
        transitions=afn_transitions,
        start_state=afd.start_state,
        accept_states=afd.accept_states
    )

def afn_to_afd(afn: Automaton) -> Automaton:
    state_sets = [frozenset([afn.start_state])]
    new_states = []
    new_transitions = []
    state_mapping = {frozenset([afn.start_state]): 'S0'}
    state_count = 1

    while state_sets:
        current_set = state_sets.pop(0)
        if current_set not in new_states:
            new_states.append(current_set)
            for symbol in afn.alphabet:
                next_set = frozenset(
                    sum([list(transition.next_state for transition in afn.transitions 
                              if transition.current_state == state and transition.symbol == symbol) 
                         for state in current_set], [])
                )
                if next_set not in state_mapping:
                    state_mapping[next_set] = f'S{state_count}'
                    state_count += 1
                if next_set:
                    new_transitions.append(Transition(
                        current_state=state_mapping[current_set],
                        symbol=symbol,
                        next_state=state_mapping[next_set]
                    ))
                if next_set and next_set not in state_sets:
                    state_sets.append(next_set)

    new_accept_states = [state_mapping[state] for state in new_states if any(s in afn.accept_states for s in state)]

    return Automaton(
        states=list(state_mapping.values()),
        alphabet=afn.alphabet,
        transitions=new_transitions,
        start_state=state_mapping[frozenset([afn.start_state])],
        accept_states=new_accept_states
    )

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
