@AGENTS.md

## Específico do Claude Code

- Os subagentes `sdd`, `sdd-descoberta`, `sdd-mapa`, `sdd-planejador`, `sdd-spec`, `sdd-testes`, `sdd-implementar` e `sdd-validar` estão instalados globalmente em `~/.claude/agents/`. Neste repo, eles seguem `docs/sdd/papeis.md`, que tem precedência sobre a versão global.
- Neste repo, use os scripts de `tools/sdd/` em vez de `~/.claude/utils/`.
- Entradas: `/sdd <slug>`, `/tarefa-voltar <slug>`, `/tarefa-parar <slug>`. Os slugs das fases estão em `.sdd/PAINEL.md`.
- No `Diário` da tarefa, identifique-se como `claude-code/<modelo>`.
