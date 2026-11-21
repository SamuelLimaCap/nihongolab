# Descoberta — Fase 6 — Progresso (CQRS) + export/import

**Semente.** Escrita em 2026-11-20 a partir do `docs/PLAN.md` e da spec do projeto, antes da conversa de descoberta. O papel `descoberta` parte daqui.

## Já se sabe (da spec do projeto e de armadilhas conhecidas)

- RN-PROG-01..05.
- Import nunca sobrescreve dado de outro usuário: `ON CONFLICT (id) DO UPDATE ... WHERE owner_id = excluded.owner_id` e verificação prévia; conflito → 409 e rollback total.
- Depois do import, recalcular os read models do usuário.
- CSV do Anki: separador `;`, campos com aspas quando necessário, cabeçalho `#separator:semicolon`.

## A decidir na descoberta

Ver `perguntas.md`. Leia também a seção da fase em `docs/PLAN.md` e as RNs relacionadas em `docs/sdd/dominio.md`.
