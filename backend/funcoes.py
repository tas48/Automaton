from typing import List, Dict, Set, Tuple
from fastapi import HTTPException
from automato import Transicao, Automato, MaquinaDeTuring, TransicaoMaquinaDeTuring, EntradaMaquinaDeTuring
from itertools import chain, combinations
from collections import deque

automatos_db: Dict[int, Automato] = {}
proximo_id = 1

def listar_automatos() -> Dict[int, Automato]:
    return automatos_db

def criar_automato(automato: Automato):
    global proximo_id
    automatos_db[proximo_id] = automato
    proximo_id += 1
    id_automato = proximo_id - 1
    raise HTTPException(
        status_code=201,
        detail={"id_automato": id_automato}
    )

def ler_automato(id_automato: int) -> Automato:
    if id_automato in automatos_db:
        return automatos_db[id_automato]
    raise HTTPException(status_code=404, detail="Automato não encontrado")

def reconhecer_cadeia(automato: Automato, palavra_entrada: str) -> bool:
    estados_atuais = {automato.estado_inicial}

    for simbolo in palavra_entrada:
        if simbolo not in automato.alfabeto:
            raise HTTPException(status_code=400, detail=f"Símbolo inválido '{simbolo}' na palavra de entrada")
        
        proximos_estados = set()
        for estado in estados_atuais:
            for transicao in automato.transicoes:
                if transicao.estado_atual == estado and transicao.simbolo == simbolo:
                    proximos_estados.add(transicao.proximo_estado)
        estados_atuais = proximos_estados
    
    return any(estado in automato.estados_de_aceitacao for estado in estados_atuais)

def eh_afd(automato: Automato) -> bool:
    contagem_transicoes = {}
    for transicao in automato.transicoes:
        chave = (transicao.estado_atual, transicao.simbolo)
        if chave in contagem_transicoes:
            contagem_transicoes[chave] += 1
        else:
            contagem_transicoes[chave] = 1
    
    for contagem in contagem_transicoes.values():
        if contagem > 1:
            return False
    return True

    
def converter_afn_para_afd(afn: Automato) -> Automato:
    tabela_afd = montar_tabela(afn)
    afd_sem_inalcancaveis = eliminar_estados(tabela_afd)
    return afd_sem_inalcancaveis

def montar_tabela(afn: Automato) -> Automato:
    novos_estados = []
    for r in range(1, len(afn.estados) + 1):
        novos_estados.extend([''.join(sorted(comb)) for comb in combinations(afn.estados, r)])
    
    transicoes_combinadas = []
    for estado_atual_comb in novos_estados:
        for simbolo in afn.alfabeto:
            estados_destino = set()
            for transicao in afn.transicoes:
                if transicao.estado_atual in estado_atual_comb and transicao.simbolo == simbolo:
                    estados_destino.add(transicao.proximo_estado)

            if estados_destino:
                estado_destino_comb = ''.join(sorted(estados_destino))
                transicoes_combinadas.append(Transicao(
                    estado_atual=estado_atual_comb,
                    simbolo=simbolo,
                    proximo_estado=estado_destino_comb
                ))
    
    novos_estados_de_aceitacao = [estado for estado in novos_estados if any(estado.find(estado_aceitacao) != -1 for estado_aceitacao in afn.estados_de_aceitacao)]
    
    return Automato(
        estados=novos_estados,
        alfabeto=afn.alfabeto,
        transicoes=transicoes_combinadas,
        estado_inicial=afn.estado_inicial,
        estados_de_aceitacao=novos_estados_de_aceitacao
    )

def eliminar_estados(afd: Automato) -> Automato:
    def estados_acessiveis(estado_inicial: str, transicoes: List[Transicao]) -> Set[str]:
        visitados = set()
        fila = deque([estado_inicial])
        
        while fila:
            estado_atual = fila.popleft()
            if estado_atual not in visitados:
                visitados.add(estado_atual)
                for transicao in transicoes:
                    if transicao.estado_atual == estado_atual and transicao.proximo_estado not in visitados:
                        fila.append(transicao.proximo_estado)
        
        return visitados
    
    acessiveis = estados_acessiveis(afd.estado_inicial, afd.transicoes)
    
    transicoes_filtradas = [
        transicao for transicao in afd.transicoes
        if transicao.estado_atual in acessiveis and transicao.proximo_estado in acessiveis
    ]
    
    estados_filtrados = [estado for estado in afd.estados if estado in acessiveis]
    aceitacao_filtrados = [estado for estado in afd.estados_de_aceitacao if estado in acessiveis]

    return Automato(
        estados=estados_filtrados,
        alfabeto=afd.alfabeto,
        transicoes=transicoes_filtradas,
        estado_inicial=afd.estado_inicial,
        estados_de_aceitacao=aceitacao_filtrados
    )

