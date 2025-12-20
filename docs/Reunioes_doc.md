# Documentação da API - Reuniões

Endpoints para criar, editar e apagar o cadastro de reuniões. E para a realização das chamadas de cada desbravador (por unidade) para cada reunião criada.

## 1. Reuniões

Endpoints para criar, editar e apagar alguma reunião.

* **`POST /reunioes/nova`**
  * **Descrição**: Cadastra uma nova reunião, passando o nome e a data em que a reunião vai acontecer.
  * **Uso**: Botão "Cadastrar" na aba de Reuniões > Nova
  * **Corpo da Requisição (Body):**
  
  ```json
    {
        "nome": "Reunião Normal",
        "data_reuniao": "01/01/2025 09:00:00"
    }
  ```

* **`GET /reunioes`**
  * **Descrição:** Retorna todas as reuniões cadastradas.
  * **Query Params:** `?ano=2025`
  * **Uso**: Alimenta a aba Reuniões > Editar quando o dropdown "Escolha uma Reunião" é selecionado.
  * **Resposta (Exemplo):**

  ```json
    [
        {
            "id_meeting": "9021348a8sd09_03284s09da8",
            "nome": "Reunião Normal",
            "data_reuniao": "01/01/2025 09:00:00"
        },
        {
            "id_meeting": "9021ads234_0328234234",
            "nome": "Reunião de Sábado",
            "data_reuniao": "02/01/2025 09:00:00"
        }
    ]
  ```

* **`PUT /reunioes/{id_meeting}`**
  * **Descrição:** Atualiza os dados de uma reunião cadastrada.
  * **Uso:** Botão de ação "Salvar edição" na aba Reuniões > Editar.
  * **Corpo da Requisição (Body):**

  ```json
    {
        "nome": "Reunião de Sábado Especial",
        "data_reuniao": "02/01/2025 15:30:00"
    }
  ```

* **`DELETE /reunioes/{id_meeting}`**
  * **Descrição**: Remove uma reunião.
  * **Uso:** Botão de ação "Remover reunião" na aba Reuniões > Editar
  * **Exemplo de resposta**:
    * **`status: 404`**
  
  ```json
    {        
        "message": "Reunião não existe"
    }
  ```

## 2. Chamada

Endpoints para registrar a chamada de cada desbravador por unidade e por reunião

* **`GET /unidade`**
  * **Descrição:** Retorna todas as unidades ativas do clube
  * **Uso:** Dropdown "Selecionar a unidade" na aba Reuniões > Chamada
  * **Resposta (exemplo):**

  ```json
  [
    {
        "id_unidade": "02934dl12kfj_lkani0281f0993",
        "nome": "Guepardo Real"
    },
    {
        "id_unidade": "0a09asi9sudfhn_lkakjasbh9083",
        "nome": "Jaguar"
    }
  ]
  ```

* **mesmo endpoint de get reunião utilizado anteriormente**

* **`GET /unidade?id=<ID>/membros`**
  * **Descrição**: Retorna todos os membros de uma unidade
  * **Query Params**: `?id=<ID>` é o ID da unidade
  * **Uso**: Na aba Reuniões > Chamada, após selecionar a unidade e a reunião é listado todos os membros dessa unidade.
  * **Resposta (exemplo):**

  ```json
    [
        {
            "id": "ka234kjasn_09432lknas",
            "codigo_sgc": "1234",
            "nome": "João Silva",
            "id_unidade": "0a09asi9sudfhn_lkakjasbh9083",
            "cargo": "Desbravador"
        },
        {
            "id": "ka2345jasn_asdasd324s",
            "codigo_sgc": "67890",
            "nome": "Pedro Costa",
            "id_unidade": "0a09asi9sudfhn_lkakjasbh9083",
            "cargo": "Desbravador"
        }
    ]
  ```

* **`POST /chamadas/reunioes?id=<id>/unidade?id=<id>`**
  * **Descrição:** Registra a chamada passando uma lista de desbravadores com base na reunião e a unidade.
  * **Uso:** Botão de ação "Salvar chamada" na aba Reuniões > Chamada
  * **Corpo da Requisição (body):**

  ```json
    [
        {
            "codigo_sgc": "1234",
            "presenca": true,
            "pontualidade": <10 | 5 | 0>,
            "uniforme": <10 | 5 | 0>,
            "modestia": <10 | 5 | 0>
        },
        {
            "codigo_sgc": "67890",
            "presenca": false,
            "pontualidade": 0,
            "uniforme": 0,
            "modestia": 0>
        }
    ]
  ```
