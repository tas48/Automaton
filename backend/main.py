from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict   
from functions import create_automaton, read_automaton, recognize_string, afn_to_afd, is_afd, list_automata, converter_afn_para_afd_completo, minimizar_afd
from automaton import Automaton, Transition

app = FastAPI()

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
    afd_completo = converter_afn_para_afd_completo(afn)
    afd_minimizado = minimizar_afd(afd_completo)
    
    return create_automaton(afd_minimizado) 


@app.get("/automaton/{automaton_id}/minify")
def minify(automaton_id: int):
    automaton = read_automaton(automaton_id)
    if is_afd(automaton):
        afd = read_automaton(automaton_id)
        afd_minimizado = minimizar_afd(afd)
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
def equivalence_route(automaton_id: int, second_automaton_id: int, input_string: str):
    try:
        automaton1 = read_automaton(automaton_id)
        automaton2 = read_automaton(second_automaton_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler os autômatos: {e}")

    try:
        recognizes_automaton1 = recognize_string(automaton1, input_string)
        recognizes_automaton2 = recognize_string(automaton2, input_string)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao reconhecer a string nos autômatos: {e}")

    are_equivalent = recognizes_automaton1 == recognizes_automaton2

    return {
        "automaton1_accepts": int(recognizes_automaton1),
        "automaton2_accepts": int(recognizes_automaton2),
        "are_equivalent": are_equivalent
    }