# Contrato — Fase 0

## Variáveis de ambiente (`.env.example`)

```dotenv
POSTGRES_DB=nihongolab
POSTGRES_USER=nihongolab
POSTGRES_PASSWORD=troque-me
SPRING_DATASOURCE_URL=jdbc:postgresql://localhost:5432/nihongolab
SPRING_DATASOURCE_USERNAME=nihongolab
SPRING_DATASOURCE_PASSWORD=troque-me
SPRING_DATA_REDIS_URL=redis://localhost:6379
```

## `infra/docker-compose.dev.yml`

| Serviço | Imagem | Porta | Healthcheck | Volume |
|---|---|---|---|---|
| `postgres` | `postgres:16-alpine` | `127.0.0.1:5432:5432` | `pg_isready -U $POSTGRES_USER -d $POSTGRES_DB` | `pgdata` |
| `redis` | `redis:7-alpine` | `127.0.0.1:6379:6379` | `redis-cli ping` | — |

Imagens oficiais multi-arch (amd64 e arm64).

## Backend

- Coordenadas Maven: `dev.nihongolab:nihongolab-backend`, parent `spring-boot-starter-parent` 3.5.x.
- Classe principal: `dev.nihongolab.NihongolabApplication` com `@SpringBootApplication` e `@EnableAsync`.
- Bean `Clock` = `Clock.tickMillis(ZoneOffset.UTC)` em `dev.nihongolab.NihongolabApplication` ou numa `@Configuration` no pacote raiz. Precisão de milissegundos: o Postgres guarda microssegundos, e um `Instant` com nanossegundos mudaria na ida e volta ao banco.

### Pacotes e `package-info.java`

| Pacote | Anotação |
|---|---|
| `dev.nihongolab.shared` | `@ApplicationModule(displayName = "Shared Kernel", type = ApplicationModule.Type.OPEN)` |
| `dev.nihongolab.srs` | `@ApplicationModule(displayName = "SRS")` |
| `dev.nihongolab.grammar` | `@ApplicationModule(displayName = "Grammar")` |
| `dev.nihongolab.media` | `@ApplicationModule(displayName = "Media")` |
| `dev.nihongolab.progress` | `@ApplicationModule(displayName = "Progress")` |
| `dev.nihongolab.identity` | `@ApplicationModule(displayName = "Identity")` |

`<modulo>/api` e `<modulo>/domain/event` ganham `package-info.java` com `@NamedInterface("api")` e `@NamedInterface("events")` quando o primeiro tipo for criado neles (Fase 1 em diante).

### `application.yml` (chaves obrigatórias)

| Chave | Valor |
|---|---|
| `spring.application.name` | `nihongolab` |
| `spring.jpa.open-in-view` | `false` |
| `spring.jpa.hibernate.ddl-auto` | `validate` |
| `spring.flyway.enabled` | `true` |
| `spring.modulith.events.jdbc.schema-initialization.enabled` | `false` |
| `spring.modulith.events.republish-outstanding-events-on-restart` | `true` |
| `spring.threads.virtual.enabled` | `true` |
| `spring.mvc.problemdetails.enabled` | `true` |
| `management.endpoints.web.exposure.include` | `health,info,prometheus` |
| `management.endpoint.health.show-details` | `never` |
| `logging.structured.format.console` | `ecs` |

Nenhuma credencial no arquivo: conexão vem das variáveis `SPRING_*` (dev e prod) ou do `@ServiceConnection` (testes).

### Endpoints

| Método e caminho | Sem sessão | Corpo |
|---|---|---|
| `GET /actuator/health` | 200 | `{"status":"UP"}` |
| Qualquer outro | 401 | vazio; sem header `WWW-Authenticate: Basic` |

Segurança (`dev.nihongolab.identity.adapter.in.web.SecurityConfig`): `/actuator/health/**` liberado; resto `authenticated()`; `httpBasic` e `formLogin` desligados; entry point `HttpStatusEntryPoint(UNAUTHORIZED)`.

### Migração

`backend/src/main/resources/db/migration/V001__shared_event_publication.sql`, DDL em `docs/sdd/dados.md`.

### Testes de infraestrutura

| Classe (em `src/test/java/dev/nihongolab/`) | Papel |
|---|---|
| `TestcontainersConfiguration` | `@TestConfiguration(proxyBeanMethods = false)` com `@Bean @ServiceConnection PostgreSQLContainer<?>` (`postgres:16-alpine`) e `@Bean @ServiceConnection RedisContainer` (`redis:7-alpine`) |
| `IntegrationTest` | classe base abstrata: `@SpringBootTest(webEnvironment = RANDOM_PORT)` + `@Import(TestcontainersConfiguration.class)` |
| `architecture/ArchitectureRules` | regras como `public static final ArchRule` |
| `architecture/ArchitectureTest` | `@AnalyzeClasses(packages = "dev.nihongolab", importOptions = DoNotIncludeTests.class)` aplicando todas as regras |
| `architecture/ArchitectureRulesSelfTest` | aplica cada regra nas fixtures e espera `AssertionError` |
| `archfixture/...` | classes que violam de propósito (só em `src/test`) |
| `architecture/ModularityTest` | `ApplicationModules.of(NihongolabApplication.class).verify()` e `Documenter` |

### Regras de arquitetura (`ArchitectureRules`)

| Constante | Regra |
|---|---|
| `DOMAIN_IS_PURE` | classes em `..domain..` (exceto `package-info`) não dependem de `org.springframework..`, `jakarta.persistence..`, `com.fasterxml..`, `..application..`, `..adapter..` |
| `APPLICATION_DOES_NOT_DEPEND_ON_ADAPTER` | classes em `..application..` não dependem de `..adapter..` |
| `ENTITIES_ONLY_IN_PERSISTENCE_ADAPTER` | classes anotadas com `@jakarta.persistence.Entity` residem em `..adapter.out.persistence..` |
| `CONTROLLERS_ONLY_IN_WEB_ADAPTER` | classes anotadas com `@RestController` residem em `..adapter.in.web..` |

Todas com `.allowEmptyShould(true)`.

## Frontend

- Criado com `ng new frontend --routing --style=scss --ssr=false --skip-git`.
- `proxy.conf.json`: `/api`, `/oauth2`, `/login` → `http://localhost:8080`, `secure: false`, `changeOrigin: false`.
- `package.json` → `"start": "ng serve --proxy-config proxy.conf.json"`.
- O `App` mostra o título "Nihongo Lab".

## CI (`.github/workflows/ci.yml`)

| Job | Diretório | Passos |
|---|---|---|
| `backend` | `backend/` | `actions/checkout`, `actions/setup-java` (temurin 21, cache maven), `./mvnw -B verify` |
| `frontend` | `frontend/` | `actions/checkout`, `actions/setup-node` (24, cache npm, `cache-dependency-path: frontend/package-lock.json`), `npm ci`, `npm test -- --watch=false`, `npm run build` |

Gatilhos: `push` em `main`, `pull_request`.

## Eventos

Nenhum.
