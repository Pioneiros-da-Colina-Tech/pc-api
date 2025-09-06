# Documentação da API - Patrimônio

Endpoints para o gerenciamento completo do inventário de materiais do clube, incluindo o registro de itens, a solicitação por parte das unidades e a aprovação e controle por parte da diretoria.

## 1. Gerenciar Patrimônio (Inventário)

Endpoints para a diretoria visualizar, adicionar, editar e remover itens do inventário do clube.

* **`GET /patrimonio`**
    * **Descrição:** Retorna a lista completa de todos os itens do inventário.
    * **Tabelas Envolvidas:**
        * `patrimonio`: `id`, `nome`, `quantidade`, `descricao`, `data_aquisicao`
    * **Query Base (PostgreSQL):**
        ```sql
        SELECT id, nome, quantidade, descricao, data_aquisicao FROM patrimonio ORDER BY nome ASC;
        ```
    * **Resposta (Exemplo):**
        ```json
        [
          {
            "id": 1,
            "nome": "Barraca Iglú 4 Pessoas",
            "quantidade": 5,
            "descricao": "Modelo Mor",
            "data_aquisicao": "2023-03-15"
          }
        ]
        ```

* **`POST /patrimonio`**
    * **Descrição:** Adiciona um novo item ao inventário do clube.
    * **Tabelas Envolvidas:**
        * `patrimonio`: `nome`, `quantidade`, `descricao`, `data_aquisicao`
    * **Query Base (PostgreSQL):**
        ```sql
        INSERT INTO patrimonio (nome, quantidade, descricao, data_aquisicao)
        VALUES (:nome, :quantidade, :descricao, :data_aquisicao)
        RETURNING id;
        ```
    * **Corpo da Requisição (Body):**
        ```json
        {
          "nome": "Lanterna de LED",
          "quantidade": 10,
          "descricao": "Modelo recarregável com bateria",
          "data_aquisicao": "2025-08-17"
        }
        ```

* **`PUT /patrimonio/{id}`**
    * **Descrição:** Atualiza as informações de um item existente no inventário.
    * **Tabelas Envolvidas:**
        * `patrimonio`: `nome`, `quantidade`, `descricao`
    * **Query Base (PostgreSQL):**
        ```sql
        UPDATE patrimonio
        SET nome = :nome, quantidade = :quantidade, descricao = :descricao
        WHERE id = :id;
        ```
    * **Corpo da Requisição (Body):**
        ```json
        {
          "nome": "Barraca Iglú para 4 Pessoas (Nova)",
          "quantidade": 6,
          "descricao": "Modelo Mor, revisada em 2025"
        }
        ```

* **`DELETE /patrimonio/{id}`**
    * **Descrição:** Remove um item do inventário.
    * **Tabelas Envolvidas:**
        * `patrimonio`
    * **Query Base (PostgreSQL):**
        ```sql
        DELETE FROM patrimonio WHERE id = :id;
        ```

## 2. Solicitação de Materiais (Visão da Unidade)

Endpoints para as unidades do clube solicitarem materiais para suas reuniões e atividades.

* **`POST /solicitacoes`**
    * **Descrição:** Cria uma nova solicitação de materiais para uma reunião específica. A API deve criar um registro na tabela `solicitacoes` para cada item do array.
    * **Tabelas Envolvidas:**
        * `solicitacoes`: `codigo_sgc`, `id_item`, `quantidade`, `data_solicitacao`, `status`, `reuniao_id`
    * **Query Base (PostgreSQL - executada em loop ou batch):**
        ```sql
        INSERT INTO solicitacoes (codigo_sgc, id_item, quantidade, data_solicitacao, status, reuniao_id)
        VALUES (:codigo_sgc_logado, :itemId, :quantidade, CURRENT_DATE, 'Pendente', :reuniaoId);
        ```
    * **Corpo da Requisição (Body):**
        ```json
        {
          "reuniaoId": 3,
          "itens": [
            { "itemId": 1, "quantidade": 4 },
            { "itemId": 2, "quantidade": 1 }
          ]
        }
        ```

