-- =============================================================================
-- Seed: roles, screens and role_screen permissions
-- Run after all migrations have been applied.
-- Safe to re-run: uses INSERT ... ON CONFLICT DO NOTHING
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Roles
-- -----------------------------------------------------------------------------
INSERT INTO role (id, label) VALUES
    ('diretor',            'Diretor'),
    ('secretaria',         'Secretaria'),
    ('tesouraria',         'Tesouraria'),
    ('equipe_pontuacao',   'Equipe de Pontuação'),
    ('conselheiro_unidade','Conselheiro da Unidade'),
    ('associado_unidade',  'Associado da Unidade'),
    ('pai',                'Pai'),
    ('membro',             'Membro'),
    ('regional',           'Regional'),
    ('distrital',          'Distrital'),
    ('executiva',          'Executiva'),
    ('chefe_apoio',        'Chefe de Apoio'),
    ('apoio',              'Apoio')
ON CONFLICT (id) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 2. Screens
-- -----------------------------------------------------------------------------
INSERT INTO screen (id, label) VALUES
    ('reunioes.nova_reuniao',           'Reuniões - Nova Reunião'),
    ('reunioes.editar',                 'Reuniões - Editar'),
    ('reunioes.chamada',                'Reuniões - Chamada'),
    ('secretaria',                      'Secretaria'),
    ('unidade',                         'Unidade'),
    ('unidade.dashboard',               'Dashboard de Unidade'),
    ('meu_painel',                      'Meu Painel'),
    ('tesouraria',                      'Tesouraria'),
    ('apoio_regional.informacoes',      'Apoio Regional - Informações e Recursos'),
    ('apoio_regional.gerenciar_posts',  'Apoio Regional - Gerenciar Posts'),
    ('apoio_regional.caixa_entrada',    'Apoio Regional - Caixa de Entrada'),
    ('avaliacao_regional',              'Avaliação Regional'),
    ('pontuacao.ranking',               'Pontuação - Ranking'),
    ('pontuacao.lancamento',            'Pontuação - Lançar Bônus'),
    ('patrimonio.gerenciar',            'Patrimônio - Gerenciar'),
    ('patrimonio.solicitar_materiais',  'Patrimônio - Solicitar Materiais'),
    ('patrimonio.solicitacoes',         'Patrimônio - Solicitações')
ON CONFLICT (id) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 3. Role → Screen mappings
-- -----------------------------------------------------------------------------

-- reunioes.nova_reuniao: Diretor, Secretaria, Tesouraria
INSERT INTO role_screen (role_id, screen_id) VALUES
    ('diretor',    'reunioes.nova_reuniao'),
    ('secretaria', 'reunioes.nova_reuniao'),
    ('tesouraria', 'reunioes.nova_reuniao')
ON CONFLICT DO NOTHING;

-- reunioes.editar: Diretor, Secretaria, Tesouraria
INSERT INTO role_screen (role_id, screen_id) VALUES
    ('diretor',    'reunioes.editar'),
    ('secretaria', 'reunioes.editar'),
    ('tesouraria', 'reunioes.editar')
ON CONFLICT DO NOTHING;

-- reunioes.chamada: Diretor, Secretaria, Tesouraria, Equipe de Pontuação
INSERT INTO role_screen (role_id, screen_id) VALUES
    ('diretor',          'reunioes.chamada'),
    ('secretaria',       'reunioes.chamada'),
    ('tesouraria',       'reunioes.chamada'),
    ('equipe_pontuacao', 'reunioes.chamada')
ON CONFLICT DO NOTHING;

-- secretaria: Diretor, Secretaria, Tesouraria
INSERT INTO role_screen (role_id, screen_id) VALUES
    ('diretor',    'secretaria'),
    ('secretaria', 'secretaria'),
    ('tesouraria', 'secretaria')
ON CONFLICT DO NOTHING;

-- unidade: Conselheiro da Unidade, Associado da Unidade, Diretor (todas)
INSERT INTO role_screen (role_id, screen_id) VALUES
    ('conselheiro_unidade', 'unidade'),
    ('associado_unidade',   'unidade'),
    ('diretor',             'unidade')
ON CONFLICT DO NOTHING;

-- unidade.dashboard: Pais com filhos, Conselheiro, Associado
INSERT INTO role_screen (role_id, screen_id) VALUES
    ('pai',                 'unidade.dashboard'),
    ('conselheiro_unidade', 'unidade.dashboard'),
    ('associado_unidade',   'unidade.dashboard')
ON CONFLICT DO NOTHING;

