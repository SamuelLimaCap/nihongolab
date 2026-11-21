# J03 — Revisar um cartão

- Objetivo: registrar a resposta do usuário e reagendar o cartão.
- Ator: usuário autenticado.
- Pré-condições: cartão do usuário (vencido ou não — RN-CARD-04).
- Pós-condições: novo estado gravado; `srs_review` com estado antes e depois; `CardReviewed` publicado uma vez.

## Fluxo principal

```fluxo
POST /api/review {"reviewId":"…","cardId":"…","grade":"GOOD"}
ReviewCard(userId, reviewId, cardId, grade)
ReviewRepository.findById(reviewId)  → vazio
CardRepository.findByIdAndOwner      → cartão
card.review(reviewId, grade, clock.instant(), scheduler)
                                     → novo SchedulingState; CardReviewed registrado
save card + save review + publish    → 200 {reviewId, cardId, grade, reviewedAt, repetitions, intervalDays, ease, dueAt}
```

## Fluxo alternativo — repetição (RN-REV-02)

```fluxo
ReviewRepository.findById(reviewId)  → existe, mesmo dono
                                     → 200 com o resultado gravado; nada muda; nenhum evento
```

## Regras

- RN-CARD-03, RN-CARD-04, RN-CARD-05, RN-REV-01..04, RN-SM2-01..06.
- `reviewedAt` = `clock.instant()` do servidor.

## Vazio e erro

- `reviewId`, `cardId` ou `grade` ausente; `grade` fora do enum → 400 `validation-failed`.
- Cartão inexistente ou de outro usuário → 404 `card-not-found`.
- `reviewId` já usado por outro usuário → 409 `review-id-conflict`.
- Duas requisições simultâneas no mesmo cartão (mesmo `reviewId` ou não): a que perder a corrida (lock otimista no `srs_card` ou chave primária do `srs_review`) recebe 409 `concurrent-update`. O cliente reenvia com o **mesmo** `reviewId` e cai na regra de repetição.

## Fora de escopo

Batch offline (Fase 7); desfazer revisão.
