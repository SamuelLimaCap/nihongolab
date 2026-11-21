---
slug: f8-infra-prod
titulo: Fase 8 — Infra de produção + observabilidade
criada: 2026-11-20
etapa: descoberta
status: rascunho
fase_atual: 1
protegidos: []
em_andamento_por:
plano_fases: 0
---

# Ficha — Fase 8 — Infra de produção + observabilidade

## Escopo

Compose de produção com perfis `core` e `full`, Dockerfiles ARM64, nginx com cache e headers de segurança, TLS, Prometheus, Grafana, Loki, limites de memória, backup diário, deploy por GitHub Actions, `docs/deploy.md` e plano B gerenciado.

## Fora de escopo

Kubernetes. Multi-região.

## Depende de

f7-pwa-offline concluída.

## Critério de pronto (do PLAN)

App no ar com HTTPS, dashboard do Grafana com métricas, restore do backup testado.
