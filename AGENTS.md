# Nihongo Lab — instruções para agentes de IA

Plataforma pessoal de estudo de japonês: SRS (estilo Anki), kana, gramática por nível JLPT e mineração de frases a partir de legendas (.srt) de doramas.

Este arquivo vale para **qualquer** agente (Claude Code, OpenCode ou outro). O `CLAUDE.md` só importa este arquivo.

## Leia antes de qualquer tarefa

1. Este arquivo inteiro.
2. `docs/sdd/README.md` — o método SDD e o protocolo entre agentes.
3. `.sdd/PAINEL.md` — o que está em andamento.
4. A pasta da tarefa em `.sdd/<slug>/` (`TAREFA.md` e `spec/`).

A fonte da verdade é a spec. Se o código, o plano e a spec divergirem, **pare** e registre a divergência em `spec/perguntas.md` da tarefa. Não improvise.

## Documentos

| O quê | Onde |
|---|---|
| Plano por fases | `docs/PLAN.md` |
| Método SDD e protocolo multi-agente | `docs/sdd/README.md` |
| Papéis (descoberta, mapa, planejador, spec, testes, implementar, validar) | `docs/sdd/papeis.md` |
| Produto, domínio, eventos, API, dados, requisitos não funcionais | `docs/sdd/*.md` |
| Decisões tomadas e perguntas abertas do projeto | `docs/sdd/decisoes.md` |
| Uma tarefa por fase (f0 a f9) | `.sdd/f<N>-<nome>/` |
| Guia para codar à mão | `docs/guia/` |
| ADRs | `docs/adr/NNNN-titulo.md` |

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Java 21, Spring Boot 3.5.x, Spring Modulith 1.4.x, Spring Security (OAuth2 Client), Spring Data JPA + JdbcClient |
| Banco | PostgreSQL 16 + Flyway |
| Cache/sessão | Redis 7 (Spring Session + Spring Cache) |
| Tokenização | Kuromoji (`com.atilika.kuromoji:kuromoji-ipadic`) |
| Frontend | Angular 22, standalone components, signals, `@angular/pwa` |
| Infra | Docker Compose, Nginx, Prometheus, Grafana, Loki |
| CI | GitHub Actions |
| Testes | JUnit 5, AssertJ, Testcontainers, ArchUnit, Spring Modulith tests, Vitest (Angular), Playwright |

Todas as imagens Docker precisam ter build **linux/arm64** (o deploy é numa VM ARM).

Spring Boot 3.5 está sem suporte OSS desde 30/06/2026. Foi uma decisão consciente (ver `docs/sdd/decisoes.md`, D-01). Não migre para 4.x sem nova decisão.

## Estrutura do repositório

```
backend/            app Spring Boot (Maven)
frontend/           app Angular
infra/              docker-compose*.yml, nginx/, prometheus/, grafana/, loki/
docs/               PLAN.md, architecture.md, adr/, sdd/, guia/
tools/sdd/          scripts do método SDD
.sdd/               tarefas SDD (uma pasta por fase)
.github/workflows/  CI/CD
```

## Arquitetura (obrigatório)

### Monólito modular + hexagonal + DDD tático

Módulos (Spring Modulith, um pacote raiz por módulo em `dev.nihongolab`):

| Módulo | Responsabilidade |
|---|---|
| `srs` | Decks, cartões, agendamento (SM-2), revisões |
| `grammar` | Lições e pontos gramaticais por nível JLPT |
| `media` | Upload de .srt, tokenização assíncrona, frases mineráveis |
| `progress` | Read models (CQRS), estatísticas, export/import de progresso |
| `identity` | Usuário, login OAuth2, usuário corrente |
| `shared` | Shared kernel: `UserId`, base de `DomainEvent` e `AggregateRoot`, tipos utilitários. Nada de lógica de negócio. |

Estrutura interna de **cada** módulo:

```
<modulo>/
  api/                    API pública para outros módulos (@NamedInterface("api"))
  domain/                 entidades, value objects, aggregates, serviços de domínio
    event/                eventos de domínio publicados (@NamedInterface("events"))
  application/
    port/in/              interfaces de casos de uso (commands) e de queries
    port/out/             interfaces de repositórios e serviços externos
    command/              implementações dos casos de uso (escrita)
    query/                implementações das queries (leitura)
  adapter/
    in/web/               controllers REST + DTOs
    in/event/             listeners de eventos de outros módulos
    out/persistence/      JPA entities, repositórios, mapeadores
    out/<outro>/          ex.: tokenizer/kuromoji
```

### Regras de dependência (verificadas por ArchUnit + `ApplicationModules.verify()`)

- `domain` não importa Spring, JPA, Jackson nem nada de `application`/`adapter`. Só Java puro e o `shared`. Única exceção: anotações do Modulith (`@NamedInterface`) em `package-info.java`.
- `application` depende de `domain`. Nunca de `adapter`.
- `adapter` depende de `application` e `domain`.
- Um módulo **não** acessa o `domain`/`application`/`adapter` de outro módulo. Ele só pode usar `<outro>/api` e `<outro>/domain/event`.
- Sem ciclos entre módulos.
- Entidades JPA ficam em `adapter/out/persistence` e são mapeadas de e para o domínio. Nunca exponha entidade JPA nem de domínio na API REST; use DTOs.

### DDD tático

- Aggregates protegem invariantes. Altere estado só por métodos do aggregate, nunca por setters.
- Value objects imutáveis (`record`), com validação no construtor.
- IDs são UUID gerados na aplicação, encapsulados em VOs (`CardId`, `DeckId`...). Nada de autoincremento: isso permite sync offline e export/import sem colisão.
- Aggregates registram eventos de domínio numa lista própria (base `AggregateRoot` do `shared`, Java puro). O command publica os eventos com `ApplicationEventPublisher` depois de salvar, na mesma transação.

