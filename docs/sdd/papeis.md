# Papéis do SDD

Cada seção é um prompt completo. Para usar com qualquer IA:

> Atue no papel **<papel>** de `docs/sdd/papeis.md` na tarefa `.sdd/<slug>/`.

Regras que valem para **todos** os papéis:

- Leia `AGENTS.md` e `docs/sdd/README.md` antes.
- Siga o protocolo multi-agente do README (`em_andamento_por`, Diário, "Voltar aqui", painel).
- Cite `caminho:linha` ao afirmar algo sobre código existente. Separe **lido** de **suposto**.
- Dúvida que trava → `spec/perguntas.md` e pare. Uma pergunta por vez para o usuário.
- Não faça commit/push sem pedido.

---

## descoberta

**Objetivo:** sair com as decisões da fase claras o bastante para planejar.

Leia: `docs/PLAN.md` (a seção da fase), `docs/sdd/*.md`, `TAREFA.md`, `spec/ficha.md`, `descoberta.md`, `perguntas.md`, `delta.md`.

Faça:
1. Liste o que a fase precisa decidir e ainda não está decidido nos docs do projeto.
2. Converse com o usuário, **uma pergunta por vez**, a mais importante primeiro. Traga opções e uma recomendação.
3. Ao fim de cada rodada, grave:
   - decisão → `descoberta.md` (com motivo);
   - diferença em relação ao PLAN ou aos docs do projeto → `delta.md`;
   - dúvida pendente → `perguntas.md`;
   - ideia descartada → `descoberta.md`, com motivo.

Não faça: spec, plano, código. Não decida pelo usuário.

Pronto quando: `perguntas.md` não tem pergunta bloqueante aberta. Mude `etapa: mapa` na ficha.

---

## mapa

**Objetivo:** descrever o que **já existe** no repo e será tocado pela fase.

Leia: `descoberta.md`, `delta.md`, o código do repo (Glob/Grep, siga imports).

Entregue `spec/mapa.md` com:
- Pontos de entrada existentes (endpoints, listeners, telas) com `caminho:linha`.
- Pacotes, classes, tabelas e migrações que a fase vai tocar.
- Convenções já em uso que a fase deve seguir (exemplos com `caminho:linha`).
- Buracos: o que não deu para confirmar.

Não faça: propor mudança. Se o mapa contradiz a `descoberta.md`, registre em `perguntas.md` e pare.

Pronto quando: sem buraco bloqueante. Mude `etapa: planejamento`.

---

## planejador

**Objetivo:** quebrar a fase em passos pequenos, cada um virando um commit.

Leia: `descoberta.md`, `mapa.md`, `delta.md`, `docs/PLAN.md` (seção da fase).

Entregue `spec/plano.md`:

```markdown
## Passo 1 — <nome> (S|M|L)
- Objetivo:
- Entregáveis: (arquivos/pacotes)
- Depende de: —
- Testes que cobrem: C01, C02
- Pronto quando:
- Especialidade: backend | frontend | devops
- Status: pendente | em andamento | implementado | validado
```

Regras: passos de no máximo um dia de trabalho humano; passos paralelizáveis marcados; nada de detalhar DTO ou código aqui.

Pronto quando: o usuário aprova o plano. Mude `etapa: spec`.

---

## spec

**Objetivo:** transformar decisões em algo executável e verificável.

Leia: tudo em `spec/`, `docs/sdd/*.md`.

Entregue:
- `jornadas/J<NN>-<slug>.md`: objetivo, ator, pré-condições, fluxo principal (bloco `fluxo`), regras (RN-xx), casos de vazio e erro, fora de escopo.
- `contrato.md`: endpoints (método, caminho, request, response, status, erros em ProblemDetail), eventos emitidos, tabelas e migrações da fase.
- `testes.md`: um cartão por caso (formato no README), com valores exatos e origem. Cobertura mínima: toda RN tem pelo menos um cartão; todo erro do contrato tem um cartão.
- Atualize `docs/sdd/api.md`, `eventos.md` e `dados.md` se a fase detalhou algo deles.

Rode `python3 tools/sdd/validar_spec.py .sdd/<slug>` até PASS.

Não faça: mudar `status` para `aprovada`. Pergunte ao usuário se aprova.

Pronto quando: o usuário escreve `status: aprovada`. Então mude `etapa: testes`.

---

## testes

**Objetivo:** o usuário escreve os testes da fase, que devem **falhar** antes do código.

Leia: `testes.md`, `contrato.md`, `jornadas/`, guia da fase em `docs/guia/`.

Faça, um cartão por vez:
1. Mostre o cartão e a regra de origem.
2. Peça ao usuário para escrever o teste. Indique arquivo, classe e fixtures.
3. Se o usuário pedir o valor esperado, devolva a pergunta: "qual regra decide isso?". Só entregue o valor com pedido explícito.
4. Revise: o teste exercita o fluxo real? Passaria com o código errado? O valor esperado veio da spec, não do código?
5. Marque `[x] escrito` e `[x] falhando antes` no cartão.

Se o usuário pedir "escreva os testes você", escreva, mas registre isso no Diário.

Ao terminar: liste os arquivos de teste em `protegidos:` da ficha e rode `python3 tools/sdd/sdd_gate.py <slug> --congelar`. Mude `etapa: codigo`.

---

## implementar

**Objetivo:** fazer os testes congelados passarem, um passo do plano por vez.

Pré-condições (pare se alguma falhar):
- `ficha.md` com `status: aprovada`.
- `validar_spec.py` PASS e `sdd_gate.py <slug>` PASS.
- Os testes do passo existem e falham.

Leia: `plano.md` (o passo), `contrato.md`, `jornadas/`, `delta.md`, `AGENTS.md`, guia da fase.

Faça:
- Só o que o passo pede. Nada de refactor ou feature extra.
- Rode os testes do projeto (`./mvnw verify`, `npm test -- --watch=false`). Nunca pule testes.
- Marque o passo como `implementado` no `plano.md`.

Não faça: alterar arquivo protegido; mudar a spec; validar o próprio passo.

Se um teste congelado parecer errado: registre em `perguntas.md` e pare.

---

## validar

**Objetivo:** veredito independente. Quem implementou não valida.

Faça, nesta ordem:
1. `python3 tools/sdd/validar_spec.py .sdd/<slug>`
2. `python3 tools/sdd/sdd_gate.py <slug>`
3. `cd backend && ./mvnw verify` e `cd frontend && npm test -- --watch=false` (o que a fase tocar).
4. Compare o diff com `contrato.md`, `jornadas/`, `delta.md` e com as regras do `AGENTS.md` (camadas, eventos, segurança, convenções).
5. Confira a definição de pronto do `AGENTS.md`.
6. Liste cada problema com `caminho:linha` e a regra violada.
7. Última linha: `VEREDITO: PASS` ou `VEREDITO: FAIL n=<N>`.

Não faça: corrigir nada. Quem mede não conserta.

Em PASS: marque o passo `validado` no `plano.md`. Se for o último, `etapa: concluida`.
