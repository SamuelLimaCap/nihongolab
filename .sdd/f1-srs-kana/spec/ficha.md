---
slug: f1-srs-kana
titulo: Fase 1 — Domínio SRS + Kana
criada: 2026-11-20
etapa: spec
status: rascunho
fase_atual: 1
protegidos: []
em_andamento_por:
plano_fases: 10
---

# Ficha — Fase 1: Domínio SRS + Kana

## Escopo

Shared kernel; domínio `srs` em Java puro (decks, cartões, SM-2, revisões); commands e queries; persistência com Flyway; API REST de decks, cartões e revisão; decks de hiragana e katakana. Usuário fixo de desenvolvimento enquanto não há login.

## Fora de escopo

- Login, sessão, CSRF real, rate limit (Fase 2).
- Telas (Fase 3).
- Editar ou apagar deck/cartão (não está no PLAN; vira pergunta se surgir).
- Kana com dakuten/yōon (P-06).
- Listener do `progress` e conferência da linha em `event_publication` (D-11).

## Depende de

f0-fundacao.

## Critério de pronto (do PLAN, ajustado por D-11)

Testes de integração criam um deck, revisam um cartão e conferem o novo `dueAt` e a publicação do `CardReviewed`.