### Eventos de domínio

- Eventos são `record`s em `<modulo>/domain/event/`, com nome no passado: `CardReviewed`, `SubtitleImported`, `SubtitleTokenized`.
- Todo evento implementa `DomainEvent` (`eventId` UUID e `occurredAt`).
- O payload de um evento só usa tipos do JDK (`UUID`, `Instant`, `String`, números) e do `shared`. Nunca VOs internos do módulo.
- Listeners entre módulos usam `@ApplicationModuleListener`, que é assíncrono e transacional.
- O Event Publication Registry do Spring Modulith (JDBC, tabela `event_publication`) é o **outbox**: nenhum evento se perde se a app cair.
- Listeners precisam ser **idempotentes** (guardam o `eventId` processado).
- Catálogo completo: `docs/sdd/eventos.md`.

### CQRS leve

- Command: caso de uso que carrega o aggregate, executa o comportamento e salva.
- Query: implementação separada que lê direto do banco com `JdbcClient` ou projeções e retorna DTOs de leitura. Não carrega aggregates.
- Read models do `progress` (tabelas `progress_*`) são atualizados por listeners de eventos. Mesmo banco, tabelas separadas, sem event sourcing.

### Processamento assíncrono

- Tarefas pesadas (tokenizar .srt) rodam em listeners assíncronos disparados por eventos.
- O status do processamento é exposto por uma query (`PENDING` → `PROCESSING` → `DONE`/`FAILED`).
- Não use RabbitMQ/Kafka: os eventos do Modulith + outbox resolvem e economizam RAM.

## Convenções

- Pacote base: `dev.nihongolab`. Código e identificadores em inglês; comentários e docs em português.
- **Flyway:** `backend/src/main/resources/db/migration/V<NNN>__<modulo>_<descricao>.sql`. Nunca edite uma migração já commitada; crie uma nova. As tabelas são prefixadas pelo módulo (`srs_card`, `media_subtitle`...). A tabela `event_publication` é do Modulith e fica sem prefixo.
- **API REST:** prefixo `/api`, sem versionamento. Erros no formato `ProblemDetail` (RFC 9457). Contrato: `docs/sdd/api.md`.
- **Segurança:** login OAuth2 (Google/GitHub) no padrão **BFF**. O backend faz o login, a sessão fica no Redis e o Angular recebe só um cookie `HttpOnly`, `Secure`, `SameSite=Lax`, com CSRF habilitado (cookie `XSRF-TOKEN`). Nenhum token no localStorage. Toda query e command filtram pelo `UserId` autenticado.
- **Usuário corrente:** controllers obtêm o `UserId` por `identity.api.CurrentUser`. Nunca leem o `SecurityContext` direto.
- **Redis:** sessões (Spring Session), cache de leitura (dicionário, lições) e rate limiting.
- **Config:** variáveis de ambiente, nunca segredos no repositório. Mantenha um `.env.example` atualizado.
- **Logs:** JSON estruturado (`logging.structured.format.console: ecs`), com `userId` e `traceId` no MDC.
- **Tempo:** injete `java.time.Clock`. Nunca chame `Instant.now()` direto no domínio; o tempo entra por parâmetro.

## Comandos

```bash
# dev: sobe postgres + redis (rode da raiz do repo)
docker compose --env-file .env -f infra/docker-compose.dev.yml up -d

# backend
cd backend && ./mvnw verify            # testes + ArchUnit + Modulith verify
cd backend && set -a && . ../.env && set +a && ./mvnw spring-boot:run

# frontend
cd frontend && npm ci && npm start     # proxy /api -> localhost:8080
cd frontend && npm test -- --watch=false && npm run e2e

# stack completa (prod-like)
docker compose -f infra/docker-compose.yml --profile full up -d --build

# SDD
python3 tools/sdd/validar_spec.py .sdd/<slug>
python3 tools/sdd/sdd_gate.py <slug> [--congelar]
python3 tools/sdd/tarefa_status.py --painel
```

## Definição de pronto (toda tarefa)

1. Testes cobrindo o comportamento novo: domínio com teste de unidade puro, adapters com Testcontainers.
2. `./mvnw verify` e `npm test` passando, incluindo ArchUnit e `ApplicationModules.verify()`.
3. Migração Flyway criada, se o schema mudou.
4. Sem segredos, sem `TODO` órfão, sem código morto.
5. Se tomou uma decisão de arquitetura, criou um ADR em `docs/adr/NNNN-titulo.md` (contexto, decisão, consequências, em até 15 linhas).
6. Um commit por passo do `plano.md`, em Conventional Commits (`feat(srs): ...`), com o trailer `Sdd-Task: <slug>#<passo>`.
7. `TAREFA.md` atualizado (Diário, Checklist, "Voltar aqui") e painel regenerado.

## O que NÃO fazer

- Não adicionar microsserviços, Kafka, RabbitMQ, Kubernetes ou event sourcing.
- Não versionar a API.
- Não colocar lógica de negócio em controllers, listeners ou entidades JPA.
- Não hospedar vídeos: o vídeo do dorama é aberto localmente no navegador (`<input type="file">` + blob URL). O servidor guarda só as legendas e os tempos de cada fala.
- Não pular a ordem das fases do `docs/PLAN.md`.
- Não alterar arquivo listado em `protegidos:` da `ficha.md` de uma tarefa.
- Não marcar spec como `aprovada`: só o usuário faz isso.
- Não fazer commit/push sem o usuário pedir.
