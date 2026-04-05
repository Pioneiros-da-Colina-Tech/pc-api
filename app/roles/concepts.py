from enum import StrEnum


class Role(StrEnum):
    DIRETOR = "diretor"
    SECRETARIA = "secretaria"
    TESOURARIA = "tesouraria"
    EQUIPE_PONTUACAO = "equipe_pontuacao"
    CONSELHEIRO_UNIDADE = "conselheiro_unidade"
    ASSOCIADO_UNIDADE = "associado_unidade"
    PAI = "pai"
    MEMBRO = "membro"
    REGIONAL = "regional"
    DISTRITAL = "distrital"
    EXECUTIVA = "executiva"
    CHEFE_APOIO = "chefe_apoio"
    APOIO = "apoio"


class Screen(StrEnum):
    REUNIOES_NOVA_REUNIAO = "reunioes.nova_reuniao"
    REUNIOES_EDITAR = "reunioes.editar"
    REUNIOES_CHAMADA = "reunioes.chamada"
    SECRETARIA = "secretaria"
    UNIDADE = "unidade"
    UNIDADE_DASHBOARD = "unidade.dashboard"
    MEU_PAINEL = "meu_painel"
    TESOURARIA = "tesouraria"
    APOIO_REGIONAL_INFORMACOES = "apoio_regional.informacoes"
    APOIO_REGIONAL_GERENCIAR_POSTS = "apoio_regional.gerenciar_posts"
    APOIO_REGIONAL_CAIXA_ENTRADA = "apoio_regional.caixa_entrada"
    AVALIACAO_REGIONAL = "avaliacao_regional"
    PONTUACAO_RANKING = "pontuacao.ranking"
    PONTUACAO_LANCAMENTO = "pontuacao.lancamento"
    PATRIMONIO_GERENCIAR = "patrimonio.gerenciar"
    PATRIMONIO_SOLICITAR_MATERIAIS = "patrimonio.solicitar_materiais"
    PATRIMONIO_SOLICITACOES = "patrimonio.solicitacoes"
