---
slug: f0-fundacao
titulo: Fase 0 — Fundação
criada: 2026-11-20
etapa: spec
status: rascunho
fase_atual: 1
protegidos: []
em_andamento_por:
plano_fases: 8
---

# Ficha — Fase 0: Fundação

## Escopo

Monorepo com backend Spring Boot 3.5 e frontend Angular 22 vazios, mas compilando e testados; Postgres e Redis de desenvolvimento; testes de arquitetura que barram import proibido; CI no GitHub Actions; documentação de arquitetura e ADR 0001.

## Fora de escopo

- Qualquer regra de negócio, endpoint de `/api` ou tela além do esqueleto.
- Login OAuth2 (Fase 2). Nesta fase, a segurança só libera `/actuator/health` e fecha o resto.
- Dockerfiles de produção, nginx e observabilidade (Fase 8).
- Playwright (entra quando houver tela, Fase 3+).

## Depende de

Nada.

## Critério de pronto (do PLAN)

O CI está verde e o teste de arquitetura falha se for criado um import proibido de propósito (cartão C03).