-- meu_painel: todos os membros e pais (todos os roles)
INSERT INTO role_screen (role_id, screen_id) VALUES
    ('diretor',             'meu_painel'),
    ('secretaria',          'meu_painel'),
    ('tesouraria',          'meu_painel'),
    ('equipe_pontuacao',    'meu_painel'),
    ('conselheiro_unidade', 'meu_painel'),
    ('associado_unidade',   'meu_painel'),
    ('pai',                 'meu_painel'),
    ('membro',              'meu_painel'),
    ('regional',            'meu_painel'),
    ('distrital',           'meu_painel'),
    ('executiva',           'meu_painel'),
    ('chefe_apoio',         'meu_painel'),
    ('apoio',               'meu_painel')
ON CONFLICT DO NOTHING;

-- tesouraria: Diretor, Secretaria, Tesouraria
INSERT INTO role_screen (role_id, screen_id) VALUES
    ('diretor',    'tesouraria'),
    ('secretaria', 'tesouraria'),
    ('tesouraria', 'tesouraria')
ON CONFLICT DO NOTHING;

-- apoio_regional.informacoes: todos da diretoria
INSERT INTO role_screen (role_id, screen_id) VALUES
    ('diretor',     'apoio_regional.informacoes'),
    ('secretaria',  'apoio_regional.informacoes'),
    ('tesouraria',  'apoio_regional.informacoes'),
    ('executiva',   'apoio_regional.informacoes'),
    ('chefe_apoio', 'apoio_regional.informacoes')
ON CONFLICT DO NOTHING;

-- apoio_regional.gerenciar_posts: todos da diretoria
INSERT INTO role_screen (role_id, screen_id) VALUES
    ('diretor',     'apoio_regional.gerenciar_posts'),
    ('secretaria',  'apoio_regional.gerenciar_posts'),
    ('tesouraria',  'apoio_regional.gerenciar_posts'),
    ('executiva',   'apoio_regional.gerenciar_posts'),
    ('chefe_apoio', 'apoio_regional.gerenciar_posts')
ON CONFLICT DO NOTHING;

-- apoio_regional.caixa_entrada: Regional e Distrital
INSERT INTO role_screen (role_id, screen_id) VALUES
    ('regional',  'apoio_regional.caixa_entrada'),
    ('distrital', 'apoio_regional.caixa_entrada')
ON CONFLICT DO NOTHING;

-- avaliacao_regional: Regional, Distrital
INSERT INTO role_screen (role_id, screen_id) VALUES
    ('regional',  'avaliacao_regional'),
    ('distrital', 'avaliacao_regional')
ON CONFLICT DO NOTHING;

-- pontuacao.ranking: todos da diretoria
INSERT INTO role_screen (role_id, screen_id) VALUES
    ('diretor',     'pontuacao.ranking'),
    ('secretaria',  'pontuacao.ranking'),
    ('tesouraria',  'pontuacao.ranking'),
    ('executiva',   'pontuacao.ranking'),
    ('chefe_apoio', 'pontuacao.ranking')
ON CONFLICT DO NOTHING;

-- pontuacao.lancamento: Equipe de Pontuação
INSERT INTO role_screen (role_id, screen_id) VALUES
    ('equipe_pontuacao', 'pontuacao.lancamento')
ON CONFLICT DO NOTHING;

-- patrimonio.gerenciar: Diretor, Secretaria, Executiva, Chefe de Apoio
INSERT INTO role_screen (role_id, screen_id) VALUES
    ('diretor',     'patrimonio.gerenciar'),
    ('secretaria',  'patrimonio.gerenciar'),
    ('executiva',   'patrimonio.gerenciar'),
    ('chefe_apoio', 'patrimonio.gerenciar')
ON CONFLICT DO NOTHING;

-- patrimonio.solicitar_materiais: toda a diretoria + Associado da Unidade
INSERT INTO role_screen (role_id, screen_id) VALUES
    ('diretor',           'patrimonio.solicitar_materiais'),
    ('secretaria',        'patrimonio.solicitar_materiais'),
    ('tesouraria',        'patrimonio.solicitar_materiais'),
    ('executiva',         'patrimonio.solicitar_materiais'),
    ('chefe_apoio',       'patrimonio.solicitar_materiais'),
    ('associado_unidade', 'patrimonio.solicitar_materiais')
ON CONFLICT DO NOTHING;

-- patrimonio.solicitacoes: Apoio
INSERT INTO role_screen (role_id, screen_id) VALUES
    ('apoio', 'patrimonio.solicitacoes')
ON CONFLICT DO NOTHING;
