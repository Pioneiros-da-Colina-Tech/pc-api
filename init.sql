-- public.cars definição
CREATE TABLE IF NOT EXISTS public.cars (
	brand varchar(255) NULL,
	model varchar(255) NULL,
	"year" int4 NULL
);

-- public.classe definição
CREATE TABLE IF NOT EXISTS public.classe (
	codigo text NOT NULL,
	nome text NOT NULL,
	CONSTRAINT classe_pkey PRIMARY KEY (codigo)
);

-- public.especialidades definição
CREATE TABLE IF NOT EXISTS public.especialidades (
	codigo text NOT NULL,
	nome text NOT NULL,
	CONSTRAINT especialidades_pkey PRIMARY KEY (codigo)
);

-- public.evento definição
CREATE TABLE IF NOT EXISTS public.evento (
	id serial4 NOT NULL,
	valor float4 NOT NULL,
	nome text NOT NULL,
	CONSTRAINT evento_pkey PRIMARY KEY (id)
);

-- public.fechamento definição
CREATE TABLE IF NOT EXISTS public.fechamento (
	id serial4 NOT NULL,
	entrada float4 NOT NULL,
	saida float4 NOT NULL,
	ano int4 NOT NULL,
	mes int4 NOT NULL,
	CONSTRAINT fechamento_pkey PRIMARY KEY (id)
);

-- public.mensalidades definição
CREATE TABLE IF NOT EXISTS public.mensalidades (
	id serial4 NOT NULL,
	valor float4 NOT NULL,
	ano int4 NOT NULL,
	mes int4 NOT NULL,
	CONSTRAINT mensalidades_pkey PRIMARY KEY (id)
);

-- public.patrimonio definição
CREATE TABLE IF NOT EXISTS public.patrimonio (
	id serial4 NOT NULL,
	nome text NOT NULL,
	quantidade int4 NOT NULL,
	descricao text NULL,
	data_aquisicao date DEFAULT CURRENT_DATE NULL,
	CONSTRAINT patrimonio_pkey PRIMARY KEY (id)
);

-- public.reunioes definição
CREATE TABLE IF NOT EXISTS public.reunioes (
	id serial4 NOT NULL,
	nome text NOT NULL,
	"data" date NOT NULL,
	CONSTRAINT reunioes_pkey PRIMARY KEY (id)
);

-- public.solicitacoes_externas definição
CREATE TABLE IF NOT EXISTS public.solicitacoes_externas (
	id serial4 NOT NULL,
	nome text NOT NULL,
	email text NOT NULL,
	telefone text NOT NULL,
	departamento text NOT NULL,
	data_coleta date NOT NULL,
	data_devolucao date NOT NULL,
	status text DEFAULT 'Pendente'::text NULL,
	CONSTRAINT solicitacoes_externas_pkey PRIMARY KEY (id)
);

-- public.ata definição
CREATE TABLE IF NOT EXISTS public.ata (
	id serial4 NOT NULL,
	reuniao_id int4 NOT NULL,
	descricao text NOT NULL,
	titulo text NOT NULL,
	CONSTRAINT ata_pkey PRIMARY KEY (id),
	CONSTRAINT ata_reuniao_id_fkey FOREIGN KEY (reuniao_id) REFERENCES public.reunioes(id)
);

-- public.caixa definição
CREATE TABLE IF NOT EXISTS public.caixa (
	id serial4 NOT NULL,
	tipo text NOT NULL,
	descricao text NOT NULL,
	valor float4 NOT NULL,
	"data" date NOT NULL,
	id_evento int4 NULL,
	CONSTRAINT caixa_pkey PRIMARY KEY (id),
	CONSTRAINT caixa_id_evento_fkey FOREIGN KEY (id_evento) REFERENCES public.evento(id)
);

-- public.evento_documentos definição
CREATE TABLE IF NOT EXISTS public.evento_documentos (
	id serial4 NOT NULL,
	id_evento int4 NOT NULL,
	nome_documento text NOT NULL,
	CONSTRAINT evento_documentos_pkey PRIMARY KEY (id),
	CONSTRAINT evento_documentos_id_evento_fkey FOREIGN KEY (id_evento) REFERENCES public.evento(id)
);

-- public.requisitos_classes definição
CREATE TABLE IF NOT EXISTS public.requisitos_classes (
	id serial4 NOT NULL,
	codigo_classe text NOT NULL,
	secao text NOT NULL,
	requisito int4 NOT NULL,
	texto text NOT NULL,
	CONSTRAINT requisitos_classes_pkey PRIMARY KEY (id),
	CONSTRAINT requisitos_classes_codigo_classe_fkey FOREIGN KEY (codigo_classe) REFERENCES public.classe(codigo)
);