* **`GET /solicitacoes/minhas`**
    * **Descrição:** Retorna o histórico de solicitações feitas pela unidade do usuário logado.
    * **Tabelas Envolvidas:**
        * `solicitacoes`: `id`, `status`, `motivo_reprovacao`, `quantidade`
        * `reunioes`: `nome`, `data`
        * `patrimonio`: `nome`
    * **Query Base (PostgreSQL):**
        ```sql
        SELECT
          s.id,
          r.nome AS reuniao,
          r.data,
          s.status,
          s.motivo_reprovacao AS motivoReprovacao,
          p.nome AS item_nome,
          s.quantidade
        FROM solicitacoes s
        JOIN reunioes r ON s.reuniao_id = r.id
        JOIN patrimonio p ON s.id_item = p.id
        WHERE s.codigo_sgc = :codigo_sgc_logado
        ORDER BY r.data DESC;
        ```
    * **Resposta (Exemplo):**
        ```json
        [
            {
                "id": 102,
                "reuniao": "Acampamento de Unidade",
                "data": "2025-03-15",
                "status": "reprovado",
                "motivoReprovacao": "Quantidade de barracas indisponível para a data.",
                "itens": [
                    { "nome": "Barraca Iglú 4 Pessoas", "quantidade": 4 },
                    { "nome": "Corda de Sisal 10mm", "quantidade": 1 }
                ]
            }
        ]
        ```

## 3. Gerenciamento de Solicitações (Visão da Diretoria)

Endpoints para a diretoria do clube aprovar, reprovar e gerenciar o fluxo de entrega e devolução dos materiais solicitados.

* **`GET /solicitacoes`**
    * **Descrição:** Retorna todas as solicitações de materiais de todas as unidades, agrupadas por reunião.
    * **Tabelas Envolvidas:**
        * `solicitacoes`: `id`, `status`, `quantidade`
        * `membros`: `codigo_sgc`
        * `unidades`: `nome`
        * `reunioes`: `id`, `nome`, `data`
        * `patrimonio`: `nome`
    * **Query Base (PostgreSQL):**
        ```sql
        SELECT
          s.id,
          s.status,
          s.quantidade,
          r.id AS reuniao_id,
          r.nome AS reuniao_nome,
          r.data AS reuniao_data,
          u.nome AS unidade,
          p.nome AS item_nome
        FROM solicitacoes s
        JOIN membros m ON s.codigo_sgc = m.codigo_sgc
        JOIN unidades u ON m.id_unidade = u.id
        JOIN reunioes r ON s.reuniao_id = r.id
        JOIN patrimonio p ON s.id_item = p.id
        ORDER BY r.data DESC, u.nome;
        ```
    * **Resposta (Exemplo - a API deve agrupar o resultado da query por reunião):**
        ```json
        [
          {
            "reuniao": {
              "id": 1,
              "nome": "Acampamento de Unidade",
              "data": "2025-03-15"
            },
            "solicitacoes": [
              {
                "id": 1,
                "unidade": "Jaguar",
                "status": "pendente",
                "itens": [{ "nome": "Barraca Iglú 4 Pessoas", "quantidade": 2 }]
              }
            ]
          }
        ]
        ```

* **`PUT /solicitacoes/{id}/status`**
    * **Descrição:** Atualiza o status de uma solicitação específica (Aprovar, Reprovar, Entregue, etc.).
    * **Tabelas Envolvidas:**
        * `solicitacoes`: `status`, `motivo_reprovacao`
    * **Query Base (PostgreSQL):**
        ```sql
        UPDATE solicitacoes
        SET status = :status, motivo_reprovacao = :motivoReprovacao
        WHERE id = :id;
        ```
    * **Corpo da Requisição (Body):**
        ```json
        {
          "status": "reprovado",
          "motivoReprovacao": "Item indisponível na data solicitada."
        }
        ```