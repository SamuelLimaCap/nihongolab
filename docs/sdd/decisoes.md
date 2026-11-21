# Decisões e perguntas do projeto

Decisões que valem para todas as fases. Decisão de uma fase só fica no `delta.md` da fase.

Status: **tomada** (o usuário decidiu) ou **proposta** (o SDD sugeriu; vale até o usuário dizer o contrário, mas precisa de confirmação antes da fase que depende dela).

## Decisões

### D-01 — Spring Boot 3.5.x
- Status: tomada (usuário, 2026-11-20)
- Contexto: o `CLAUDE.md` original fixava Boot 3.x. O 3.5 é o último 3.x e perdeu suporte OSS em 30/06/2026 (3.5.16 foi a última versão OSS).
- Decisão: manter Spring Boot 3.5.x (última patch disponível) com Spring Modulith 1.4.x.
- Consequências: sem patch de segurança OSS do Boot. Antes do deploy público (Fase 8), reavaliar migração para 4.x. A migração vira uma tarefa SDD própria, nunca uma mudança dentro de outra fase.

### D-02 — Angular 22
- Status: tomada (o `CLAUDE.md` pede "versão estável atual"; em 2026-11 é a 22)
- Consequências: standalone e zoneless por padrão; o runner de teste padrão é o Vitest (`ng test`); signals e Signal Forms estáveis.

### D-03 — Agentes usados
- Status: tomada (usuário, 2026-11-20)
- Decisão: Claude Code e OpenCode. A entrada comum é `AGENTS.md`; o `CLAUDE.md` só importa `@AGENTS.md`.

### D-04 — `PLAN.md` em `docs/`
- Status: tomada
- Decisão: `PLAN.md` foi movido da raiz para `docs/PLAN.md`, como o `CLAUDE.md` original já dizia.

### D-05 — Eventos em `domain/event`, expostos como named interface
- Status: tomada (usuário, 2026-11-21)
- Contexto: o Modulith barra acesso a subpacotes internos de outro módulo. Se o evento ficar em `srs/domain`, o listener do `progress` não compila sem violar a regra.
- Decisão: eventos em `<modulo>/domain/event/` com `@NamedInterface("events")`. O payload só usa tipos do JDK e do `shared`.
- Consequências: o ArchUnit permite acesso entre módulos só a `..api..` e `..domain.event..`.

### D-06 — Registry de eventos com `spring-modulith-starter-jdbc`
- Status: tomada (usuário, 2026-11-21)
- Contexto: o PLAN lista `starter-jpa` e `events-jdbc` juntos. O `starter-jpa` já traz o registry JPA; os dois juntos registram dois repositórios de publicação.
- Decisão: usar `spring-modulith-starter-core` + `spring-modulith-starter-jdbc` (registry JDBC, como o `AGENTS.md` pede) + `spring-modulith-starter-test`.

### D-07 — Numeração das migrações
- Status: tomada (usuário, 2026-11-21)
- Decisão: `V001__shared_event_publication.sql` (Fase 0) e `V002__srs_init.sql` (Fase 1). O seed de kana sai de JSON em `content/kana/`, por um command idempotente, e não de migração. O PLAN citava `V001__srs_init.sql` e `V002__srs_kana_seed.sql`.
- Motivo: a tabela do outbox precisa existir desde a Fase 0, e o Flyway roda com `ddl-auto: validate`. Os decks de kana são por usuário, e na Fase 2 o seed roda no `UserRegistered`; uma migração não sabe quais usuários existem.

### D-08 — `AggregateRoot` em Java puro
- Status: proposta
- Contexto: `AbstractAggregateRoot` é do Spring Data; o `domain` não pode importar Spring.
- Decisão: `shared` tem uma base `AggregateRoot` em Java puro (`registerEvent`, `domainEvents`, `clearDomainEvents`). O command publica os eventos com `ApplicationEventPublisher` depois do `save`, na mesma transação.

### D-09 — Usuário corrente via `identity.api.CurrentUser`
- Status: proposta
- Contexto: a Fase 1 tem API REST, mas o login só chega na Fase 2.
- Decisão: `identity/api/CurrentUser` (interface). Na Fase 1, uma implementação de desenvolvimento devolve um `UserId` fixo, ativa só com `nihongolab.dev-user.enabled=true`. Na Fase 2, ela é apagada e substituída pela sessão.
- Consequências: com a propriedade desligada (padrão), `/api/**` exige autenticação desde a Fase 1.

