from typing import List
from pydantic import BaseModel

class Transicao(BaseModel):
    estado_atual: str
    simbolo: str
    proximo_estado: str

class Automato(BaseModel):
    estados: List[str]
    alfabeto: List[str]
    transicoes: List[Transicao]
    estado_inicial: str
    estados_de_aceitacao: List[str]

class MaquinaDeTuring(BaseModel):
    estados: List[str]
    alfabeto_entrada: List[str]
    alfabeto_fita: List[str]
    simbolo_branco: str
    transicoes: List[Transicao]
    estado_inicial: str
    estado_aceitacao: str
    estado_rejeicao: str
    fita: List[str] = []
    posicao_cabeca: int = 0

class TransicaoMaquinaDeTuring(BaseModel):
    estado_atual: str
    simbolo: str
    proximo_estado: str
    escrever_simbolo: str
    direcao_movimento: str
    
class EntradaMaquinaDeTuring(BaseModel):
    maquina_turing: MaquinaDeTuring
    palavra_entrada: str