def minimizar_automato(automato: Automato) -> Automato:
    completar_automato(automato)
    pares = criar_pares_estados(automato.estados)
    marcados = marcar_pares_triviais(pares, automato.estados_de_aceitacao)
    marcar_pares_nao_equivalentes(pares, marcados, automato)
    estados_unificados, transicoes_novas = unificar_estados_equivalentes(pares, marcados, automato)
    
    automato_minimizado = Automato(
        estados=list(estados_unificados),
        alfabeto=automato.alfabeto,
        transicoes=transicoes_novas,
        estado_inicial=automato.estado_inicial,
        estados_de_aceitacao=[estado for estado in estados_unificados if estado in automato.estados_de_aceitacao]
    )
    
    automato_minimizado = eliminar_estados_inuteis(automato_minimizado)
    
    automato_minimizado.estados = [estado for estado in automato_minimizado.estados if estado != 'D']
    automato_minimizado.transicoes = [t for t in automato_minimizado.transicoes if t.estado_atual != 'D' and t.proximo_estado != 'D']
    
    automato_minimizado.estados.sort()
    automato_minimizado.transicoes.sort(key=lambda t: (t.estado_atual, t.simbolo, t.proximo_estado))
    
    automato.estados = automato_minimizado.estados
    automato.alfabeto = automato_minimizado.alfabeto
    automato.transicoes = automato_minimizado.transicoes
    automato.estado_inicial = automato_minimizado.estado_inicial
    automato.estados_de_aceitacao = automato_minimizado.estados_de_aceitacao

    return automato_minimizado

def completar_automato(automato: Automato):
    transicoes_faltantes = []
    estado_d = "D"
    if estado_d not in automato.estados:
        automato.estados.append(estado_d)
    
    for simbolo in automato.alfabeto:
        if not any(t.estado_atual == estado_d and t.simbolo == simbolo for t in automato.transicoes):
            automato.transicoes.append(Transicao(estado_atual=estado_d, simbolo=simbolo, proximo_estado=estado_d))
     
    for estado in automato.estados:
        for simbolo in automato.alfabeto:
            if not any(t.estado_atual == estado and t.simbolo == simbolo for t in automato.transicoes):
                transicoes_faltantes.append(Transicao(estado_atual=estado, simbolo=simbolo, proximo_estado=estado_d))
                
    automato.transicoes.extend(transicoes_faltantes)

def criar_pares_estados(estados: List[str]) -> List[Tuple[str, str]]:
    pares = []
    for i in range(len(estados)):
        for j in range(i + 1, len(estados)):
            pares.append((estados[i], estados[j]))
    return pares

def marcar_pares_triviais(pares: List[Tuple[str, str]], estados_de_aceitacao: List[str]) -> Dict[Tuple[str, str], bool]:
    marcados = {}
    for q1, q2 in pares:
        if (q1 in estados_de_aceitacao and q2 not in estados_de_aceitacao) or (q1 not in estados_de_aceitacao and q2 in estados_de_aceitacao):
            marcados[(q1, q2)] = True
        else:
            marcados[(q1, q2)] = False
    return marcados

def marcar_pares_nao_equivalentes(pares: List[Tuple[str, str]], marcados: Dict[Tuple[str, str], bool], automato: Automato):
    alterado = True
    while alterado:
        alterado = False
        for q1, q2 in pares:
            if not marcados[(q1, q2)]:
                for simbolo in automato.alfabeto:
                    p1 = next((t.proximo_estado for t in automato.transicoes if t.estado_atual == q1 and t.simbolo == simbolo), None)
                    p2 = next((t.proximo_estado for t in automato.transicoes if t.estado_atual == q2 and t.simbolo == simbolo), None)
                    if p1 and p2 and p1 != p2:
                        par = (p1, p2) if (p1, p2) in marcados else (p2, p1)
                        if par in marcados and marcados.get(par, False):
                            marcados[(q1, q2)] = True
                            alterado = True
                            break

