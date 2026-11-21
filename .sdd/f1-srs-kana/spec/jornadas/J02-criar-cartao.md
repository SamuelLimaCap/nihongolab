# J02 — Criar cartão manual

- Objetivo: adicionar um cartão a um deck do próprio usuário.
- Ator: usuário autenticado.
- Pré-condições: deck existe e é do usuário.
- Pós-condições: cartão com estado inicial (RN-CARD-01), já vencido; `CardCreated` publicado.

## Fluxo principal

```fluxo
POST /api/decks/{deckId}/cards {"front":"食べる","back":"comer","reading":"たべる","example":"ご飯を食べる。"}
CreateCard(userId, deckId, content, MANUAL)
DeckRepository.findByIdAndOwner     → deck do usuário
Card.create(..., now)                → repetitions=0, intervalDays=0, ease=2.50, dueAt=now; CardCreated
save + publish                       → 201 com source {"type":"MANUAL","reference":null} e dueAt == createdAt
```

## Regras

- RN-CARD-01, RN-CARD-02.
- `front` 1–500, `back` 1–1000, `reading` até 200, `example` até 1000. Opcionais vazios viram `null`.

## Vazio e erro

- `front` ou `back` vazio → 400 `validation-failed`.
- Deck inexistente ou de outro usuário → 404 `deck-not-found`.

## Fora de escopo

Editar, mover e apagar cartão.
