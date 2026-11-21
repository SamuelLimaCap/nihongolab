# J04 — Ver cartões vencidos e resumo dos decks

- Objetivo: saber o que revisar agora.
- Ator: usuário autenticado.

## Fluxo principal

```fluxo
GET /api/review/due?deckId=&limit=50  → DueCardsQuery (JdbcClient) → cartões com due_at <= now do usuário
GET /api/decks                        → DeckSummaryQuery → por deck: totalCards e dueCards
```

## Regras

- Vencido: `due_at <= clock.instant()`.
- Ordem dos vencidos: `due_at` crescente, empate por `id`.
- Ordem dos decks: `lower(name)` crescente.
- `limit` padrão 50, aceito de 1 a 200.
- Só dados do usuário corrente (NFR-SEC-01).
- Queries não carregam aggregates.

## Vazio e erro

- Sem cartões vencidos → `[]`.
- Sem decks → `[]`.
- `limit` 0 ou 201 → 400 `validation-failed`.
- `deckId` de outro usuário ou inexistente → 404 `deck-not-found`.
