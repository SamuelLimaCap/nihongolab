# Fase 0 — Fundação

- **Slug:** f0-fundacao
- **Criada:** 2026-11-20
- **Ficha:** `spec/ficha.md`
- **Plano do projeto:** `docs/PLAN.md` → "Fase 0: Fundação"
- **Guia à mão:** `docs/guia/fase-0-fundacao.md`

## Voltar aqui

Perguntas respondidas e `validar_spec.py` PASS. Próximo: o **usuário** revisa `spec/` e muda `status: aprovada` na `ficha.md`. Depois: papel `testes` (o usuário escreve, o agente orienta), cartões C01–C10.

## Checklist

- [x] Descoberta (a partir de `CLAUDE.md` original, `PLAN.md` e decisões do projeto)
- [x] Mapa (greenfield)
- [x] Plano (8 passos)
- [x] Spec em rascunho
- [x] Perguntas P-F0-01 a P-F0-03 respondidas
- [ ] Spec aprovada pelo usuário
- [ ] Testes escritos e congelados
- [ ] Passos 1–8 implementados
- [ ] Validação PASS
- [ ] CI verde e teste de arquitetura falha com import proibido (critério do PLAN)

## Decisões

- 2026-11-20 · Spring Boot 3.5.x (D-01) · decisão do usuário, ciente do fim do suporte OSS.
- 2026-11-20 · Registry JDBC com `spring-modulith-starter-jdbc` (D-06) · proposta.

## Dúvidas abertas

Ver `spec/perguntas.md`.

## Para depois

- Reavaliar Spring Boot 4.x antes da Fase 8 (D-01).

## Diário

- 2026-11-20 · claude-code/claude-opus-5-5 · descoberta, mapa, planejador, spec · — · spec da Fase 0 escrita em rascunho a partir do PLAN e do CLAUDE.md original.
- 2026-11-21 · opencode/deepseek-v4.1-flash · guia · — · P-F0-01..03 respondidas; validar_spec PASS; aguardando o usuário aprovar a spec.
