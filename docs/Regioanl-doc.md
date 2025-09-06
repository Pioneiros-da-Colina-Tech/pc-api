# Documentação da API - Apoio Regional

Endpoints para a comunicação e gestão de recursos entre a coordenação regional e a diretoria dos clubes.

## Pré-requisitos: Tabelas do Banco de Dados

Para o funcionamento desta seção, são necessárias as seguintes tabelas:

* **`regional_posts`**
    * **Descrição:** Armazena os posts e comunicados criados pela regional.
    * **DDL (PostgreSQL):**
      ```sql
      CREATE TABLE public.regional_posts (
          id SERIAL PRIMARY KEY,
          titulo TEXT NOT NULL,
          conteudo TEXT NOT NULL,
          autor TEXT,
          data_publicacao DATE NOT NULL DEFAULT CURRENT_DATE
      );
      ```

* **`regional_avaliacoes_datas`**
    * **Descrição:** Armazena as datas importantes de avaliações.
    * **DDL (PostgreSQL):**
      ```sql
      CREATE TABLE public.regional_avaliacoes_datas (
          id SERIAL PRIMARY KEY,
          nome TEXT NOT NULL,
          data DATE NOT NULL
      );
      ```
* **`regional_arquivos`**
    * **Descrição:** Armazena metadados de arquivos e manuais para download.
    * **DDL (PostgreSQL):**
      ```sql
      CREATE TABLE public.regional_arquivos (
          id SERIAL PRIMARY KEY,
          nome TEXT NOT NULL,
          tipo VARCHAR(10),
          tamanho VARCHAR(10),
          url TEXT NOT NULL
      );
      ```

* **`mensagens_regional`**
    * **Descrição:** Armazena a troca de mensagens entre o clube e a regional.
    * **DDL (PostgreSQL):**
      ```sql
      CREATE TABLE public.mensagens_regional (
          id SERIAL PRIMARY KEY,
          codigo_sgc_remetente TEXT NOT NULL REFERENCES public.membros(codigo_sgc),
          assunto TEXT NOT NULL,
          mensagem TEXT NOT NULL,
          data_envio TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
          resposta TEXT,
          autor_resposta TEXT,
          data_resposta TIMESTAMP WITH TIME ZONE
      );
      ```

---

## 1. Visão do Clube (Informações e Recursos)

Endpoints para os membros da diretoria do clube visualizarem comunicados, datas e arquivos, além de enviarem mensagens para a regional.

* **`GET /regional/posts`**
    * **Descrição:** Retorna a lista de todos os posts e comunicados publicados pela regional.
    * **Tabelas Envolvidas:** `regional_posts`
    * **Query Base (PostgreSQL):**
      ```sql
      SELECT id, titulo, autor, data_publicacao, conteudo FROM regional_posts ORDER BY data_publicacao DESC;
      ```
    * **Resposta (Exemplo):**
        ```json
        [
          {
            "id": 1,
            "titulo": "Ajustes no Calendário de Eventos",
            "autor": "Pastor Regional",
            "data": "2025-08-10",
            "conteudo": "Atenção, diretoria! O Camporee Regional foi adiantado em uma semana."
          }
        ]
        ```

* **`GET /regional/avaliacoes`**
    * **Descrição:** Retorna a lista das próximas datas de avaliação definidas pela regional.
    * **Tabelas Envolvidas:** `regional_avaliacoes_datas`
    * **Query Base (PostgreSQL):**
      ```sql
      SELECT id, nome, data FROM regional_avaliacoes_datas WHERE data >= CURRENT_DATE ORDER BY data ASC;
      ```
    * **Resposta (Exemplo):**
        ```json
        [
          {
            "id": 1,
            "nome": "Avaliação de Classes Regulares",
            "data": "2025-09-15"
          }
        ]
        ```

* **`GET /regional/arquivos`**
    * **Descrição:** Retorna a lista de arquivos e manuais disponíveis para download.
    * **Tabelas Envolvidas:** `regional_arquivos`
    * **Query Base (PostgreSQL):**
      ```sql
      SELECT id, nome, tipo, tamanho, url FROM regional_arquivos ORDER BY nome ASC;
      ```
    * **Resposta (Exemplo):**
        ```json
        [
          {
            "id": 1,
            "nome": "Regulamento de Uniformes 2025",
            "tipo": "PDF",
            "tamanho": "1.8MB",
            "url": "/path/to/downloadable/file.pdf"
          }
        ]
        ```

* **`POST /regional/mensagens`**
    * **Descrição:** Envia uma nova mensagem da diretoria do clube para a regional.
    * **Tabelas Envolvidas:** `mensagens_regional`
    * **Query Base (PostgreSQL):**
        ```sql
        INSERT INTO mensagens_regional (codigo_sgc_remetente, assunto, mensagem)
        VALUES (:codigo_sgc_logado, :assunto, :mensagem);
        ```
    * **Corpo da Requisição (Body):**
        ```json
        {
          "assunto": "Dúvida sobre o Camporee",
          "mensagem": "Gostaríamos de confirmar se o local permanece o mesmo."
        }
        ```

