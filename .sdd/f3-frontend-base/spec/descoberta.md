# Descoberta — Fase 3 — Frontend base

**Semente.** Escrita em 2026-11-20 a partir do `docs/PLAN.md` e da spec do projeto, antes da conversa de descoberta. O papel `descoberta` parte daqui.

## Já se sabe (da spec do projeto e de armadilhas conhecidas)

- Angular 22: standalone, zoneless e signals por padrão; testes com Vitest.
- Tokens: fundo `#0f1115`, superfície `#171a21`, borda `#262a33`, texto `#e7e9ee`, secundário `#9aa1ad`, destaque `#ff7a70`. Fontes Inter e Noto Sans JP, self-hosted (CSP da Fase 8 sem fontes externas).
- Noto Sans JP é pesada: usar subsets por `unicode-range` (ex.: pacotes `@fontsource`) e `font-display: swap`.
- XSRF: o `HttpClient` do Angular lê o cookie `XSRF-TOKEN` e manda `X-XSRF-TOKEN` só em requisições mutáveis para URL relativa. Em produção é mesma origem (nginx), então `withCredentials` não é necessário.
- Revisão: espaço mostra a resposta; teclas 1–4 escolhem a nota (NFR-UX-03). `reviewId` gerado no cliente com `crypto.randomUUID()`.
- Menu lateral a partir de 768 px; barra de abas abaixo; alvos de toque ≥ 44 px (NFR-UX-02).

## A decidir na descoberta

Ver `perguntas.md`. Leia também a seção da fase em `docs/PLAN.md` e as RNs relacionadas em `docs/sdd/dominio.md`.
