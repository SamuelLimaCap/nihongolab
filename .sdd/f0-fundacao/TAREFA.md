# Fase 0 — Fundação

- **Slug:** f0-fundacao
- **Criada:** 2026-11-20
- **Ficha:** `spec/ficha.md`
- **Plano do projeto:** `docs/PLAN.md` → "Fase 0: Fundação"
- **Guia à mão:** `docs/guia/fase-0-fundacao.md`

## Voltar aqui

Passos 1–4 implementados e commitados; C01, C02, C04 e C05 verdes. Próximo: **passo 5** (guardiões ArchUnit + `ApplicationModules.verify()`), cartões C03, C03b e C06. Pendências de processo: o **usuário** aprovar a spec (`status: aprovada`) e rodar `sdd_gate.py --congelar` com os testes de C03–C06.

## Checklist

- [x] Descoberta (a partir de `CLAUDE.md` original, `PLAN.md` e decisões do projeto)
- [x] Mapa (greenfield)
- [x] Plano (8 passos)
- [x] Spec em rascunho
- [x] Perguntas P-F0-01 a P-F0-03 respondidas
- [ ] Spec aprovada pelo usuário
- [ ] Testes escritos e congelados
- [x] Passos 1–4 implementados
- [ ] Passos 5–8 implementados
- [ ] Validação PASS
- [ ] CI verde e teste de arquitetura falha com import proibido (critério do PLAN)

## Decisões

- 2026-11-20 · Spring Boot 3.5.x (D-01) · decisão do usuário, ciente do fim do suporte OSS.
- 2026-11-20 · Registry JDBC com `spring-modulith-starter-jdbc` (D-06) · tomada (usuário, 2026-11-21).

## Dúvidas abertas

Ver `spec/perguntas.md`.

## Para depois

- Reavaliar Spring Boot 4.x antes da Fase 8 (D-01).

## Diário

- 2026-11-20 · claude-code/claude-opus-5-5 · descoberta, mapa, planejador, spec · — · spec da Fase 0 escrita em rascunho a partir do PLAN e do CLAUDE.md original.
- 2026-11-21 · opencode/deepseek-v4.1-flash · guia · — · P-F0-01..03 respondidas; validar_spec PASS; aguardando o usuário aprovar a spec.
- 2026-11-21 · opencode/deepseek-v4.1-flash · guia · passo 4 · C04 corrigido: Flyway 11 preserva o zero (`version = '001'`, não `'1'`); spec e guia ajustados.
- 2026-11-21 · usuário + opencode/deepseek-v4.1-flash · implementar · passos 1–3 · monorepo, compose de dev e esqueleto do backend; `./mvnw verify` verde; commits 6681cf7, 3888772, ba89e95.
- 2026-11-21 · usuário + opencode/deepseek-v4.1-flash · implementar · passo 4 · V001 + Testcontainers + C04/C05; 2 testes verdes; commit d1c6085.
