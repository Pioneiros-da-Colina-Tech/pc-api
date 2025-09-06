# Documentação da API - Tesouraria

Endpoints para o gerenciamento financeiro completo do clube, incluindo fluxo de caixa, mensalidades, eventos e relatórios.

## 1. Visão Geral

* **`GET /tesouraria/visao-geral`**
    * **Descrição:** Retorna um resumo financeiro consolidado do mês atual, ideal para os cards de destaque.
    * **Tabelas Envolvidas:**
        * `caixa`: `valor`, `tipo`, `data`
    * **Query Base (PostgreSQL):**
        ```sql
        -- Query para Receitas do Mês
        SELECT COALESCE(SUM(valor), 0) AS receitasMes
        FROM caixa
        WHERE tipo = 'entrada' AND EXTRACT(YEAR FROM data) = EXTRACT(YEAR FROM CURRENT_DATE) AND EXTRACT(MONTH FROM data) = EXTRACT(MONTH FROM CURRENT_DATE);

        -- Query para Despesas do Mês
        SELECT COALESCE(SUM(valor), 0) AS despesasMes
        FROM caixa
        WHERE tipo = 'saida' AND EXTRACT(YEAR FROM data) = EXTRACT(YEAR FROM CURRENT_DATE) AND EXTRACT(MONTH FROM data) = EXTRACT(MONTH FROM CURRENT_DATE);
        ```
    * **Resposta (Exemplo):**
        ```json
        {
          "receitasMes": 2450.00,
          "despesasMes": 1850.00,
          "saldoAtual": 600.00,
          "orcamentoUtilizadoPercentual": 75
        }
        ```

## 2. Fluxo de Caixa

* **`GET /caixa/lancamentos`**
    * **Descrição:** Retorna uma lista de todos os lançamentos do fluxo de caixa, podendo ser filtrado por período.
    * **Tabelas Envolvidas:** `caixa`
    * **Query Base (PostgreSQL):**
        ```sql
        SELECT id, tipo, descricao, valor, data
        FROM caixa
        WHERE data BETWEEN :data_inicio AND :data_fim
        ORDER BY data DESC;
        ```
    * **Query Params (Opcionais):** `?data_inicio=YYYY-MM-DD&data_fim=YYYY-MM-DD`

* **`POST /caixa/lancamentos`**
    * **Descrição:** Registra um novo lançamento (entrada ou saída) no caixa.
    * **Tabelas Envolvidas:** `caixa`
    * **Query Base (PostgreSQL):**
        ```sql
        INSERT INTO caixa (tipo, descricao, valor, data)
        VALUES (:tipo, :descricao, :valor, :data);
        ```
    * **Corpo da Requisição (Body):**
        ```json
        {
          "tipo": "saida",
          "descricao": "Compra de material de limpeza",
          "valor": 80.00,
          "data": "2025-01-16"
        }
        ```

## 3. Mensalidades

* **`GET /mensalidades`**
    * **Descrição:** Retorna a lista de todos os meses de mensalidade já criados.
    * **Tabelas Envolvidas:** `mensalidades`
    * **Query Base (PostgreSQL):**
        ```sql
        SELECT id, mes, ano, valor FROM mensalidades ORDER BY ano DESC, mes DESC;
        ```

* **`POST /mensalidades`**
    * **Descrição:** Cria um novo mês de mensalidade.
    * **Tabelas Envolvidas:** `mensalidades`
    * **Query Base (PostgreSQL):**
        ```sql
        INSERT INTO mensalidades (mes, ano, valor) VALUES (:mes, :ano, :valor);
        ```
    * **Corpo da Requisição (Body):**
        ```json
        {
          "mes": 3,
          "ano": 2025,
          "valor": 50.00
        }
        ```

* **`PUT /mensalidades/{id}`**
    * **Descrição:** Edita o valor de uma mensalidade.
    * **Tabelas Envolvidas:** `mensalidades`
    * **Query Base (PostgreSQL):**
        ```sql
        UPDATE mensalidades SET valor = :valor WHERE id = :id;
        ```
    * **Corpo da Requisição (Body):**
        ```json
        {
          "valor": 55.00
        }
        ```

* **`GET /mensalidades/{id}/pagamentos`**
    * **Descrição:** Retorna a lista de todos os membros e o status de pagamento da mensalidade do mês selecionado.
    * **Tabelas Envolvidas:** `membros`, `user_mensalidades`
    * **Query Base (PostgreSQL):**
        ```sql
        SELECT
            m.codigo_sgc,
            m.nome,
            um.status
        FROM membros m
        LEFT JOIN user_mensalidades um ON m.codigo_sgc = um.codigo_sgc AND um.id_mensalidade = :id_mensalidade;
        ```

