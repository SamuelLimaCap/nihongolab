# Descoberta — Fase 5 — Gramática

**Semente.** Escrita em 2026-11-20 a partir do `docs/PLAN.md` e da spec do projeto, antes da conversa de descoberta. O papel `descoberta` parte daqui.

## Já se sabe (da spec do projeto e de armadilhas conhecidas)

- RN-GRAM-01 e RN-GRAM-02.
- `@Cacheable` com Redis exige serialização JSON configurada (`RedisCacheConfiguration` com serializer JSON e TTL). Records de leitura como valor.
- Busca de exemplos nas legendas: `pg_trgm` ou `LIKE` no texto, filtrando pelo usuário.
- Conteúdo de gramática é autoral: revisar fonte e licença de qualquer material de referência.

## A decidir na descoberta

Ver `perguntas.md`. Leia também a seção da fase em `docs/PLAN.md` e as RNs relacionadas em `docs/sdd/dominio.md`.
