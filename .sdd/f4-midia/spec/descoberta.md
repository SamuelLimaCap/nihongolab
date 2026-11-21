# Descoberta — Fase 4 — Mídia (legendas + processamento assíncrono)

**Semente.** Escrita em 2026-11-20 a partir do `docs/PLAN.md` e da spec do projeto, antes da conversa de descoberta. O papel `descoberta` parte daqui.

## Já se sabe (da spec do projeto e de armadilhas conhecidas)

- Regras RN-MEDIA-01..06 em `docs/sdd/dominio.md`.
- `Tokenizer` do Kuromoji é thread-safe e pesado (dicionário IPADIC em memória): um bean único, criado uma vez.
- Listener de `SubtitleImported` no próprio `media`, assíncrono, idempotente (só processa `PENDING`).
- Front: `URL.createObjectURL(file)` no `<video>`; sincronizar por `timeupdate`; `URL.revokeObjectURL` ao trocar de arquivo. MKV não toca na maioria dos navegadores (NFR-COMP-02).
- Limite de upload 2 MB (NFR-SEC-06).

## A decidir na descoberta

Ver `perguntas.md`. Leia também a seção da fase em `docs/PLAN.md` e as RNs relacionadas em `docs/sdd/dominio.md`.
