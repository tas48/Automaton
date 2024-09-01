# API de Autômatos

Este projeto fornece uma API REST para gerenciar e converter autômatos (Autômatos Finitos). Ele usa FastAPI para lidar com solicitações e operações em autômatos.
##
## Pré-requisitos

- Python 3.12.4 ou superior

## Instalação

1. **Clone o repositório**:

    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Rodando o projeto** (Obrigatório):
    Nota: 
    ./run.bat
    ```
    
2. **Acesse a API**:

    Abra seu navegador e navegue até `http://127.0.0.1:8000/docs` para ver a documentação interativa da API fornecida pelo FastAPI.

## Endpoints

- **GET /**: Lista todos os autômatos
- **POST /automaton/**: Cria um novo autômato
- **GET /automaton/{automaton_id}**: Recupera um autômato específico por ID
- **POST /automaton/{automaton_id}/recognize**: Verifica se uma string é aceita por um autômato específico
- **POST /automaton/{automaton_id}/to_afn**: Converte um AFD para um AFN
- **POST /automaton/{automaton_id}/to_afd**: Converte um AFN para um AFD
- **GET /automaton/{automaton_id}/type**: Determina se um autômato é um AFD ou AFN

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.
