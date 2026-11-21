# Plano — Fase 1: Domínio SRS + Kana

## Visão

API de decks, cartões e revisão funcionando com SM-2, decks de kana prontos, tudo isolado por usuário e testado em unidade (domínio) e integração (Postgres real).

## Passo 1 — Shared kernel (S)
- Objetivo: tipos base usados por todos os módulos.
- Entregáveis: `UserId`, `DomainEvent`, `AggregateRoot`, `DomainException` (+ `Kind`) em `dev.nihongolab.shared`; `ApiExceptionHandler` em `dev.nihongolab.shared.web`.
- Depende de: f0
- Testes que cobrem: C01, C02
- Pronto quando: testes de unidade do shared verdes.
- Especialidade: backend
- Status: pendente

## Passo 2 — Value objects do `srs` (S)
- Objetivo: VOs com validação no construtor.
- Entregáveis: `DeckId`, `CardId`, `ReviewId`, `DeckName`, `CardContent`, `Grade`, `SchedulingState`, `CardSource`, `SystemDeck`.
- Depende de: 1
- Testes que cobrem: C03, C04, C05, C06
- Pronto quando: testes de unidade verdes.
- Especialidade: backend
- Status: pendente

## Passo 3 — Scheduler SM-2 (M)
- Objetivo: cálculo do próximo estado.
- Entregáveis: `Scheduler`, `Sm2Scheduler`.
- Depende de: 2
- Testes que cobrem: C10, C11, C12
- Pronto quando: tabela de referência inteira verde.
- Especialidade: backend
- Status: pendente

## Passo 4 — Aggregates e eventos (M)
- Objetivo: `Deck` e `Card` protegendo invariantes e registrando eventos.
- Entregáveis: `Deck`, `Card`, `Review`, `ReviewOutcome`; `DeckCreated`, `CardCreated`, `CardReviewed` em `srs/domain/event` com `@NamedInterface("events")`.
- Depende de: 3
- Testes que cobrem: C20, C21, C22, C23
- Pronto quando: testes de unidade verdes; ArchUnit verde.
- Especialidade: backend
- Status: pendente

## Passo 5 — Persistência (M)
- Objetivo: tabelas e adapters de repositório.
- Entregáveis: `V002__srs_init.sql`; entidades JPA, repositórios Spring Data e adapters que implementam `DeckRepository`, `CardRepository`, `ReviewRepository`.
- Depende de: 4
- Testes que cobrem: C30
- Pronto quando: ida e volta domínio → banco → domínio sem perda.
- Especialidade: backend
- Status: pendente

## Passo 6 — Usuário corrente e modo dev (S)
- Objetivo: controllers obtêm o `UserId` sem depender do login.
- Entregáveis: `identity/api/CurrentUser` (+ `package-info` com `@NamedInterface("api")`), `DevCurrentUser`, `NoSessionCurrentUser`, ajuste no `SecurityConfig`.
- Depende de: f0
- Testes que cobrem: C70, C71
- Pronto quando: com a propriedade desligada `/api/**` dá 401; ligada, libera.
- Especialidade: backend
- Status: pendente

## Passo 7 — Commands (M)
- Objetivo: casos de uso de escrita.
- Entregáveis: `CreateDeck`, `CreateCard`, `ReviewCard` (port/in + implementação em `application/command`), publicação dos eventos.
- Depende de: 5
- Testes que cobrem: C31, C32, C33, C34, C35, C36, C37
- Pronto quando: testes de integração verdes.
- Especialidade: backend
- Status: pendente

## Passo 8 — Queries (S)
- Objetivo: leituras com `JdbcClient`.
- Entregáveis: `DueCardsQuery`, `DeckSummaryQuery` (port/in + implementação em `application/query`).
- Depende de: 5 (paralelizável com 7)
- Testes que cobrem: C40, C41, C42
- Pronto quando: testes de integração verdes.
- Especialidade: backend
- Status: pendente

## Passo 9 — API REST (M)
- Objetivo: endpoints do contrato com erros em ProblemDetail.
- Entregáveis: `DeckController`, `ReviewController`, DTOs, mapeamento de erros.
- Depende de: 6, 7, 8
- Testes que cobrem: C50–C58
- Pronto quando: testes de API verdes.
- Especialidade: backend
- Status: pendente

## Passo 10 — Decks de kana (S)
- Objetivo: hiragana e katakana prontos para o usuário.
- Entregáveis: `content/kana/hiragana.json`, `katakana.json`, `KanaContentSource` (port/out) + adapter, `SeedKanaDecks` (command), `DevKanaSeeder`.
- Depende de: 7
- Testes que cobrem: C60, C61, C62
- Pronto quando: usuário de dev tem 2 decks com 46 cartões cada, mesmo reiniciando a app.
- Especialidade: backend
- Status: pendente
