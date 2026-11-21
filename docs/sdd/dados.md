# Modelo de dados

PostgreSQL 16, Flyway, `ddl-auto: validate`. Tabelas prefixadas pelo módulo. IDs `uuid` gerados na aplicação. Datas `timestamptz`.

Nenhuma FK entre tabelas de módulos diferentes: a fronteira do módulo vale também no banco. Dentro do módulo, FK normal.

## Fase 0 — `V001__shared_event_publication.sql`

Tabela do Event Publication Registry do Spring Modulith 1.4 (JDBC, PostgreSQL):

```sql
CREATE TABLE IF NOT EXISTS event_publication
(
  id               UUID NOT NULL,
  listener_id      TEXT NOT NULL,
  event_type       TEXT NOT NULL,
  serialized_event TEXT NOT NULL,
  publication_date TIMESTAMP WITH TIME ZONE NOT NULL,
  completion_date  TIMESTAMP WITH TIME ZONE,
  PRIMARY KEY (id)
);
CREATE INDEX IF NOT EXISTS event_publication_serialized_event_hash_idx
  ON event_publication USING hash(serialized_event);
CREATE INDEX IF NOT EXISTS event_publication_by_completion_date_idx
  ON event_publication (completion_date);
```

Confira o DDL contra o `schema-postgresql.sql` do jar `spring-modulith-events-jdbc` da versão usada antes de commitar.

## Fase 1 — `srs`

```sql
CREATE TABLE srs_deck (
  id          UUID PRIMARY KEY,
  owner_id    UUID         NOT NULL,
  name        VARCHAR(100) NOT NULL,
  system_key  VARCHAR(30),
  created_at  TIMESTAMPTZ  NOT NULL,
  version     BIGINT       NOT NULL DEFAULT 0
);
CREATE UNIQUE INDEX srs_deck_owner_name_uq ON srs_deck (owner_id, lower(name));
CREATE UNIQUE INDEX srs_deck_owner_system_key_uq ON srs_deck (owner_id, system_key) WHERE system_key IS NOT NULL;

CREATE TABLE srs_card (
  id             UUID PRIMARY KEY,
  deck_id        UUID          NOT NULL REFERENCES srs_deck (id),
  owner_id       UUID          NOT NULL,
  front          VARCHAR(500)  NOT NULL,
  back           VARCHAR(1000) NOT NULL,
  reading        VARCHAR(200),
  example        VARCHAR(1000),
  lemma          VARCHAR(200),
  source_type    VARCHAR(20)   NOT NULL,
  source_ref     VARCHAR(200),
  repetitions    INT           NOT NULL,
  interval_days  INT           NOT NULL,
  ease           NUMERIC(4,2)  NOT NULL,
  due_at         TIMESTAMPTZ   NOT NULL,
  created_at     TIMESTAMPTZ   NOT NULL,
  version        BIGINT        NOT NULL DEFAULT 0
);
CREATE INDEX srs_card_owner_due_idx ON srs_card (owner_id, due_at);
CREATE INDEX srs_card_deck_idx ON srs_card (deck_id);
CREATE INDEX srs_card_owner_lemma_idx ON srs_card (owner_id, lemma) WHERE lemma IS NOT NULL;

CREATE TABLE srs_review (
  id                    UUID PRIMARY KEY,          -- reviewId do cliente
  card_id               UUID         NOT NULL REFERENCES srs_card (id),
  owner_id              UUID         NOT NULL,
  grade                 VARCHAR(10)  NOT NULL,
  reviewed_at           TIMESTAMPTZ  NOT NULL,
  prev_repetitions      INT          NOT NULL,
  prev_interval_days    INT          NOT NULL,
  prev_ease             NUMERIC(4,2) NOT NULL,
  prev_due_at           TIMESTAMPTZ  NOT NULL,
  new_repetitions       INT          NOT NULL,
  new_interval_days     INT          NOT NULL,
  new_ease              NUMERIC(4,2) NOT NULL,
  new_due_at            TIMESTAMPTZ  NOT NULL
);
CREATE INDEX srs_review_card_idx ON srs_review (card_id, reviewed_at);
CREATE INDEX srs_review_owner_day_idx ON srs_review (owner_id, reviewed_at);
```

`lemma` já existe na Fase 1 (nulo para cartão manual) para a Fase 4 não precisar de migração no `srs`.

## Fase 2 — `identity` (rascunho)

`identity_user(id uuid pk, provider varchar(20), provider_subject varchar(200), display_name, email null, avatar_url null, time_zone varchar(50) null, created_at)`, único em `(provider, provider_subject)`.

Spring Session cuida da sessão no Redis (nada no Postgres).

## Fase 4 — `media` (rascunho)

- `media_subtitle(id, owner_id, show_title, episode, status, failure_reason, line_count, skipped_blocks, imported_at, version)`
- `media_subtitle_line(id, subtitle_id fk, idx, start_ms, end_ms, text)`
- `media_token(id, line_id fk, position, surface, lemma, reading, part_of_speech, start_offset)`
- Índice `media_subtitle_line (subtitle_id, idx)`; busca por texto para a Fase 5: `pg_trgm` em `media_subtitle_line.text` (decidir na fase).

## Fase 5 — `grammar` (rascunho)

- `grammar_lesson(id, slug unique, level, ord, title, explanation, content_hash)`
- `grammar_point(id, lesson_id fk, ord, pattern, meaning)`
- `grammar_example(id, point_id fk, ord, japanese, reading, translation)`
- `grammar_lesson_completion(user_id, lesson_id, completed_at, pk (user_id, lesson_id))`

## Fase 6 — `progress` (rascunho)

- `progress_processed_event(event_id uuid pk, processed_at)`
- `progress_daily_stats(user_id, day date, reviews, correct, new_cards, pk (user_id, day))`
- `progress_streak(user_id pk, current_days, longest_days, last_day)`
- `progress_level(user_id, level, total, learned, pk (user_id, level))`
