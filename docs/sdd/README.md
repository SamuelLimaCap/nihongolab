# SDD no Nihongo Lab

SDD (Spec-Driven Development): primeiro se decide e escreve **o que** o sistema faz, com casos de teste concretos. Só depois se escreve código. A spec é a fonte da verdade e é o que permite que agentes diferentes (Claude Code, OpenCode, modelos diferentes ou você, à mão) trabalhem no mesmo projeto sem se contradizer.

## Dois níveis de spec

| Nível | Onde | Muda quando |
|---|---|---|
| **Projeto** — vale para todas as fases | `docs/sdd/produto.md`, `dominio.md`, `eventos.md`, `api.md`, `dados.md`, `nfr.md`, `decisoes.md` | Uma decisão nova é tomada. Mudança aqui exige entrada em `decisoes.md`. |
| **Fase** — uma tarefa SDD por fase do `docs/PLAN.md` | `.sdd/f<N>-<nome>/` | Durante a fase. |

A spec da fase **detalha** a do projeto. Se as duas divergirem, a da fase está errada ou a do projeto precisa de uma decisão nova. Nos dois casos: pare e pergunte.

## Fluxo de uma fase

```fluxo
descoberta → mapa → planejamento → spec → [usuário aprova] → testes → [gate congela] → código → validação
```

| Etapa | Papel | Entrega | Sai quando |
|---|---|---|---|
| descoberta | `descoberta` | `spec/descoberta.md`, `perguntas.md`, `delta.md` | não há pergunta bloqueante aberta |
| mapa | `mapa` | `spec/mapa.md` (o que já existe no repo e será tocado) | mapa sem buracos bloqueantes |
| planejamento | `planejador` | `spec/plano.md` (passos = commits) | usuário aprova o plano |
| spec | `spec` | `spec/jornadas/J*.md`, `contrato.md`, `testes.md` | `validar_spec.py` PASS e usuário muda `status: aprovada` |
| testes | `testes` | testes escritos e **falhando**; `protegidos:` preenchido | `sdd_gate.py --congelar` PASS |
| código | `implementar` | código que faz os testes passarem, um commit por passo | testes verdes |
| validação | `validar` | `VEREDITO: PASS` ou `FAIL n=<N>` | PASS |

A descrição completa de cada papel, para colar em qualquer IA, está em `papeis.md`.

## Arquivos de uma tarefa

```
.sdd/f1-srs-kana/
  TAREFA.md              diário, checklist, decisões, "Voltar aqui"
  spec/
    ficha.md             frontmatter: etapa, status, protegidos, em_andamento_por
    descoberta.md        o que foi decidido na conversa e por quê
    perguntas.md         dúvidas abertas (P-NN), cada uma com quem precisa responder
    delta.md             diferenças em relação ao PLAN/spec do projeto (MANTER / MUDAR / NAO FAZER)
    mapa.md              o que já existe no repo e será tocado (caminho:linha)
    plano.md             passos numerados; cada passo = 1 commit
    jornadas/J01-*.md    um fluxo de uso por arquivo
    contrato.md          endpoints, DTOs, erros, eventos e tabelas desta fase
    testes.md            cartões de teste (### Cnn) com valores exatos
    .gate.json           hashes dos testes congelados (gerado)
```

## Protocolo multi-agente

Várias IAs e modelos vão trabalhar no mesmo repo, em momentos diferentes. As regras abaixo evitam trabalho duplicado e contradições.

### 1. Unidade de trabalho

Um **passo** do `plano.md` de uma fase. Um passo = um commit. Nunca pegue dois passos de uma vez sem o usuário pedir.

### 2. Antes de começar

1. Leia `AGENTS.md`, este arquivo e o papel que vai exercer em `papeis.md`.
2. Leia `.sdd/PAINEL.md` e a `TAREFA.md` da fase (comece por "Voltar aqui").
3. Leia a `ficha.md`. Se `em_andamento_por:` estiver preenchido por outro agente, **pare** e avise o usuário.
4. Preencha `em_andamento_por: <ferramenta>/<modelo> <papel> passo <N> <AAAA-MM-DD>`.

