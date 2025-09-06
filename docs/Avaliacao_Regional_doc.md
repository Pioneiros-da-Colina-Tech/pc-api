# Documentação da API - Avaliação Regional

Endpoints destinados à liderança regional para avaliar e aprovar o progresso dos membros em classes e especialidades, garantindo a conformidade com os padrões estabelecidos.

## 1. Avaliação de Classes

Endpoints para visualizar e avaliar os requisitos de classes enviados pelos clubes.

* **`GET /avaliacoes/classes?unidade_id=<ID_UNIDADE>`**
    * **Descrição:** Retorna todos os requisitos de classe que estão aguardando avaliação ou que foram marcados para refazer, para uma unidade específica.
    * **Tabelas Envolvidas:**
        * `avaliacao_requisitos`: `id`, `codigo_sgc_membro`, `id_requisito`, `status`
        * `membros`: `codigo_sgc`, `nome`, `id_unidade`
        * `requisitos_classes`: `id`, `texto`
    * **Query Base (PostgreSQL):**
        ```sql
        SELECT
          ar.id AS id_avaliacao,
          ar.status,
          m.codigo_sgc,
          m.nome,
          rc.id AS id_requisito,
          rc.texto
        FROM avaliacao_requisitos ar
        JOIN membros m ON ar.codigo_sgc_membro = m.codigo_sgc
        JOIN requisitos_classes rc ON ar.id_requisito = rc.id
        WHERE m.id_unidade = :unidade_id AND ar.status IN ('Avaliação', 'Refazer');
        ```
    * **Resposta (Exemplo):**
        ```json
        [
          {
            "membro": {
              "codigo_sgc": "12345",
              "nome": "João Silva"
            },
            "requisitos": [
              {
                "id_avaliacao": 12,
                "id_requisito": 102,
                "texto": "Memorizar Voto e Lei.",
                "status": "Avaliação"
              }
            ]
          }
        ]
        ```

* **`PUT /avaliacoes/requisitos/{id_avaliacao}`**
    * **Descrição:** Atualiza o status de um requisito específico para um membro (Aprovar/Refazer).
    * **Tabelas Envolvidas:**
        * `avaliacao_requisitos`: `status`, `data_aprovacao`
    * **Query Base (PostgreSQL):**
        ```sql
        UPDATE avaliacao_requisitos
        SET
          status = :novo_status,
          data_aprovacao = CASE WHEN :novo_status = 'Aprovado' THEN CURRENT_DATE ELSE NULL END
        WHERE id = :id_avaliacao;
        ```
    * **Corpo da Requisição (Body):**
        ```json
        {
          "status": "Aprovado"
        }
        ```

## 2. Avaliação de Especialidades

Endpoints para visualizar e avaliar as especialidades concluídas pelos membros.

* **`GET /avaliacoes/especialidades?unidade_id=<ID_UNIDADE>`**
    * **Descrição:** Retorna uma lista de todas as especialidades que estão aguardando avaliação ou que foram marcadas para refazer, para uma unidade específica.
    * **Tabelas Envolvidas:**
        * `avaliacao_especialidade`: `id`, `codigo_sgc`, `codigo_especialidade`, `status`
        * `membros`: `codigo_sgc`, `nome`, `id_unidade`
        * `especialidades`: `codigo`, `nome`
    * **Query Base (PostgreSQL):**
        ```sql
        SELECT
          ae.id AS id_avaliacao,
          ae.status,
          m.codigo_sgc,
          m.nome,
          e.codigo AS codigo_especialidade,
          e.nome AS nome_especialidade
        FROM avaliacao_especialidade ae
        JOIN membros m ON ae.codigo_sgc = m.codigo_sgc
        JOIN especialidades e ON ae.codigo_especialidade = e.codigo
        WHERE m.id_unidade = :unidade_id AND ae.status IN ('Avaliação', 'Refazer');
        ```
    * **Resposta (Exemplo):**
        ```json
        [
          {
            "membro": {
              "codigo_sgc": "54321",
              "nome": "Maria Santos"
            },
            "especialidades": [
              {
                "id_avaliacao": 25,
                "codigo_especialidade": "PS-001",
                "nome": "Primeiros Socorros",
                "status": "Refazer"
              }
            ]
          }
        ]
        ```

* **`PUT /avaliacoes/especialidades/{id_avaliacao}`**
    * **Descrição:** Atualiza o status de uma especialidade para um membro (Aprovar/Refazer).
    * **Tabelas Envolvidas:**
        * `avaliacao_especialidade`: `status`, `aproved_at`
    * **Query Base (PostgreSQL):**
        ```sql
        UPDATE avaliacao_especialidade
        SET
          status = :novo_status,
          aproved_at = CASE WHEN :novo_status = 'Aprovado' THEN CURRENT_DATE ELSE NULL END
        WHERE id = :id_avaliacao;
        ```
    * **Corpo da Requisição (Body):**
        ```json
        {
          "status": "Aprovado"
        }
        ```

## 3. Sentinelas da Colina

Endpoints para a aprovação final de membros que completaram todos os requisitos, tornando-os "Sentinelas".

* **`GET /sentinelas?tipo=<TIPO>&codigo=<CODIGO_CLASSE/ESPECIALIDADE>`**
    * **Descrição:** Retorna uma lista de membros aguardando aprovação final para uma classe ou especialidade.
    * **Tabelas Envolvidas:**
        * `sentinelas_classe` ou `sentinelas_especialidade`
        * `membros`
    * **Query Base (PostgreSQL - para `tipo=classe`):**
        ```sql
        SELECT
          sc.codigo_sgc,
          m.nome,
          sc.status
        FROM sentinelas_classe sc
        JOIN membros m ON sc.codigo_sgc = m.codigo_sgc
        WHERE sc.codigo_classe = :codigo AND sc.status IN ('Avaliação', 'Refazer');
        ```
    * **Resposta (Exemplo):**
        ```json
        [
          {
            "codigo_sgc": "12345",
            "nome": "João Silva",
            "status": "Avaliação"
          }
        ]
        ```

* **`PUT /sentinelas`**
    * **Descrição:** Realiza a aprovação final (ou marca para refazer) de um membro em uma classe ou especialidade.
    * **Tabelas Envolvidas:**
        * `sentinelas_classe` ou `sentinelas_especialidade`
    * **Query Base (PostgreSQL - para `tipo=classe`):**
        ```sql
        UPDATE sentinelas_classe
        SET
          status = :novo_status,
          aproved_at = CASE WHEN :novo_status = 'Aprovado' THEN CURRENT_DATE ELSE NULL END
        WHERE codigo_sgc = :codigo_sgc AND codigo_classe = :codigo;
        ```
    * **Corpo da Requisição (Body):**
        ```json
        {
          "codigo_sgc": "12345",
          "tipo": "classe",
          "codigo": "AM-001",
          "status": "Aprovado"
        }
        ```