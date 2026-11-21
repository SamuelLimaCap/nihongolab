# Delta — Fase 1 × PLAN

### D-F1-01 — Migrações
- Tipo: MUDAR
- Antes (PLAN): `V001__srs_init.sql`; seed em `V002__srs_kana_seed.sql` ou JSON
- Depois: `V002__srs_init.sql`; seed por JSON + command
- Motivo: D-07
- Decidido por: proposto (aguardando)

### D-F1-02 — Conferência do outbox
- Tipo: MUDAR
- Antes (PLAN): "conferem ... a gravação do evento na tabela de publicação"
- Depois: confere a publicação do `CardReviewed` com `ApplicationEvents`; a linha em `event_publication` fica para a Fase 2
- Motivo: D-11
- Decidido por: proposto (aguardando)

### D-F1-03 — `CardReviewed` com mais campos
- Tipo: MUDAR
- Antes (PLAN): `CardReviewed(cardId, userId, grade, reviewedAt, newDueAt)`
- Depois: + `eventId`, `occurredAt` (`DomainEvent`), `reviewId`, `intervalDays`
- Motivo: listeners idempotentes por `eventId` (Fase 6) e estatística de intervalo
- Decidido por: proposto (aguardando)

### D-F1-04 — Eventos extras
- Tipo: MUDAR
- Depois: `DeckCreated` e `CardCreated` (o PLAN só cita `CardReviewed`; a Fase 6 escuta `CardCreated`)
- Decidido por: proposto (aguardando)

### D-F1-05 — Usuário de dev e segurança aberta em dev
- Tipo: MUDAR
- Depois: com `nihongolab.dev-user.enabled=true`, `/api/**` fica liberado e sem CSRF, e `CurrentUser` devolve `nihongolab.dev-user.id`. Padrão: desligado (`/api/**` → 401).
- Motivo: D-09
- Decidido por: proposto (aguardando)

### D-F1-06 — Coluna `lemma` em `srs_card`
- Tipo: MUDAR
- Depois: coluna já criada na Fase 1 (nula para cartão manual e kana)
- Motivo: a Fase 4 precisa dela para "palavras novas" sem migrar a tabela do `srs`
- Decidido por: proposto (aguardando)
