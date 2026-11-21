---
slug: f4-midia
titulo: Fase 4 — Mídia (legendas + processamento assíncrono)
criada: 2026-11-20
etapa: descoberta
status: rascunho
fase_atual: 1
protegidos: []
em_andamento_por:
plano_fases: 0
---

# Ficha — Fase 4 — Mídia (legendas + processamento assíncrono)

## Escopo

Upload de `.srt`, parse e limpeza, tokenização assíncrona com Kuromoji, status `PENDING → PROCESSING → DONE/FAILED`, palavras novas, cartão a partir da frase, player com vídeo local sincronizado.

## Fora de escopo

Guardar vídeo no servidor. Dicionário (significado vem do usuário ou fica vazio).

## Depende de

f3-frontend-base concluída.

## Critério de pronto (do PLAN)

Enviar um `.srt` deixa o status em `DONE`, as palavras ficam clicáveis e o cartão criado aparece na revisão.