### 3. Durante

- Toda afirmação sobre código existente cita `caminho/arquivo:linha`.
- Separe o que **leu** do que está **supondo**.
- Faltou informação? Registre em `spec/perguntas.md` (formato abaixo) e pare. Não escolha por conta própria.
- Não altere arquivo de `protegidos:`. Se um teste congelado parecer errado, registre a pergunta e pare.

### 4. Ao terminar

1. Limpe `em_andamento_por:` (deixe vazio).
2. Adicione uma linha no Diário da `TAREFA.md`:
   `AAAA-MM-DD · <ferramenta>/<modelo> · <papel> · passo <N> · <resultado em 1 linha>`
3. Atualize "Voltar aqui" com o próximo passo concreto e o papel que deve executá-lo.
4. Marque o Checklist.
5. Rode `python3 tools/sdd/tarefa_status.py --painel`.

### 5. Separação de papéis

- Quem implementa **não** valida o próprio código. Prefira um **modelo diferente** para validar (exemplo: implementou com um modelo, valide com outro). Registre os dois no Diário.
- Quem escreve a spec **não** a aprova. Só o usuário muda `status: aprovada`.
- O papel `testes` é conduzido pelo usuário: o agente orienta e revisa, mas não entrega o valor esperado sem pedido explícito.

### 6. Rastreabilidade

Commit em Conventional Commits com o trailer da tarefa:

```
feat(srs): agenda revisão com SM-2

Sdd-Task: f1-srs-kana#3
```

## Formatos

### Pergunta (`perguntas.md`)

```markdown
### P-03 — Cartão pode ser revisado antes de vencer?
- Bloqueia: passo 4 (ReviewCard)
- Opções: (a) sim, sempre; (b) não, 409
- Recomendação: (a) — revisão antecipada é comum em app de estudo
- Quem decide: usuário
- Status: aberta | respondida (AAAA-MM-DD: resposta)
```

### Delta (`delta.md`)

```markdown
### D-02 — Migração V001 vira V002
- Tipo: MUDAR
- Antes (PLAN): `V001__srs_init.sql`
- Depois: `V002__srs_init.sql`
- Motivo: a Fase 0 cria `V001__shared_event_publication.sql`
- Decidido por: usuário em AAAA-MM-DD | proposto (aguardando)
```

### Cartão de teste (`testes.md`)

```markdown
### C04 — EASY aumenta ease e intervalo · RN-SM2-03
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: unidade (domínio)
- Dado: repetitions=2, intervalDays=6, ease=2.50
- Quando: grade=EASY em 2026-01-10T12:00Z
- Então: ease=2.60, intervalDays=16, repetitions=3, dueAt=2026-01-26T12:00Z
- Origem: fórmula RN-SM2-02 com q=5 (dominio.md)
```

Valor ainda desconhecido fica `a calcular`. A spec só pode ser aprovada sem nenhum `a calcular`.

## Papéis do PLAN × papéis do SDD

O `docs/PLAN.md` cita agentes por especialidade. Eles se encaixam assim:

| PLAN | SDD |
|---|---|
| `architect` | `planejador` e `spec` |
| `backend`, `frontend`, `devops` | `implementar` (com a especialidade da fase) |
| `reviewer` | `validar` |

## Scripts

| Script | Faz |
|---|---|
| `tools/sdd/validar_spec.py .sdd/<slug>` | confere se os arquivos exigidos pela etapa existem e não estão vazios |
| `tools/sdd/sdd_gate.py <slug> --congelar` | grava o SHA-256 dos arquivos em `protegidos:` |
| `tools/sdd/sdd_gate.py <slug>` | falha se algum protegido mudou |
| `tools/sdd/tarefa_status.py --painel` | regenera `.sdd/PAINEL.md` |

Rode da raiz do repo.