* **`PUT /mensalidades/{id}/pagamentos`**
    * **Descrição:** Atualiza o status de pagamento de um membro para uma mensalidade.
    * **Tabelas Envolvidas:** `user_mensalidades`
    * **Query Base (PostgreSQL - UPSERT):**
        ```sql
        INSERT INTO user_mensalidades (id_mensalidade, codigo_sgc, status)
        VALUES (:id_mensalidade, :codigo_sgc, :status)
        ON CONFLICT (id_mensalidade, codigo_sgc)
        DO UPDATE SET status = EXCLUDED.status;
        ```
    * **Corpo da Requisição (Body):**
        ```json
        {
          "codigo_sgc": "67890",
          "status": "pago"
        }
        ```

## 4. Eventos

* **`GET /eventos`**
    * **Descrição:** Retorna a lista de todos os eventos criados.
    * **Tabelas Envolvidas:** `evento`
    * **Query Base (PostgreSQL):**
        ```sql
        SELECT id, nome, valor FROM evento ORDER BY nome ASC;
        ```

* **`POST /eventos`**
    * **Descrição:** Cria um novo evento.
    * **Tabelas Envolvidas:** `evento`
    * **Query Base (PostgreSQL):**
        ```sql
        INSERT INTO evento (nome, valor) VALUES (:nome, :valor);
        ```
    * **Corpo da Requisição (Body):**
        ```json
        {
          "nome": "Caminhada Ecológica",
          "valor": 25.00
        }
        ```

* **`PUT /eventos/{id}`**
    * **Descrição:** Atualiza os detalhes de um evento existente.
    * **Tabelas Envolvidas:** `evento`
    * **Query Base (PostgreSQL):**
        ```sql
        UPDATE evento SET nome = :nome, valor = :valor WHERE id = :id;
        ```
    * **Corpo da Requisição (Body):**
        ```json
        {
          "nome": "Acampamento de Verão 2025",
          "valor": 160.00
        }
        ```

* **`GET /eventos/{id}/pagamentos`**
    * **Descrição:** Retorna a lista de membros inscritos em um evento e o status de pagamento de cada um.
    * **Tabelas Envolvidas:** `membros`, `inscricao_eventos`
    * **Query Base (PostgreSQL):**
        ```sql
        SELECT
            m.codigo_sgc,
            m.nome,
            ie.status
        FROM membros m
        JOIN inscricao_eventos ie ON m.codigo_sgc = ie.codigo_sgc
        WHERE ie.id_evento = :id_evento;
        ```

* **`PUT /eventos/{id}/pagamentos`**
    * **Descrição:** Atualiza o status de pagamento de um membro para um evento.
    * **Tabelas Envolvidas:** `inscricao_eventos`
    * **Query Base (PostgreSQL):**
        ```sql
        UPDATE inscricao_eventos SET status = :status WHERE id_evento = :id_evento AND codigo_sgc = :codigo_sgc;
        ```
    * **Corpo da Requisição (Body):**
        ```json
        {
          "codigo_sgc": "67890",
          "status": "pago"
        }
        ```

* **`POST /eventos/{id}/inscricoes`**
    * **Descrição:** Inscreve um membro em um evento.
    * **Tabelas Envolvidas:** `inscricao_eventos`
    * **Query Base (PostgreSQL):**
        ```sql
        INSERT INTO inscricao_eventos (id_evento, codigo_sgc, status)
        VALUES (:id_evento, :codigo_sgc, 'Pendente');
        ```
    * **Corpo da Requisição (Body):**
        ```json
        {
          "codigo_sgc": "11122"
        }
        ```

## 5. Relatórios

* **`GET /relatorios/mensal`**
    * **Descrição:** Retorna os dados para o relatório financeiro de um mês específico.
    * **Tabelas Envolvidas:** `caixa`
    * **Query Base (PostgreSQL):**
        ```sql
        SELECT
            COALESCE(SUM(CASE WHEN tipo = 'entrada' THEN valor ELSE 0 END), 0) AS totalEntradas,
            COALESCE(SUM(CASE WHEN tipo = 'saida' THEN valor ELSE 0 END), 0) AS totalSaidas
        FROM caixa
        WHERE EXTRACT(YEAR FROM data) = :ano AND EXTRACT(MONTH FROM data) = :mes;
        ```
    * **Query Params:** `?ano=2025&mes=1`

* **`GET /relatorios/eventos/{id}`**
    * **Descrição:** Retorna os dados financeiros e de inscrições para um evento específico.
    * **Tabelas Envolvidas:** `caixa`, `inscricao_eventos`
    * **Query Base (PostgreSQL):**
        ```sql
        -- Entradas/Saídas do Caixa
        SELECT tipo, SUM(valor) FROM caixa WHERE id_evento = :id_evento GROUP BY tipo;
        -- Status das Inscrições
        SELECT status, COUNT(*) FROM inscricao_eventos WHERE id_evento = :id_evento GROUP BY status;
        ```