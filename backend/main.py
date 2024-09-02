from fastapi import FastAPI, HTTPException
from typing import List, Dict, Set, Tuple  
from funcoes import criar_automato, ler_automato, reconhecer_cadeia, minimizar_automato, eh_afd, listar_automatos, converter_afn_para_afd, normalizar_automato, executar_maquina_turing
from automato import Transicao, Automato, MaquinaDeTuring, TransicaoMaquinaDeTuring
from fastapi.middleware.cors import CORSMiddleware
from itertools import chain, combinations


app = FastAPI()

origens = [
    "http://localhost:5500",
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=Dict[int, Automato])
def listar_automatos_rota():
    return listar_automatos()
    
@app.post("/automato/", response_model=int)
def criar_automato_rota(automato: Automato):
    if(automato):
        return criar_automato(automato)
    else:
        raise HTTPException(status_code=400, detail="Conteúdo nulo")

@app.get("/automato/{automato_id}", response_model=Automato)
def ler_automato_rota(automato_id: int):
    if(automato_id):
        return ler_automato(automato_id)
    else:
        raise HTTPException(status_code=400, detail="Id nulo")

@app.post("/automato/{automato_id}/reconhecer")
def reconhecer_cadeia_rota(automato_id: int, cadeia: str):
    print(automato_id, cadeia)
    if(automato_id):
        print('to aqui')
        automato = ler_automato(automato_id)
        print(automato)
        return {"reconhecido": reconhecer_cadeia(automato, cadeia)}
    else:
        raise HTTPException(status_code=400, detail="Id nulo")
    

@app.post("/automato/{automato_id}/converter-afn-para-afd", response_model=int)
def converter_afn_para_afd_rota(automato_id: int):
    if(automato_id):
        afn = ler_automato(automato_id)
        afd_convertido = converter_afn_para_afd(afn)
        return criar_automato(afd_convertido)
    else:
        raise HTTPException(status_code=400, detail="Id nulo")
         

@app.get("/automato/{automato_id}/minimizar")
def minimizar_rota(automato_id: int):
    automato = ler_automato(automato_id)
    if eh_afd(automato):
        afd = ler_automato(automato_id)
        afd_minimizado = minimizar_automato(afd)
        return afd_minimizado
    else:
        raise HTTPException(status_code=400, detail="O autômato não é um AFD. É um AFN.")

@app.get("/automato/{automato_id}/tipo")
def obter_tipo_automato(automato_id: int):
    if(automato_id):
        automato = ler_automato(automato_id)
        if eh_afd(automato):
            return {"tipo": "AFD"}
        else:
            return {"tipo": "AFN"}
    else:
        raise HTTPException(status_code=400, detail="Id nulo")

@app.post("/automato/{automato_id}/equivalencia/{segundo_automato_id}")
def equivalencia_rota(automato_id: int, segundo_automato_id: int) -> bool:
    try:
        automato_minimizado1 = minimizar_automato(ler_automato(automato_id))
        automato_minimizado2 = minimizar_automato(ler_automato(segundo_automato_id))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler os autômatos: {e}")

    automato_normalizado1 = normalizar_automato(automato_minimizado1)
    automato_normalizado2 = normalizar_automato(automato_minimizado2)

    return (
        automato_normalizado1.estados == automato_normalizado2.estados and
        automato_normalizado1.alfabeto == automato_normalizado2.alfabeto and
        set((t.estado_atual, t.simbolo, t.proximo_estado) for t in automato_normalizado1.transicoes) ==
        set((t.estado_atual, t.simbolo, t.proximo_estado) for t in automato_normalizado2.transicoes) and
        automato_normalizado1.estado_inicial == automato_normalizado2.estado_inicial and
        set(automato_normalizado1.estados_de_aceitacao) == set(automato_normalizado2.estados_de_aceitacao)
    )
    
@app.post("/MaquinaDeTuring/executar/{palavra}")
def executar_maquina_turing_rota(palavra: str, maquina_de_turing: MaquinaDeTuring):
    resultado = executar_maquina_turing(maquina_de_turing, palavra)
    return {"resultado": resultado}

