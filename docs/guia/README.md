# Guia para codar à mão

Este guia é para quando **você** for implementar, sem agente. Ele segue a mesma spec que os agentes seguem, então dá para alternar: você faz um passo, um agente faz o próximo, outro agente valida.

## Como usar

1. Abra a tarefa da fase: `.sdd/f<N>-<nome>/TAREFA.md` → "Voltar aqui".
2. Preencha `em_andamento_por: humano <papel> passo <N> <data>` na `ficha.md`.
3. Leia o passo no `spec/plano.md`, os cartões de teste citados e o capítulo da fase neste guia.
4. Escreva o teste primeiro (ele tem que falhar), depois o código.
5. Rode `./mvnw verify` / `npm test -- --watch=false`.
6. Commit com o trailer `Sdd-Task: <slug>#<passo>`.
7. Atualize Diário, Checklist e "Voltar aqui"; limpe `em_andamento_por`; rode `python3 tools/sdd/tarefa_status.py --painel`.
8. Peça a um agente para fazer o papel `validar` (`docs/sdd/papeis.md`).

O código do guia é um ponto de partida que segue a spec. Se o guia e a spec divergirem, **a spec vale**: anote a divergência no `perguntas.md` da fase.

## Capítulos

| Arquivo | Conteúdo | Nível de detalhe |
|---|---|---|
| `00-ambiente.md` | Instalar JDK, Maven, Node, Angular CLI, Docker | completo |
| `01-conceitos.md` | Hexagonal, Modulith, DDD tático, eventos e outbox, CQRS, BFF — em uma página cada | completo |
| `fase-0-fundacao.md` | Monorepo, compose, backend, testes de arquitetura, frontend, CI | passo a passo com código |
| `fase-1-srs-kana.md` | Shared kernel, SM-2, aggregates, persistência, commands, queries, REST, kana | passo a passo com código |
| `fase-2-identity.md` … `fase-9-polimento.md` | Roteiro, trechos-chave e armadilhas | roteiro; detalhado quando a fase chegar |

## Convenções do guia

- Caminhos relativos à raiz do repo.
- Blocos `bash` rodam na raiz, a menos que comecem com `cd`.
- `// ...` num bloco de código significa "o resto segue o mesmo padrão".
