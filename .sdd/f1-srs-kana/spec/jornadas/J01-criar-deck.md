# J01 — Criar deck

- Objetivo: o usuário cria um deck vazio para organizar cartões.
- Ator: usuário autenticado (na Fase 1, o usuário de dev).
- Pré-condições: nenhuma.
- Pós-condições: deck gravado com o usuário como dono; `DeckCreated` publicado.

## Fluxo principal

```fluxo
POST /api/decks {"name":"  Verbos "}   → controller valida DTO (@NotBlank, @Size max 100)
CurrentUser.currentUserId()            → UserId
CreateDeck(userId, "  Verbos ")        → DeckName apara para "Verbos"
DeckRepository.existsByOwnerAndNameIgnoreCase → false
Deck.create(...)                       → registra DeckCreated
save + publish                         → 201 {"id","name":"Verbos","systemKey":null,"createdAt"}
```

## Regras

- RN-DECK-01 nome único por dono, sem diferenciar maiúsculas.
- Nome aparado; 1 a 100 caracteres depois de aparar.

## Vazio e erro

- Nome vazio ou só espaços → 400 `validation-failed`, `errors[0].field = "name"`.
- Nome com 101+ caracteres → 400 `validation-failed`.
- Já existe "verbos" para o mesmo dono → 409 `deck-name-taken`.
- Outro usuário com "Verbos" → permitido.

## Fora de escopo

Renomear e apagar deck.
