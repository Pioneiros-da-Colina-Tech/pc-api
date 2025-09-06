# Documentação da API - Pontuação

Endpoints para exibir os rankings de desempenho das unidades e membros, e para permitir o lançamento de pontos bônus.

## Pré-requisito: Tabela de Bônus

Para gerenciar os pontos bônus, é necessária uma tabela adicional no banco de dados.

* **Tabela:** `pontuacao_bonus`
    * **Descrição:** Armazena os registros de pontos bônus aplicados a membros ou unidades.
    * **DDL (PostgreSQL):**
      ```sql
      CREATE TABLE public.pontuacao_bonus (
          id SERIAL PRIMARY KEY,
          tipo VARCHAR(10) NOT NULL, -- 'unidade' ou 'membro'
          id_referencia INT NOT NULL, -- id da unidade ou do membro
          pontos INT NOT NULL,
          descricao TEXT,
          data DATE NOT NULL DEFAULT CURRENT_DATE,
          CONSTRAINT tipo_check CHECK (tipo IN ('unidade', 'membro'))
      );
      ```

---

## 1. Ranking

Endpoints para buscar os dados de pontuação e exibir nos rankings. **Todos os endpoints de ranking agora aceitam os parâmetros `ano` e `semestre` para filtrar os resultados.**

* **`GET /ranking/unidades`**
    * **Descrição:** Retorna a pontuação total de cada unidade para o ranking geral, filtrada por ano e semestre.
    * **Tabelas Envolvidas:**
        * `unidades`: `id`, `nome`
        * `membros`: `id_unidade`, `codigo_sgc`
        * `chamadas`: `codigo_sgc`, `presenca`, `pontualidade`, `uniforme`, `modestia`
        * `reunioes`: `id`, `data`
        * `pontuacao_bonus`: `id_referencia`, `tipo`, `pontos`, `data`
    * **Query Base (PostgreSQL):**
        ```sql
        -- Esta query é conceitual. Ela une a soma das chamadas com a soma dos bônus.
        SELECT
            u.nome AS unidade,
            COALESCE(SUM(c.presenca + c.pontualidade + c.uniforme + c.modestia), 0) + COALESCE(b.bonus_pontos, 0) AS pontos
        FROM unidades u
        LEFT JOIN membros m ON u.id = m.id_unidade
        LEFT JOIN chamadas c ON m.codigo_sgc = c.codigo_sgc
        LEFT JOIN reunioes r ON c.reuniao_id = r.id
        LEFT JOIN (
            SELECT id_referencia, SUM(pontos) as bonus_pontos
            FROM pontuacao_bonus
            WHERE tipo = 'unidade' AND EXTRACT(YEAR FROM data) = :ano -- Filtro de ano
            GROUP BY id_referencia
        ) b ON u.id = b.id_referencia
        WHERE EXTRACT(YEAR FROM r.data) = :ano -- Filtro de ano
        GROUP BY u.nome, b.bonus_pontos
        ORDER BY pontos DESC;
        ```
    * **Resposta (Exemplo):**
        ```json
        [
          {
            "unidade": "Jaguar",
            "pontos": 250
          },
          {
            "unidade": "Gato do Mato",
            "pontos": 210
          }
        ]
        ```