-- public.unidades definição
CREATE TABLE IF NOT EXISTS public.unidades (
	id serial4 NOT NULL,
	nome text NOT NULL,
	codigo_classe_regular text NULL,
	codigo_classe_avancada text NULL,
	CONSTRAINT unidades_pkey PRIMARY KEY (id),
	CONSTRAINT fk_codigo_classe FOREIGN KEY (codigo_classe_regular) REFERENCES public.classe(codigo),
	CONSTRAINT fk_codigo_classe_avancada FOREIGN KEY (codigo_classe_avancada) REFERENCES public.classe(codigo)
);

-- public.ato definição
CREATE TABLE IF NOT EXISTS public.ato (
	id serial4 NOT NULL,
	ata_id int4 NOT NULL,
	descricao text NOT NULL,
	titulo text NOT NULL,
	unidade_id int4 NOT NULL,
	CONSTRAINT ato_pkey PRIMARY KEY (id),
	CONSTRAINT ato_ata_id_fkey FOREIGN KEY (ata_id) REFERENCES public.ata(id),
	CONSTRAINT ato_unidade_id_fkey FOREIGN KEY (unidade_id) REFERENCES public.unidades(id)
);

-- public.avaliacao_classes definição
CREATE TABLE IF NOT EXISTS public.avaliacao_classes (
	id serial4 NOT NULL,
	id_unidade int4 NOT NULL,
	id_requisito int4 NOT NULL,
	conclusao date NOT NULL,
	status varchar(20) NOT NULL,
	aproved_at date NULL,
	created_at timestamp DEFAULT now() NOT NULL,
	CONSTRAINT avaliacao_classes_pkey PRIMARY KEY (id),
	CONSTRAINT status_check CHECK (((status)::text = ANY ((ARRAY['Avaliação'::character varying, 'Aprovado'::character varying, 'Refazer'::character varying])::text[]))),
	CONSTRAINT avaliacao_classes_id_requisito_fkey FOREIGN KEY (id_requisito) REFERENCES public.requisitos_classes(id),
	CONSTRAINT avaliacao_classes_id_unidade_fkey FOREIGN KEY (id_unidade) REFERENCES public.unidades(id)
);

-- public.membros definição
CREATE TABLE IF NOT EXISTS public.membros (
	id serial4 NOT NULL,
	nome text NOT NULL,
	codigo_sgc text NOT NULL,
	id_unidade int4 NULL,
	cargo text NOT NULL,
	CONSTRAINT membros_codigo_sgc_key UNIQUE (codigo_sgc),
	CONSTRAINT membros_pkey PRIMARY KEY (id),
	CONSTRAINT membros_id_unidade_fkey FOREIGN KEY (id_unidade) REFERENCES public.unidades(id)
);

-- public.permissao definição
CREATE TABLE IF NOT EXISTS public.permissao (
	codigo_sgc varchar(50) NOT NULL,
	permissao varchar(100) NOT NULL,
	CONSTRAINT permissao_pkey PRIMARY KEY (codigo_sgc, permissao),
	CONSTRAINT permissao_codigo_sgc_fkey FOREIGN KEY (codigo_sgc) REFERENCES public.membros(codigo_sgc) ON DELETE CASCADE ON UPDATE CASCADE
);

-- public.sentinelas_classe definição
CREATE TABLE IF NOT EXISTS public.sentinelas_classe (
	id serial4 NOT NULL,
	codigo_sgc text NOT NULL,
	codigo_classe text NOT NULL,
	conclusao date NOT NULL,
	status varchar(20) NOT NULL,
	aproved_at date NULL,
	created_at timestamp DEFAULT now() NOT NULL,
	CONSTRAINT sentinela_classe_pkey PRIMARY KEY (id),
	CONSTRAINT status_check CHECK (((status)::text = ANY ((ARRAY['Avaliação'::character varying, 'Aprovado'::character varying, 'Refazer'::character varying])::text[]))),
	CONSTRAINT sentinela_classe_codigo_classe_fkey FOREIGN KEY (codigo_classe) REFERENCES public.classe(codigo),
	CONSTRAINT sentinela_classe_codigo_sgc_fkey FOREIGN KEY (codigo_sgc) REFERENCES public.membros(codigo_sgc) ON UPDATE CASCADE
);

