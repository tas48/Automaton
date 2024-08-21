from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict   
from functions import create_automaton, read_automaton, recognize_string, minimize_automaton, is_afd, list_automata, converter_afn_para_afd, normalize_automaton
from automaton import Automaton, Transition

app = FastAPI()

#ADICIONAR CODIGO DE PREVENÇÃO A CORS AQUI

@app.get("/", response_model=Dict[int, Automaton])
def list_automata_route():
    return list_automata()
    
@app.post("/automaton/", response_model=int)
def create_automaton_route(automaton: Automaton):
    return create_automaton(automaton)

@app.get("/automaton/{automaton_id}", response_model=Automaton)
def read_automaton_route(automaton_id: int):
    return read_automaton(automaton_id)

@app.post("/automaton/{automaton_id}/recognize")
def recognize_string_route(automaton_id: int, input_string: str):
    automaton = read_automaton(automaton_id)
    return {"recognized": recognize_string(automaton, input_string)}

@app.post("/automaton/{automaton_id}/convert-afn-to-afd", response_model=int)
def convert_afn_to_afd(automaton_id: int):
    afn = read_automaton(automaton_id)
    afd_convertido = converter_afn_para_afd(afn)
    
    return create_automaton(afd_convertido) 

@app.get("/automaton/{automaton_id}/minify")
def minify(automaton_id: int):
    automaton = read_automaton(automaton_id)
    if is_afd(automaton):
        afd = read_automaton(automaton_id)
        afd_minimizado = minimize_automaton(afd)
        return afd_minimizado
    else:
        raise HTTPException(status_code=400, detail="Error: The automaton is not an AFD. It is an AFN).")
    
    
@app.get("/automaton/{automaton_id}/type")
def get_automaton_type(automaton_id: int):
    automaton = read_automaton(automaton_id)
    if is_afd(automaton):
        return {"type": "AFD"}
    else:
        return {"type": "AFN"}

@app.post("/automaton/{automaton_id}/equivalence/{second_automaton_id}")
def equivalence_route(automaton_id: int, second_automaton_id: int) -> bool:
    try:
        # Ler e minimizar os autômatos
        minimized_automaton1 = minimize_automaton(read_automaton(automaton_id))
        minimized_automaton2 = minimize_automaton(read_automaton(second_automaton_id))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler os autômatos: {e}")

    # Padronização dos nomes para verificar equivalência
    normalized_automaton1 = normalize_automaton(minimized_automaton1)
    normalized_automaton2 = normalize_automaton(minimized_automaton2)

    # Comparação entre os autômatos minimizados e normalizados
    return (
        normalized_automaton1.states == normalized_automaton2.states and
        normalized_automaton1.alphabet == normalized_automaton2.alphabet and
        set((t.current_state, t.symbol, t.next_state) for t in normalized_automaton1.transitions) ==
        set((t.current_state, t.symbol, t.next_state) for t in normalized_automaton2.transitions) and
        normalized_automaton1.start_state == normalized_automaton2.start_state and
        set(normalized_automaton1.accept_states) == set(normalized_automaton2.accept_states)
    )
     