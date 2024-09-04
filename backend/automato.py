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

class Fita(object):
    simbolo_branco = " "
    
    def __init__(self, string_fita=""):
        self.__fita = dict(enumerate(string_fita))
        
    def __str__(self):
        s = ""
        min_index_utilizado = min(self.__fita.keys())
        max_index_utilizado = max(self.__fita.keys())
        for i in range(min_index_utilizado, max_index_utilizado + 1):
            s += self.__fita.get(i, Fita.simbolo_branco)
        return s
    
    def __getitem__(self, indice):
        return self.__fita.get(indice, Fita.simbolo_branco)

    def __setitem__(self, posicao, caractere):
        self.__fita[posicao] = caractere


class MaquinaDeTuring(object):
    def __init__(self, fita="", simbolo_branco=" ", estado_inicial="", estados_finais=None, funcao_transicao=None):
        self.__fita = Fita(fita)
        self.__posicao_cabeca = 0
        self.__simbolo_branco = simbolo_branco
        self.__estado_atual = estado_inicial
        self.__funcao_transicao = funcao_transicao if funcao_transicao else {}
        self.__estados_finais = set(estados_finais) if estados_finais else set()
        
    def obter_fita(self): 
        return str(self.__fita)
    
    def passo(self):
        caractere_sob_cabeca = self.__fita[self.__posicao_cabeca]
        x = (self.__estado_atual, caractere_sob_cabeca)
        if x in self.__funcao_transicao:
            y = self.__funcao_transicao[x]
            self.__fita[self.__posicao_cabeca] = y[1]
            if y[2] == "D":
                self.__posicao_cabeca += 1
            elif y[2] == "E": 
                self.__posicao_cabeca -= 1
            self.__estado_atual = y[0]

    def final(self):
        return self.__estado_atual in self.__estados_finais



    
