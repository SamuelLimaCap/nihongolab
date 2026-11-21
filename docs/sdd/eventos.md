# Catálogo de eventos

Regras (de `AGENTS.md`): `record` em `<modulo>/domain/event/`, nome no passado, implementa `DomainEvent`, payload só com tipos do JDK e do `shared`. Listeners entre módulos com `@ApplicationModuleListener`, idempotentes.

Todo evento tem `UUID eventId` e `Instant occurredAt`, omitidos nas tabelas abaixo.

| Evento | Emissor | Quando | Payload | Consumidores | Fase |
|---|---|---|---|---|---|
| `DeckCreated` | `srs` | deck criado (manual ou de sistema) | `UUID deckId`, `UserId userId`, `String name`, `String systemKey` (nulo se manual) | — | 1 |
| `CardCreated` | `srs` | cartão criado | `UUID cardId`, `UUID deckId`, `UserId userId`, `String sourceType`, `String lemma` (nulo se não houver) | `progress` (6) | 1 |
| `CardReviewed` | `srs` | revisão nova gravada (não em repetição idempotente) | `UUID reviewId`, `UUID cardId`, `UserId userId`, `String grade`, `Instant reviewedAt`, `Instant newDueAt`, `int intervalDays` | `progress` (6) | 1 |
| `UserRegistered` | `identity` | primeiro login | `UserId userId`, `String displayName` | `srs` (seed de kana, 2) | 2 |
| `SubtitleImported` | `media` | `.srt` aceito e linhas gravadas | `UUID subtitleId`, `UserId userId`, `int lineCount` | `media` (tokenização, 4) | 4 |
| `SubtitleTokenized` | `media` | tokenização terminou | `UUID subtitleId`, `UserId userId`, `String status` (`DONE`/`FAILED`), `int tokenCount` | — (front faz polling) | 4 |
| `LessonCompleted` | `grammar` | lição concluída pela primeira vez | `UUID lessonId`, `String slug`, `String level`, `UserId userId` | `progress` (6) | 5 |

## Idempotência por consumidor

| Consumidor | Evento | Como garante |
|---|---|---|
| `srs` | `UserRegistered` | seed por `systemKey` único por dono (RN-KANA-02) |
| `media` | `SubtitleImported` | só processa se status for `PENDING` (RN-MEDIA-05) |
| `progress` | `CardCreated`, `CardReviewed`, `LessonCompleted` | `progress_processed_event(event_id)` na mesma transação (RN-PROG-01) |

## Outbox

- Tabela `event_publication` (Modulith, registry JDBC), criada por `V001__shared_event_publication.sql`.
- Só há linha para eventos que têm listener transacional (`@ApplicationModuleListener`).
- Publicações que falharam são reenviadas no restart (`spring.modulith.events.republish-outstanding-events-on-restart=true`).
- Publicações concluídas são apagadas após 7 dias por uma rotina agendada (Fase 8).
