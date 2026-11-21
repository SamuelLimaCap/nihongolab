# Contrato da API

Prefixo `/api`, sem versão. JSON em `camelCase`. Datas em ISO-8601 UTC (`2026-01-10T12:00:00Z`). IDs são UUID.

Endpoints das fases ainda não especificadas estão marcados **rascunho**: a spec da fase pode mudá-los, atualizando este arquivo.

## Erros

Todo erro é `application/problem+json` (RFC 9457):

```json
{
  "type": "/problems/deck-name-taken",
  "title": "Já existe um deck com esse nome",
  "status": 409,
  "detail": "Já existe um deck chamado \"Verbos\".",
  "instance": "/api/decks",
  "code": "deck-name-taken"
}
```

Erro de validação de entrada (400) traz `errors`: `[{ "field": "name", "message": "..." }]`.

| `code` | Status | Quando |
|---|---|---|
| `validation-failed` | 400 | corpo ou parâmetro inválido |
| `unauthenticated` | 401 | sem sessão em `/api/**` |
| `csrf-invalid` | 403 | POST/PUT/DELETE sem token CSRF válido |
| `deck-not-found` | 404 | deck não existe **ou** é de outro usuário |
| `card-not-found` | 404 | cartão não existe **ou** é de outro usuário |
| `subtitle-not-found` | 404 | legenda não existe ou é de outro usuário |
| `lesson-not-found` | 404 | lição não existe |
| `deck-name-taken` | 409 | RN-DECK-01 |
| `review-id-conflict` | 409 | RN-REV-03 |
| `concurrent-update` | 409 | lock otimista ou corrida na mesma chave; o cliente pode reenviar |
| `import-id-conflict` | 409 | RN-PROG-04 |
| `unsupported-media` | 415 | arquivo não é `.srt` UTF-8 |
| `subtitle-empty` | 422 | nenhum bloco válido no `.srt` |
| `import-schema-unsupported` | 422 | `schemaVersion` desconhecido |
| `rate-limited` | 429 | limite excedido; header `Retry-After` |

## Fase 1 — SRS

### `POST /api/decks`
Request: `{ "name": "Verbos" }`
- 201 → `{ "id", "name", "systemKey": null, "createdAt" }`
- 400 `validation-failed` (nome vazio ou > 100) · 409 `deck-name-taken`

### `GET /api/decks`
- 200 → `[{ "id", "name", "systemKey", "totalCards", "dueCards" }]`, ordenado por `name` (sem diferenciar maiúsculas).

### `POST /api/decks/{deckId}/cards`
Request: `{ "front": "食べる", "back": "comer", "reading": "たべる", "example": "ご飯を食べる。" }`
- 201 → `{ "id", "deckId", "front", "back", "reading", "example", "source": { "type": "MANUAL", "reference": null }, "dueAt", "createdAt" }`
- 400 `validation-failed` · 404 `deck-not-found`

### `GET /api/review/due?deckId={uuid}&limit={n}`
- `deckId` opcional; `limit` padrão 50, máximo 200.
- 200 → `[{ "cardId", "deckId", "front", "back", "reading", "example", "dueAt" }]`, ordenado por `dueAt` crescente e depois `cardId`.
- 400 `validation-failed` (limit fora de 1..200) · 404 `deck-not-found` (deckId de outro usuário)

### `POST /api/review`
Request: `{ "reviewId": "uuid gerado no cliente", "cardId": "uuid", "grade": "GOOD" }`
- 200 → `{ "reviewId", "cardId", "grade", "reviewedAt", "repetitions", "intervalDays", "ease": 2.5, "dueAt" }`
- Repetir o mesmo `reviewId`: 200 com o mesmo corpo (RN-REV-02).
- 400 `validation-failed` · 404 `card-not-found` · 409 `review-id-conflict` · 409 `concurrent-update`

## Fase 2 — Identity

| Método e caminho | Resposta |
|---|---|
| `GET /oauth2/authorization/{google\|github}` | 302 para o provedor (Spring Security) |
| `GET /login/oauth2/code/{provider}` | callback; 302 para `/` |
| `GET /api/me` | 200 `{ "id", "displayName", "email", "avatarUrl", "provider" }` · 401 |
| `POST /api/logout` | 204; invalida a sessão; exige CSRF |

## Fase 4 — Mídia (rascunho)

| Método e caminho | Request | Resposta |
|---|---|---|
| `POST /api/media/subtitles` | multipart: `file` (.srt), `showTitle`, `episode` | 202 `{ "id", "status": "PENDING", "lineCount", "skippedBlocks" }` · 415 · 422 |
| `GET /api/media/subtitles` | — | 200 `[{ "id", "showTitle", "episode", "status", "lineCount", "importedAt" }]` |
| `GET /api/media/subtitles/{id}` | — | 200 `{ "id", "showTitle", "episode", "status", "failureReason", "lineCount" }` · 404 |
| `GET /api/media/subtitles/{id}/lines?offset=0&limit=200` | — | 200 `[{ "id", "index", "startMs", "endMs", "text", "tokens": [{ "surface", "lemma", "reading", "partOfSpeech", "isNew" }] }]` |
| `POST /api/decks/{deckId}/cards/from-sentence` | `{ "lemma", "reading", "meaning", "sentence", "subtitleId", "lineId", "startMs" }` | 201 (mesmo corpo do cartão, `source.type=SUBTITLE`) |

## Fase 5 — Gramática (rascunho)

| Método e caminho | Resposta |
|---|---|
| `GET /api/grammar/lessons?level=N5` | 200 `[{ "id", "slug", "level", "order", "title", "completed" }]` |
| `GET /api/grammar/lessons/{slug}` | 200 lição completa com pontos e exemplos (inclui frases das legendas do usuário) · 404 |
| `POST /api/grammar/lessons/{slug}/complete` | 204 (idempotente) |
| `POST /api/grammar/lessons/{slug}/cards` | `{ "deckId" }` → 201 `{ "created": 7 }` |

## Fase 6 — Progresso (rascunho)

| Método e caminho | Resposta |
|---|---|
| `GET /api/progress/dashboard` | 200 `{ "streakDays", "totalCards", "dueToday", "reviewsToday", "levels": [{ "level", "percent" }] }` |
| `GET /api/progress/export` | 200 JSON `{ "schemaVersion": 1, "exportedAt", "decks", "cards", "reviews", "lessonsCompleted", "subtitles" }` |
| `POST /api/progress/import` | corpo = export → 200 `{ "decks", "cards", "reviews", ... }` (contagens) · 409 · 422 |
| `GET /api/progress/export/anki.csv?deckId=` | 200 `text/csv`, `frente;verso;tags` |

## Fase 7 — Offline (rascunho)

| Método e caminho | Request | Resposta |
|---|---|---|
| `POST /api/review/batch` | `[{ "reviewId", "cardId", "grade", "reviewedAt" }]` (máx. 500) | 200 `[{ "reviewId", "status": "APPLIED"\|"DUPLICATE"\|"REJECTED", "dueAt", "code" }]` |