* **`GET /regional/mensagens/enviadas`**
    * **Descrição:** Retorna o histórico de mensagens que o clube enviou para a regional, incluindo as respostas.
    * **Tabelas Envolvidas:** `mensagens_regional`
    * **Query Base (PostgreSQL):**
        ```sql
        SELECT id, assunto, mensagem, data_envio, resposta, autor_resposta, data_resposta
        FROM mensagens_regional
        WHERE codigo_sgc_remetente = :codigo_sgc_logado
        ORDER BY data_envio DESC;
        ```
    * **Resposta (Exemplo):**
        ```json
        [
          {
            "id": 1,
            "assunto": "Dúvida sobre o Camporee",
            "mensagem": "Gostaríamos de confirmar se o local permanece o mesmo.",
            "dataEnvio": "2025-08-11T10:00:00Z",
            "resposta": {
              "autorResposta": "Pastor Regional",
              "dataResposta": "2025-08-12T09:30:00Z",
              "conteudo": "Sim, o local está confirmado! Abraços."
            }
          }
        ]
        ```

## 2. Visão da Regional (Gerenciamento)

Endpoints para a equipe regional criar, editar e gerenciar o conteúdo que será exibido para os clubes.

* **`POST /regional/gerenciar/posts`**
    * **Descrição:** Cria um novo post ou comunicado para os clubes.
    * **Tabelas Envolvidas:** `regional_posts`
    * **Query Base (PostgreSQL):**
        ```sql
        INSERT INTO regional_posts (titulo, conteudo, autor) VALUES (:titulo, :conteudo, :autor_logado);
        ```
    * **Corpo da Requisição (Body):**
        ```json
        {
          "titulo": "Novo Regulamento de Uniformes",
          "conteudo": "O novo manual de uniformes já está disponível para download."
        }
        ```

* **`PUT /regional/gerenciar/posts/{id}`**
    * **Descrição:** Atualiza o título ou conteúdo de um post existente.
    * **Tabelas Envolvidas:** `regional_posts`
    * **Query Base (PostgreSQL):**
        ```sql
        UPDATE regional_posts SET titulo = :titulo, conteudo = :conteudo WHERE id = :id;
        ```
    * **Corpo da Requisição (Body):**
        ```json
        {
          "titulo": "ATUALIZADO: Novo Regulamento de Uniformes",
          "conteudo": "A implementação é imediata a partir de hoje."
        }
        ```

* **`POST /regional/gerenciar/avaliacoes`**
    * **Descrição:** Adiciona uma nova data de avaliação ao calendário.
    * **Tabelas Envolvidas:** `regional_avaliacoes_datas`
    * **Query Base (PostgreSQL):**
        ```sql
        INSERT INTO regional_avaliacoes_datas (nome, data) VALUES (:nome, :data);
        ```
    * **Corpo da Requisição (Body):**
        ```json
        {
          "nome": "Avaliação de Especialidades (Artes Manuais)",
          "data": "2025-09-22"
        }
        ```

* **`DELETE /regional/gerenciar/avaliacoes/{id}`**
    * **Descrição:** Remove uma data de avaliação.
    * **Tabelas Envolvidas:** `regional_avaliacoes_datas`
    * **Query Base (PostgreSQL):**
        ```sql
        DELETE FROM regional_avaliacoes_datas WHERE id = :id;
        ```

* **`GET /regional/gerenciar/mensagens`**
    * **Descrição:** Retorna todas as mensagens recebidas de todos os clubes.
    * **Tabelas Envolvidas:** `mensagens_regional`, `membros`, `unidades`
    * **Query Base (PostgreSQL):**
        ```sql
        SELECT
          msg.id,
          msg.assunto,
          msg.mensagem,
          msg.data_envio,
          m.nome AS autor_nome,
          u.nome AS autor_unidade
        FROM mensagens_regional msg
        JOIN membros m ON msg.codigo_sgc_remetente = m.codigo_sgc
        LEFT JOIN unidades u ON m.id_unidade = u.id
        WHERE msg.resposta IS NULL
        ORDER BY msg.data_envio ASC;
        ```
    * **Resposta (Exemplo):**
        ```json
        [
          {
            "id": 1,
            "assunto": "Dúvida sobre o Camporee",
            "autor": "Maria Santos (Diretora Jaguar)",
            "data": "2025-08-11T10:00:00Z",
            "mensagem": "Olá, Pastor! Gostaríamos de confirmar se o local do Camporee permanece o mesmo."
          }
        ]
        ```

* **`POST /regional/gerenciar/mensagens/{id}/responder`**
    * **Descrição:** Envia uma resposta para uma mensagem recebida de um clube.
    * **Tabelas Envolvidas:** `mensagens_regional`
    * **Query Base (PostgreSQL):**
        ```sql
        UPDATE mensagens_regional
        SET resposta = :resposta, autor_resposta = :autor_logado, data_resposta = CURRENT_TIMESTAMP
        WHERE id = :id;
        ```
    * **Corpo da Requisição (Body):**
        ```json
        {
          "resposta": "Sim, o local está confirmado! Abraços."
        }
        ```