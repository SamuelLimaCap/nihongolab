# Testes — Fase 0

Fase de infraestrutura: parte dos cartões é verificação por comando (manual ou no CI), marcada como "Nível: comando".

### C01 — `.env` nunca vai para o git · RN-F0-03
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: comando
- Dado: repo com `.gitignore` do passo 1 e um `.env` criado a partir do `.env.example`
- Quando: `git check-ignore .env`
- Então: imprime `.env` e sai com código 0
- Origem: AGENTS.md (Config) e NFR-SEC-07

### C02 — Postgres e Redis sobem saudáveis e só em localhost · RN-F0-01
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: comando
- Dado: `.env` copiado do exemplo
- Quando: `docker compose --env-file .env -f infra/docker-compose.dev.yml up -d --wait`
- Então: o comando sai com 0; `docker compose ... ps` mostra `postgres` e `redis` como `healthy`; as portas publicadas aparecem como `127.0.0.1:5432` e `127.0.0.1:6379`
- Origem: contrato.md → compose

### C03 — Cada regra de arquitetura falha na sua fixture · RN-F0-07, RN-F0-08, RN-F0-09, RN-F0-11
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: unidade (ArchUnit)
- Dado: fixtures em `src/test/java/dev/nihongolab/archfixture/`:
  - `srs/domain/SpringInDomain` com campo do tipo `org.springframework.context.ApplicationEventPublisher`
  - `srs/application/AdapterInApplication` com campo do tipo `archfixture.srs.adapter.out.persistence.SomeAdapter`
  - `srs/domain/MisplacedEntity` anotada com `@jakarta.persistence.Entity`
  - `srs/application/MisplacedController` anotada com `@RestController`
- Quando: cada regra é checada contra `new ClassFileImporter().importPackages("dev.nihongolab.archfixture")`
- Então: `DOMAIN_IS_PURE`, `APPLICATION_DOES_NOT_DEPEND_ON_ADAPTER`, `ENTITIES_ONLY_IN_PERSISTENCE_ADAPTER` e `CONTROLLERS_ONLY_IN_WEB_ADAPTER` lançam `AssertionError` cuja mensagem contém o nome simples da classe fixture correspondente
- Origem: critério de pronto do PLAN ("o teste de arquitetura falha se você criar um import proibido")

### C03b — Import proibido no código real quebra o build · RN-F0-07
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: comando (verificação manual, uma vez)
- Dado: uma classe temporária `src/main/java/dev/nihongolab/srs/domain/Tmp.java` importando `org.springframework.stereotype.Component`
- Quando: `./mvnw verify`
- Então: o build falha em `ArchitectureTest` citando `DOMAIN_IS_PURE`; ao apagar a classe, volta a passar
- Origem: critério de pronto do PLAN

### C04 — Contexto sobe com Postgres e Redis reais e aplica a V001 · RN-F0-02
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: integração (`IntegrationTest`)
- Dado: Testcontainers com `postgres:16-alpine` e `redis:7-alpine`
- Quando: o contexto Spring sobe
- Então: `select count(*) from flyway_schema_history where version = '1' and success` devolve 1; `select to_regclass('public.event_publication')` não é nulo
- Origem: contrato.md → Migração; D-07

### C05 — Health aberto e resto fechado com 401 · contrato.md → Endpoints
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: integração (`IntegrationTest` com `TestRestTemplate` ou `MockMvc`)
- Dado: nenhuma sessão
- Quando: `GET /actuator/health` e `GET /api/qualquer-coisa`
- Então: health → 200 com corpo `{"status":"UP"}`; `/api/qualquer-coisa` → 401 e sem header `WWW-Authenticate`
- Origem: contrato.md → Endpoints; D-F0-05

### C06 — Estrutura modular válida · RN-F0-10
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: unidade (Spring Modulith)
- Dado: os 6 pacotes de módulo com `package-info.java`
- Quando: `ApplicationModules.of(NihongolabApplication.class).verify()`
- Então: não lança exceção; `new Documenter(modules).writeDocumentation()` gera arquivos em `target/spring-modulith-docs/`
- Origem: AGENTS.md → Regras de dependência

### C07 — App Angular mostra o nome do produto
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: componente (Vitest + TestBed)
- Dado: `App` renderizado
- Quando: o teste consulta o elemento `h1`
- Então: o texto é `Nihongo Lab`
- Origem: contrato.md → Frontend

### C08 — Build de produção do front
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: comando
- Quando: `npm run build` em `frontend/`
- Então: sai com 0 e gera `dist/frontend/browser/index.html`
- Origem: J02

### C09 — CI verde · RN-F0-04, RN-F0-05, RN-F0-06
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: comando (GitHub)
- Dado: repo no GitHub (P-F0-01) com o workflow
- Quando: push na `main`
- Então: os jobs `backend` e `frontend` terminam com sucesso
- Origem: critério de pronto do PLAN

### C10 — Documentação de arquitetura
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: revisão (papel `validar`)
- Dado: `docs/architecture.md` e `docs/adr/0001-monolito-modular-hexagonal.md`
- Então: `architecture.md` tem um bloco Mermaid `C4Context` e um `C4Container` (navegador, Angular/nginx, backend, Postgres, Redis, Google/GitHub OAuth) e a tabela de módulos; o ADR tem as seções Contexto, Decisão e Consequências, com até 15 linhas de conteúdo
- Origem: PLAN Fase 0; AGENTS.md → Definição de pronto 5
