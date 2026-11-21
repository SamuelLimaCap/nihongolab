# Delta — Fase 0 × PLAN

### D-F0-01 — Dependências do Modulith
- Tipo: MUDAR
- Antes (PLAN): `spring-modulith (starter-core, starter-jpa, events-jdbc)`
- Depois: `spring-modulith-starter-core`, `spring-modulith-starter-jdbc`, `spring-modulith-starter-test` (test)
- Motivo: D-06
- Decidido por: proposto (aguardando)

### D-F0-02 — Migração do outbox
- Tipo: MUDAR
- Antes (PLAN): nenhuma migração na Fase 0
- Depois: `V001__shared_event_publication.sql`
- Motivo: D-07
- Decidido por: proposto (aguardando)

### D-F0-03 — Comando do compose de dev
- Tipo: MUDAR
- Antes: `docker compose -f infra/docker-compose.dev.yml up -d`
- Depois: `docker compose --env-file .env -f infra/docker-compose.dev.yml up -d`
- Motivo: com `-f infra/...`, o compose procura o `.env` em `infra/`. Explícito evita surpresa. D-12.
- Decidido por: proposto (aguardando)

### D-F0-04 — Runner de teste do front
- Tipo: MUDAR (o PLAN não especificava)
- Depois: Vitest, padrão do Angular 21+. No CI: `npm test -- --watch=false`.
- Decidido por: proposto (aguardando)

### D-F0-05 — Segurança mínima já na Fase 0
- Tipo: MUDAR (o PLAN deixa segurança para a Fase 2)
- Depois: `SecurityFilterChain` mínimo em `identity/adapter/in/web/SecurityConfig.java` que libera `/actuator/health/**` e autentica o resto.
- Motivo: o starter de security entra na Fase 0; sem config, o Boot gera senha aleatória e um form login que a Fase 2 teria que desfazer.
- Decidido por: proposto (aguardando)

### D-F0-06 — `PLAN.md` em `docs/`
- Tipo: MUDAR
- Depois: `docs/PLAN.md`
- Motivo: D-04
- Decidido por: usuário (2026-11-20, aceito ao pedir o SDD)
