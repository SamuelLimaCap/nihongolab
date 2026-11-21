# Perguntas — Fase 4 — Mídia (legendas + processamento assíncrono)

### P-03 — Encoding das legendas (projeto)
- Recomendação: Só UTF-8 primeiro. Ver `docs/sdd/decisoes.md`.
- Quem decide: usuário
- Status: aberta

### P-05 — Direção da dependência `media` ↔ `srs` (projeto)
- Contexto: Evita ciclo entre módulos.
- Recomendação: Só `media → srs/api`; front manda os dados da frase ao `srs`. Ver `docs/sdd/decisoes.md`.
- Quem decide: usuário
- Status: aberta

### P-F4-01 — Polling do status: intervalo e limite?
- Recomendação: 1 s nos primeiros 10 s, depois 3 s; para em `DONE`/`FAILED` ou após 2 min.
- Quem decide: usuário
- Status: aberta
