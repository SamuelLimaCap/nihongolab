# Descoberta — Fase 0

Fontes lidas: `docs/PLAN.md` (Fase 0), `CLAUDE.md` original (hoje em `AGENTS.md`), `docs/sdd/decisoes.md`.

## Decidido

| # | Decisão | Motivo | Origem |
|---|---|---|---|
| 1 | Spring Boot 3.5.x, Java 21, Maven com wrapper | decisão do usuário | D-01 |
| 2 | Spring Modulith 1.4.x com `starter-core`, `starter-jdbc`, `starter-test` | registry JDBC único | D-06 (proposta) |
| 3 | Angular 22, standalone, zoneless, SCSS, sem SSR, testes com Vitest (`ng test`) | versão estável atual | D-02 |
| 4 | `V001__shared_event_publication.sql` cria a tabela do outbox | Flyway + `ddl-auto: validate` | D-07 (proposta) |
| 5 | Compose de dev com `--env-file .env`, portas só em `127.0.0.1` | não expor banco na rede | D-12 (proposta) |
| 6 | Testcontainers declarados como `@Bean @ServiceConnection` num `@TestConfiguration` importado pela base de teste | containers vivem junto com o contexto Spring em cache; evita porta morta entre classes de teste | guia |
| 7 | Regras ArchUnit com `allowEmptyShould(true)` | na Fase 0 os pacotes estão vazios e o ArchUnit falha regra sem classe por padrão | guia |
| 8 | Segurança mínima: `/actuator/health/**` aberto, resto autenticado, sem form login nem basic | o starter de security está no classpath desde a Fase 0 | — |
| 9 | Pacote `shared` é `@ApplicationModule(type = OPEN)`; `identity/api`, `srs/api` etc. com `@NamedInterface("api")`; `<modulo>/domain/event` com `@NamedInterface("events")` | permitir só o acesso previsto entre módulos | D-05 (proposta) |
| 10 | Logs ECS no console | `AGENTS.md` | — |
| 11 | Node 24 LTS no CI e no dev | compatível com Angular 22 | P-F0-03 |

## Descartado

- `spring-modulith-starter-jpa` junto com `events-jdbc`: dois registries de publicação. Ver D-06.
- Containers `static` com `@Container` numa classe base abstrata: o Testcontainers para os containers ao fim de cada classe e o contexto Spring em cache aponta para portas mortas.
