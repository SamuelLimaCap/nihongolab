---
slug: f2-identity
titulo: Fase 2 — Identity + segurança (OAuth2, BFF)
criada: 2026-11-20
etapa: descoberta
status: rascunho
fase_atual: 1
protegidos: []
em_andamento_por:
plano_fases: 0
---

# Ficha — Fase 2 — Identity + segurança (OAuth2, BFF)

## Escopo

Login com Google e GitHub no padrão BFF, sessão no Redis, CSRF para SPA, `/api/me` e `/api/logout`, isolamento entre usuários testado, rate limit e ADR 0002. Remove o modo `dev-user` da Fase 1.

## Fora de escopo

Telas (Fase 3). Perfil editável. Apagar conta.

## Depende de

f1-srs-kana concluída.

## Critério de pronto (do PLAN)

Rota protegida retorna 401 sem sessão; teste de acesso entre usuários passa; POST sem CSRF retorna 403; linha em `event_publication` conferida para `UserRegistered` (D-11).
