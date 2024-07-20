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
