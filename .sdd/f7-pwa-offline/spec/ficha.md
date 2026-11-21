---
slug: f7-pwa-offline
titulo: Fase 7 — PWA offline
criada: 2026-11-20
etapa: descoberta
status: rascunho
fase_atual: 1
protegidos: []
em_andamento_por:
plano_fases: 0
---

# Ficha — Fase 7 — PWA offline

## Escopo

Service worker, cache de cartões vencidos e fila de revisões no IndexedDB (Dexie), sincronização em lote idempotente, indicador de offline/sincronizando, e2e offline.

## Fora de escopo

Criar cartão offline. Sync em background no iOS.

## Depende de

f6-progresso concluída.

## Critério de pronto (do PLAN)

E2E: ficar offline, revisar 3 cartões, voltar online e o servidor registrar as 3 revisões.
