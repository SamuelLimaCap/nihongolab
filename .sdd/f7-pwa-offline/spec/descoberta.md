# Descoberta — Fase 7 — PWA offline

**Semente.** Escrita em 2026-11-20 a partir do `docs/PLAN.md` e da spec do projeto, antes da conversa de descoberta. O papel `descoberta` parte daqui.

## Já se sabe (da spec do projeto e de armadilhas conhecidas)

- `POST /api/review/batch` idempotente por `reviewId` (RN-REV-02).
- Sincronizar no evento `online` e na abertura do app (Background Sync não existe no Safari).
- O service worker só existe no build de produção: o e2e roda contra `ng build` servido estático, não `ng serve`.
- Playwright: `context.setOffline(true)`.

## A decidir na descoberta

Ver `perguntas.md`. Leia também a seção da fase em `docs/PLAN.md` e as RNs relacionadas em `docs/sdd/dominio.md`.