* **`GET /ranking/unidades/categorias`**
    * **Descrição:** Retorna a pontuação de cada unidade, detalhada por categoria, filtrada por ano e semestre.
    * **Tabelas Envolvidas:**
        * `unidades`: `id`, `nome`
        * `membros`: `id_unidade`, `codigo_sgc`
        * `chamadas`: `codigo_sgc`, `presenca`, `pontualidade`, `uniforme`, `modestia`
        * `reunioes`: `id`, `data`
    * **Query Base (PostgreSQL):**
        ```sql
        SELECT
            u.nome AS unidade,
            SUM(c.presenca) AS presenca,
            SUM(c.pontualidade) AS pontualidade,
            SUM(c.uniforme) AS uniforme,
            SUM(c.modestia) AS modestia
        FROM unidades u
        JOIN membros m ON u.id = m.id_unidade
        JOIN chamadas c ON m.codigo_sgc = c.codigo_sgc
        JOIN reunioes r ON c.reuniao_id = r.id
        WHERE EXTRACT(YEAR FROM r.data) = :ano -- Filtro de ano
        GROUP BY u.nome;
        ```
    * **Resposta (Exemplo):**
        ```json
        {
          "presenca": [
            { "unidade": "Gato do Mato", "pontos": 19 },
            { "unidade": "Jaguar", "pontos": 18 }
          ],
          "pontualidade": [
            { "unidade": "Jaguar", "pontos": 20 },
            { "unidade": "Gato do Mato", "pontos": 18 }
          ]
        }
        ```

* **`GET /ranking/membros`**
    * **Descrição:** Retorna a pontuação detalhada de cada membro, filtrada por ano, semestre e, opcionalmente, por cargo.
    * **Tabelas Envolvidas:**
        * `membros`: `nome`, `cargo`, `codigo_sgc`
        * `unidades`: `nome`
        * `chamadas`: `presenca`, `pontualidade`, `uniforme`, `modestia`
        * `reunioes`: `data`
        * `pontuacao_bonus`: `id_referencia`, `tipo`, `pontos`, `data`
    * **Query Base (PostgreSQL):**
        ```sql
        SELECT
            m.nome,
            u.nome AS unidade,
            m.cargo,
            SUM(c.presenca) AS presenca,
            SUM(c.pontualidade) AS pontualidade,
            SUM(c.uniforme) AS uniforme,
            SUM(c.modestia) AS modestia,
            COALESCE(b.bonus_pontos, 0) AS bonus,
            (SUM(c.presenca + c.pontualidade + c.uniforme + c.modestia) + COALESCE(b.bonus_pontos, 0)) AS total
        FROM membros m
        JOIN unidades u ON m.id_unidade = u.id
        LEFT JOIN chamadas c ON m.codigo_sgc = c.codigo_sgc
        LEFT JOIN reunioes r ON c.reuniao_id = r.id
        LEFT JOIN (
            SELECT id_referencia, SUM(pontos) as bonus_pontos
            FROM pontuacao_bonus
            WHERE tipo = 'membro' AND EXTRACT(YEAR FROM data) = :ano -- Filtro de ano
            GROUP BY id_referencia
        ) b ON m.id = b.id_referencia
        WHERE EXTRACT(YEAR FROM r.data) = :ano -- Filtro de ano
        AND (:cargo = 'todos' OR m.cargo = :cargo) -- Filtro de cargo
        GROUP BY m.nome, u.nome, m.cargo, b.bonus_pontos
        ORDER BY total DESC;
        ```
    * **Resposta (Exemplo):**
        ```json
        [
          {
            "nome": "João Silva",
            "unidade": "Jaguar",
            "cargo": "Desbravador",
            "presenca": 10,
            "pontualidade": 10,
            "uniforme": 5,
            "modestia": 10,
            "bonus": 5,
            "total": 40
          }
        ]
        ```

## 2. Bônus

Endpoint para adicionar pontos de bônus.

* **`POST /pontuacao/bonus`**
    * **Descrição:** Lança um ponto bônus para uma unidade ou um membro específico.
    * **Tabelas Envolvidas:**
        * `pontuacao_bonus`: `tipo`, `id_referencia`, `pontos`, `descricao`
    * **Query Base (PostgreSQL):**
        ```sql
        INSERT INTO pontuacao_bonus (tipo, id_referencia, pontos, descricao)
        VALUES (:tipo, :id, :pontos, :descricao);
        ```
    * **Corpo da Requisição (Body):**
        ```json
        {
          "tipo": "unidade",
          "id": 1,
          "pontos": 50,
          "descricao": "Decoração da sala da unidade."
        }
        ```