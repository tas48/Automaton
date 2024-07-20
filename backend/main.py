from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict   
from functions import create_automaton, read_automaton, recognize_string, afd_to_afn, afn_to_afd, is_afd, list_automata
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

@app.post("/automaton/{automaton_id}/to_afn", response_model=Automaton)
def convert_to_afn(automaton_id: int):
    afd = read_automaton(automaton_id)
    return afd_to_afn(afd)

@app.post("/automaton/{automaton_id}/to_afd", response_model=Automaton)
def convert_to_afd(automaton_id: int):
    afn = read_automaton(automaton_id)
    return afn_to_afd(afn)

@app.get("/automaton/{automaton_id}/type")
def get_automaton_type(automaton_id: int):
    automaton = read_automaton(automaton_id)
    if is_afd(automaton):
        return {"type": "AFD"}
    else:
        return {"type": "AFN"}
