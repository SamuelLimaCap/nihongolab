# Descoberta — Fase 1

Fontes: `docs/PLAN.md` (Fase 1), `AGENTS.md`, `docs/sdd/dominio.md`, `docs/sdd/decisoes.md`.

## Decidido

| # | Decisão | Motivo | Origem |
|---|---|---|---|
| 1 | SM-2 conforme RN-SM2-01..06; `AGAIN` volta em 10 min; ease com 2 casas | regra precisa para testes determinísticos | D-10 (proposta) |
| 2 | `ReviewCard` idempotente por `reviewId` do cliente; repetição devolve o resultado gravado | sync offline da Fase 7 | PLAN, RN-REV-01..04 |
| 3 | `srs_review` guarda estado antes e depois | permite recalcular na Fase 7 (P-04) | RN-REV-04 |
| 4 | O servidor define `reviewedAt` pelo `Clock` na Fase 1 | `reviewedAt` do cliente só entra no batch da Fase 7 | — |
| 5 | Usuário corrente via `identity.api.CurrentUser`; modo `dev-user` por propriedade | Fase 2 traz o login | D-09 (proposta) |
| 6 | Seed de kana por command idempotente que lê JSON de `content/kana/`; na Fase 1 roda no `ApplicationReadyEvent` para o usuário de dev | Fase 2 troca o gatilho para `UserRegistered` | D-07 |
| 7 | Publicação de evento conferida com `@RecordApplicationEvents` + `ApplicationEvents` (Spring Test) | registry não grava sem listener | D-11 (proposta) |
| 8 | Recurso de outro usuário → 404 | não revelar existência | NFR-SEC-02 |
| 9 | Exceções de regra: `DomainException(code, kind)` no `shared`; o handler web traduz `kind` em status | um ponto só de mapeamento | — |
| 10 | Commands devolvem um record de resultado (não a entidade) | o controller monta o DTO sem nova consulta | CQRS leve |
| 11 | Nome de deck único por dono, sem diferenciar maiúsculas (índice `lower(name)`) | RN-DECK-01 | — |

## Descartado

- Seed de kana por migração SQL: decks são por usuário; migração não conhece usuários.
- `AbstractAggregateRoot` do Spring Data no domínio: viola a regra de domínio puro (D-08).
- Gerar `reviewId` no servidor: quebraria a idempotência do sync offline.
