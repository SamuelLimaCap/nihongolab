# Fase 6 — Progresso + export/import (roteiro)

Spec: `.sdd/f6-progresso/` (em descoberta). Regras: RN-PROG-01..05.

## Ordem sugerida

1. Migração `progress_*` e `progress_processed_event`.
2. Listeners idempotentes de `CardCreated`, `CardReviewed`, `LessonCompleted`.
3. Query do painel.
4. Export JSON.
5. Import JSON (transação única, upsert por UUID, proteção entre usuários) + recálculo dos read models.
6. Export CSV para o Anki.
7. Teste de ida e volta.
8. Front: painel e card "Backup do progresso".

## Trechos-chave

Listener idempotente:

```java
@ApplicationModuleListener
void on(CardReviewed e) {
    int first = jdbc.sql("""
            insert into progress_processed_event(event_id, processed_at)
            values (:id, now()) on conflict do nothing
            """).param("id", e.eventId()).update();
    if (first == 0) {
        return;                       // já processado (RN-PROG-01)
    }
    jdbc.sql("""
            insert into progress_daily_stats(user_id, day, reviews, correct, new_cards)
            values (:user, :day, 1, :correct, 0)
            on conflict (user_id, day) do update
               set reviews = progress_daily_stats.reviews + 1,
                   correct = progress_daily_stats.correct + excluded.correct
            """)
        .param("user", e.userId().value())
        .param("day", dayInUserZone(e.reviewedAt(), e.userId()))
        .param("correct", "AGAIN".equals(e.grade()) ? 0 : 1)
        .update();
}
```

Import sem tocar dado alheio:

```sql
-- 1) recusa se algum ID do arquivo pertence a outro usuário
select count(*) from srs_card where id = any(:ids) and owner_id <> :me;   -- > 0 → 409 import-id-conflict

-- 2) upsert
insert into srs_card (id, deck_id, owner_id, ...) values (...)
on conflict (id) do update set front = excluded.front, ...
 where srs_card.owner_id = excluded.owner_id;
```

O passo 1 é o que garante a regra; o `where` do passo 2 é cinto de segurança.

CSV do Anki:

```text
#separator:semicolon
#html:false
#tags column:3
食べる;comer;nihongolab srs
"よろしく;お願いします";muito prazer;nihongolab
```

Campos com `;`, `"` ou quebra de linha vão entre aspas, com `"` duplicado.

## Armadilhas

- **Fuso:** "dia" depende do fuso do usuário (P-02). Uma revisão às 23h em São Paulo é dia seguinte em UTC.
- **Ordem dos listeners:** não assuma ordem entre eventos; `CardReviewed` pode chegar antes do `CardCreated` correspondente no `progress`.
- **Import grande:** uma transação só pode ser longa. Limite o tamanho do arquivo e use `batchUpdate`.
- **Ida e volta:** compare por conteúdo, ignorando campos gerados (`version`, `processed_at`).

## Testes (prévia)

- Mesmo evento entregue duas vezes conta uma vez.
- Export → `truncate` das tabelas do usuário → import → export de novo = igual ao primeiro (RN-PROG-05).
- Import com um `cardId` de outro usuário → 409 e nada gravado.