def unificar_estados_equivalentes(pares: List[Tuple[str, str]], marcados: Dict[Tuple[str, str], bool], automato: Automato) -> Tuple[set, List[Transicao]]:
    classes_equivalentes = {estado: estado for estado in automato.estados}
    for q1, q2 in pares:
        if not marcados[(q1, q2)]:
            classes_equivalentes[q2] = classes_equivalentes[q1]
    
    estados_unificados = set(classes_equivalentes.values())
    transicoes_novas = []
    for t in automato.transicoes:
        estado_atual = classes_equivalentes[t.estado_atual]
        proximo_estado = classes_equivalentes[t.proximo_estado]
        transicao_nova = Transicao(estado_atual=estado_atual, simbolo=t.simbolo, proximo_estado=proximo_estado)
        if transicao_nova not in transicoes_novas:
            transicoes_novas.append(transicao_nova)
    
    return estados_unificados, transicoes_novas

def eliminar_estados_inuteis(automato: Automato) -> Automato:
    alcancaveis = set()
    para_explorar = {automato.estado_inicial}
    
    while para_explorar:
        estado = para_explorar.pop()
        if estado not in alcancaveis:
            alcancaveis.add(estado)
            for t in automato.transicoes:
                if t.estado_atual == estado:
                    para_explorar.add(t.proximo_estado)
    
    estados_alcancaveis = list(alcancaveis)
    transicoes_novas = [t for t in automato.transicoes if t.estado_atual in alcancaveis and t.proximo_estado in alcancaveis]
    
    return Automato(
        estados=sorted(estados_alcancaveis),
        alfabeto=automato.alfabeto,
        transicoes=transicoes_novas,
        estado_inicial=automato.estado_inicial,
        estados_de_aceitacao=[s for s in sorted(automato.estados_de_aceitacao) if s in alcancaveis]
    )
    
def normalizar_automato(automato: Automato) -> Automato:
    mapeamento_estados = {estado: f'q{i}' for i, estado in enumerate(sorted(automato.estados))}
    
    transicoes_normalizadas = [
        Transicao(
            estado_atual=mapeamento_estados[t.estado_atual],
            simbolo=t.simbolo,
            proximo_estado=mapeamento_estados[t.proximo_estado]
        )
        for t in automato.transicoes
    ]
    
    automato_normalizado = Automato(
        estados=sorted(mapeamento_estados.values()),
        alfabeto=automato.alfabeto,
        transicoes=transicoes_normalizadas,
        estado_inicial=mapeamento_estados[automato.estado_inicial],
        estados_de_aceitacao=[mapeamento_estados[estado] for estado in automato.estados_de_aceitacao]
    )
    
    return automato_normalizado

def inicializar_fita(tm: MaquinaDeTuring, palavra_entrada: str):
    tm.fita = list(palavra_entrada) + [tm.simbolo_branco]
    tm.posicao_cabeca = 0

def executar_maquina_turing(tm: MaquinaDeTuring, palavra_entrada: str) -> str:
    inicializar_fita(tm, palavra_entrada)
    estado_atual = tm.estado_inicial

    while True:
        if estado_atual == tm.estado_aceitacao:
            return "Sim"
        if estado_atual == tm.estado_rejeicao:
            return "Não"

        simbolo_sob_cabeca = tm.fita[tm.posicao_cabeca]
        transicao_encontrada = False

        for transicao in tm.transicoes:
            if (transicao.estado_atual == estado_atual and
                transicao.simbolo == simbolo_sob_cabeca):
                
                tm.fita[tm.posicao_cabeca] = transicao.escrever_simbolo
                estado_atual = transicao.proximo_estado

                if transicao.direcao_movimento == 'R':
                    tm.posicao_cabeca += 1
                    if tm.posicao_cabeca >= len(tm.fita):
                        tm.fita.append(tm.simbolo_branco)
                elif transicao.direcao_movimento == 'L':
                    tm.posicao_cabeca -= 1
                    if tm.posicao_cabeca < 0:
                        tm.fita.insert(0, tm.simbolo_branco)
                        tm.posicao_cabeca = 0

                transicao_encontrada = True
                break

        if not transicao_encontrada:
            return "Não"