### D-10 — Variante do SM-2
- Status: proposta
- Decisão: regras RN-SM2-01 a RN-SM2-06 em `dominio.md`. `AGAIN` volta em 10 minutos; o ease é recalculado em toda revisão e guardado com 2 casas.

### D-11 — Conferência do outbox sai da Fase 1
- Status: proposta
- Contexto: o "Pronto quando" da Fase 1 pede conferir o evento na tabela de publicação. O registry só grava publicações de eventos que **têm listener** transacional. Na Fase 1 ninguém escuta `CardReviewed`.
- Decisão: a Fase 1 confere a publicação com `@RecordApplicationEvents` + `ApplicationEvents` (Spring Test). A linha em `event_publication` é conferida na Fase 2, com `UserRegistered` → listener do `srs`.

### D-12 — Ambiente de dev
- Status: tomada (usuário, 2026-11-21)
- Decisão: `docker compose --env-file .env -f infra/docker-compose.dev.yml`; portas ligadas só em `127.0.0.1`; o backend lê as mesmas variáveis do `.env` (`SPRING_DATASOURCE_*`, `SPRING_DATA_REDIS_URL`).

### D-13 — Tempo injetado
- Status: tomada (usuário, 2026-11-21)
- Decisão: um bean `Clock` = `Clock.tickMillis(ZoneOffset.UTC)`. O domínio recebe `Instant now` por parâmetro. Testes usam `Clock.fixed`.
- Motivo do `tickMillis`: o Postgres guarda microssegundos; com nanossegundos, o resultado devolvido e o gravado seriam diferentes (quebra a idempotência "mesmo corpo" de RN-REV-02).

## Perguntas abertas

### P-01 — Promtail ou Grafana Alloy?
- Fase: 8
- Contexto: a Grafana descontinuou o Promtail (fim de vida em março de 2026). O PLAN cita Promtail.
- Opções: (a) Grafana Alloy; (b) Docker logging driver do Loki; (c) Promtail mesmo assim.
- Recomendação: (a). Confirmar o status atual na descoberta da Fase 8.
- Status: aberta

### P-02 — Fuso horário do usuário
- Fase: 6 (sequência de dias e estatística diária)
- Opções: (a) guardar o fuso do navegador no perfil (`identity_user.time_zone`); (b) fixo `America/Sao_Paulo`; (c) UTC.
- Recomendação: (a), com padrão `America/Sao_Paulo`.
- Status: aberta

### P-03 — Encoding das legendas
- Fase: 4
- Opções: (a) só UTF-8 (com ou sem BOM), recusar o resto com 415; (b) detectar Shift_JIS/EUC-JP e converter.
- Recomendação: (a) primeiro; (b) se aparecer legenda real em Shift_JIS.
- Status: aberta

### P-04 — Revisão offline mais antiga que a última do servidor
- Fase: 7
- Opções: (a) grava no histórico mas não reagenda; (b) reaplica todas em ordem de `reviewedAt`, recalculando o estado do cartão.
- Recomendação: (b). O histórico de `srs_review` guarda o estado antes e depois, o que permite recalcular.
- Status: aberta

### P-05 — Direção da dependência entre `media` e `srs`
- Fase: 4
- Contexto: "palavras novas" precisam saber quais lemas o usuário já tem (`media` → `srs`). Criar cartão a partir da frase precisa do texto da linha (`srs` → `media`). As duas direções juntas formam um ciclo, que o Modulith proíbe.
- Recomendação: só `media` → `srs/api` (`KnownLemmas`). O front manda ao `srs` os dados da frase (texto, lema, leitura, referência ao episódio e tempos).
- Status: aberta

### P-06 — Kana com dakuten, handakuten e yōon
- Fase: 1
- Opções: (a) só os 46 básicos de cada silabário na Fase 1; (b) incluir が, ぱ, きゃ etc.
- Recomendação: (a). Os outros viram decks extras numa fase futura.
- Status: aberta

### P-07 — Login nos testes e2e
- Fase: 9 (e 7)
- Opções: (a) `mock-oauth2-server` como provedor OAuth2 nos testes; (b) endpoint de login falso num perfil `e2e`.
- Recomendação: (a). Não cria caminho de login alternativo no código de produção.
- Status: aberta

### P-08 — Estratégias do service worker
- Fase: 7
- Contexto: o PLAN diz "`freshness` para a API e `performance` para os assets". No `ngsw-config.json`, assets ficam em `assetGroups` (`installMode: prefetch`). `freshness` e `performance` são estratégias de `dataGroups` (API).
- Recomendação: assets em `assetGroups` com prefetch; `/api/review/**` em `freshness`; `/api/grammar/**` em `performance`.
- Status: aberta