-- public.sentinelas_especialidade definição
CREATE TABLE IF NOT EXISTS public.sentinelas_especialidade (
	id serial4 NOT NULL,
	codigo_sgc text NOT NULL,
	codigo_especialidade text NOT NULL,
	conclusao date NOT NULL,
	status varchar(20) NOT NULL,
	aproved_at date NULL,
	created_at timestamp DEFAULT now() NOT NULL,
	CONSTRAINT sentinela_especialidade_pkey PRIMARY KEY (id),
	CONSTRAINT status_check CHECK (((status)::text = ANY ((ARRAY['Avaliação'::character varying, 'Aprovado'::character varying, 'Refazer'::character varying])::text[]))),
	CONSTRAINT sentinela_especialidade_codigo_especialidade_fkey FOREIGN KEY (codigo_especialidade) REFERENCES public.especialidades(codigo),
	CONSTRAINT sentinela_especialidade_codigo_sgc_fkey FOREIGN KEY (codigo_sgc) REFERENCES public.membros(codigo_sgc) ON UPDATE CASCADE
);

-- public.solicitacoes definição
CREATE TABLE IF NOT EXISTS public.solicitacoes (
	id serial4 NOT NULL,
	codigo_sgc text NOT NULL,
	id_item int4 NOT NULL,
	quantidade int4 NOT NULL,
	data_solicitacao date NOT NULL,
	status text DEFAULT 'Pendente'::text NULL,
	reuniao_id int4 NOT NULL,
	CONSTRAINT solicitacoes_pkey PRIMARY KEY (id),
	CONSTRAINT solicitacoes_codigo_sgc_fkey FOREIGN KEY (codigo_sgc) REFERENCES public.membros(codigo_sgc) ON UPDATE CASCADE,
	CONSTRAINT solicitacoes_id_item_fkey FOREIGN KEY (id_item) REFERENCES public.patrimonio(id),
	CONSTRAINT solicitacoes_reuniao_id_fkey FOREIGN KEY (reuniao_id) REFERENCES public.reunioes(id)
);

-- public.user_classes definição
CREATE TABLE IF NOT EXISTS public.user_classes (
	codigo_sgc text NOT NULL,
	codigo_classe text NOT NULL,
	status varchar(20) NULL,
	CONSTRAINT user_classes_pkey PRIMARY KEY (codigo_sgc, codigo_classe),
	CONSTRAINT user_classes_status_check CHECK (((status)::text = ANY ((ARRAY['Pendente'::character varying, 'Entregue'::character varying, 'Investidura'::character varying])::text[]))),
	CONSTRAINT user_classes_codigo_classe_fkey FOREIGN KEY (codigo_classe) REFERENCES public.classe(codigo),
	CONSTRAINT user_classes_codigo_sgc_fkey FOREIGN KEY (codigo_sgc) REFERENCES public.membros(codigo_sgc) ON UPDATE CASCADE
);

-- public.user_especialidades definição
CREATE TABLE IF NOT EXISTS public.user_especialidades (
	codigo_sgc text NOT NULL,
	codigo_especialidade text NOT NULL,
	status varchar(20) NULL,
	CONSTRAINT user_especialidades_pkey PRIMARY KEY (codigo_sgc, codigo_especialidade),
	CONSTRAINT user_especialidades_status_check CHECK (((status)::text = ANY ((ARRAY['Pendente'::character varying, 'Entregue'::character varying, 'Investidura'::character varying])::text[]))),
	CONSTRAINT user_especialidades_codigo_especialidade_fkey FOREIGN KEY (codigo_especialidade) REFERENCES public.especialidades(codigo),
	CONSTRAINT user_especialidades_codigo_sgc_fkey FOREIGN KEY (codigo_sgc) REFERENCES public.membros(codigo_sgc) ON UPDATE CASCADE
);

-- public.user_evento_documentos definição
CREATE TABLE IF NOT EXISTS public.user_evento_documentos (
	id serial4 NOT NULL,
	codigo_sgc text NOT NULL,
	id_evento int4 NOT NULL,
	id_documento int4 NOT NULL,
	data_entrega date DEFAULT CURRENT_DATE NULL,
	CONSTRAINT user_evento_documentos_pkey PRIMARY KEY (id),
	CONSTRAINT user_evento_documentos_codigo_sgc_fkey FOREIGN KEY (codigo_sgc) REFERENCES public.membros(codigo_sgc) ON UPDATE CASCADE,
	CONSTRAINT user_evento_documentos_id_documento_fkey FOREIGN KEY (id_documento) REFERENCES public.evento_documentos(id),
	CONSTRAINT user_evento_documentos_id_evento_fkey FOREIGN KEY (id_evento) REFERENCES public.evento(id)
);

