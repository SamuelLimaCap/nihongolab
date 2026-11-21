# Perguntas — Fase 0

### P-F0-01 — Repositório no GitHub
- Bloqueia: passo 7 (CI) só para rodar de verdade; o arquivo do workflow pode ser escrito antes.
- Pergunta: qual o nome e a visibilidade do repo no GitHub (público, por ser portfólio)?
- Quem decide: usuário
- Status: respondida (2026-11-21: GitHub público, para portfólio)

### P-F0-02 — Confirmar decisões propostas
- Bloqueia: aprovação da spec
- Pergunta: confirma D-05, D-06, D-07, D-12 e D-13 de `docs/sdd/decisoes.md`?
- Recomendação: confirmar. Sem elas, a Fase 1 esbarra no Modulith (D-05), em registry duplicado (D-06) ou em migração faltando (D-07).
- Quem decide: usuário
- Status: respondida (2026-11-21: todas confirmadas; D-05, D-06, D-07, D-12 e D-13 passam a "tomada")

### P-F0-03 — Versão do Node
- Bloqueia: passo 6
- Opções: (a) Node 24 LTS; (b) a versão que você já tem instalada.
- Recomendação: (a). Confira com `ng version` depois de instalar o CLI 22.
- Quem decide: usuário
- Status: respondida (2026-11-21: Node 24 LTS; máquina já tem v24.21.0)