-- public.user_mensalidades definição
CREATE TABLE IF NOT EXISTS public.user_mensalidades (
	id_mensalidade int4 NOT NULL,
	codigo_sgc text NOT NULL,
	status text DEFAULT 'Pendente'::text NULL,
	CONSTRAINT user_mensalidades_pkey PRIMARY KEY (id_mensalidade, codigo_sgc),
	CONSTRAINT user_mensalidades_codigo_sgc_fkey FOREIGN KEY (codigo_sgc) REFERENCES public.membros(codigo_sgc) ON UPDATE CASCADE,
	CONSTRAINT user_mensalidades_id_mensalidade_fkey FOREIGN KEY (id_mensalidade) REFERENCES public.mensalidades(id)
);

-- public.usuarios definição (Tabela users)
CREATE TABLE IF NOT EXISTS public.users (
    id text PRIMARY KEY UNIQUE,
    username text NOT NULL UNIQUE,
    email text NOT NULL UNIQUE,
    hashed_password text NOT NULL UNIQUE,
    full_name text,
    phone_number text,
    disabled boolean NOT NULL DEFAULT false,
    sgc_code text REFERENCES membros(codigo_sgc) ON UPDATE CASCADE,
    created_at timestamp with time zone not null default now(),
    updated_at timestamp with time zone null default now(),
    deleted_at timestamp with time zone DEFAULT NULL,
    CONSTRAINT usuarios_codigo_sgc_fkey FOREIGN KEY (sgc_code) REFERENCES public.membros(codigo_sgc) ON UPDATE CASCADE
);

-- public.associados definição
CREATE TABLE IF NOT EXISTS public.associados (
	user_id int4 NOT NULL,
	unidade_id int4 NOT NULL,
	CONSTRAINT fk_associados_unidade FOREIGN KEY (unidade_id) REFERENCES public.unidades(id) ON DELETE CASCADE,
	CONSTRAINT fk_associados_user FOREIGN KEY (user_id) REFERENCES public.membros(id) ON DELETE CASCADE
);

-- public.avaliacao_especialidade definição
CREATE TABLE IF NOT EXISTS public.avaliacao_especialidade (
	id serial4 NOT NULL,
	codigo_sgc text NOT NULL,
	codigo_especialidade text NOT NULL,
	conclusao date NOT NULL,
	status varchar(20) NOT NULL,
	aproved_at date NULL,
	created_at timestamp DEFAULT now() NOT NULL,
	CONSTRAINT avaliacao_especialidade_pkey PRIMARY KEY (id),
	CONSTRAINT status_check CHECK (((status)::text = ANY ((ARRAY['Avaliação'::character varying, 'Aprovado'::character varying, 'Refazer'::character varying])::text[]))),
	CONSTRAINT avaliacao_especialidade_codigo_especialidade_fkey FOREIGN KEY (codigo_especialidade) REFERENCES public.especialidades(codigo),
	CONSTRAINT avaliacao_especialidade_codigo_sgc_fkey FOREIGN KEY (codigo_sgc) REFERENCES public.membros(codigo_sgc) ON UPDATE CASCADE
);

-- public.chamadas definição
CREATE TABLE IF NOT EXISTS public.chamadas (
	id serial4 NOT NULL,
	reuniao_id int4 NOT NULL,
	presenca int4 NOT NULL,
	pontualidade int4 NOT NULL,
	uniforme int4 NOT NULL,
	modestia int4 NOT NULL,
	codigo_sgc text NULL,
	CONSTRAINT chamadas_pkey PRIMARY KEY (id),
	CONSTRAINT chamadas_codigo_sgc_fkey FOREIGN KEY (codigo_sgc) REFERENCES public.membros(codigo_sgc),
	CONSTRAINT chamadas_reuniao_id_fkey FOREIGN KEY (reuniao_id) REFERENCES public.reunioes(id)
);

-- public.inscricao_eventos definição
CREATE TABLE IF NOT EXISTS public.inscricao_eventos (
	codigo_sgc text NOT NULL,
	status text DEFAULT 'Pendente'::text NULL,
	id_evento int4 NOT NULL,
	CONSTRAINT inscricao_eventos_pkey PRIMARY KEY (codigo_sgc, id_evento),
	CONSTRAINT inscricao_eventos_codigo_sgc_fkey FOREIGN KEY (codigo_sgc) REFERENCES public.membros(codigo_sgc) ON UPDATE CASCADE,
	CONSTRAINT inscricao_eventos_id_evento_fkey FOREIGN KEY (id_evento) REFERENCES public.evento(id)
);
