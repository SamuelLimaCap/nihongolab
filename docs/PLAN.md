# Plano de implementação

Cada fase termina com tudo verde, um commit por tarefa e uma revisão do agente `reviewer`. Não comece uma fase antes de terminar a anterior.

Agentes (`.claude/agents/`): `architect`, `backend`, `frontend`, `devops`, `reviewer`.

No método SDD, esses agentes viram papéis (ver `docs/sdd/README.md` → "Papéis do PLAN × papéis do SDD"). Cada fase tem uma tarefa em `.sdd/f<N>-<nome>/`.

---

## Fase 0: Fundação

**Agentes:** architect → devops → backend → frontend

- [ ] Monorepo com `backend/`, `frontend/`, `infra/`, `docs/`.
- [ ] `infra/docker-compose.dev.yml`: Postgres 16 e Redis 7 (imagens multi-arch), com healthchecks.
- [ ] Backend: Spring Boot 3 + Java 21 + Maven wrapper. Dependências: web, validation, data-jpa, flyway, postgresql, data-redis, session-data-redis, security, oauth2-client, actuator, micrometer-registry-prometheus, spring-modulith (starter-core, starter-jpa, events-jdbc), archunit-junit5, testcontainers (postgresql, junit-jupiter), `com.redis:testcontainers-redis`.
- [ ] Pacotes vazios dos módulos (`srs`, `grammar`, `media`, `progress`, `identity`, `shared`) com `package-info.java` (`@ApplicationModule`).
- [ ] Testes de arquitetura: `ApplicationModules.of(App.class).verify()` e regras ArchUnit de camadas (ver `CLAUDE.md`).
- [ ] Classe base de teste de integração com Testcontainers (Postgres + Redis) via `@ServiceConnection`.
- [ ] Frontend: Angular com standalone components, roteamento, SCSS e proxy `/api` → `:8080`.
- [ ] CI (`.github/workflows/ci.yml`): `./mvnw verify` e `npm ci && npm test && npm run build`.
- [ ] `docs/architecture.md` com um diagrama C4 (contexto + containers) em Mermaid, e o ADR 0001 (monólito modular + hexagonal).

**Pronto quando:** o CI está verde e o teste de arquitetura falha se você criar um import proibido de propósito.

---

## Fase 1: Domínio SRS + Kana

**Agentes:** backend → reviewer

Domínio (`srs/domain`), Java puro:
- [ ] VOs: `CardId`, `DeckId`, `UserId` (vem do shared), `Grade` (enum `AGAIN`, `HARD`, `GOOD`, `EASY`), `SchedulingState` (intervalo, ease factor, repetições, `dueAt`).
- [ ] Aggregate `Card`: frente, verso, leitura, exemplo, fonte (`MANUAL`, `KANA`, `SUBTITLE` + referência), estado de agendamento. Método `review(Grade, Instant now, Scheduler)` que gera o evento `CardReviewed(cardId, userId, grade, reviewedAt, newDueAt)`.
- [ ] Interface `Scheduler` com uma implementação `Sm2Scheduler`, já pensando em trocar por FSRS depois.
- [ ] Aggregate `Deck` com nome e dono. Cartões referenciam o deck pelo ID.
- [ ] Testes de unidade do SM-2 (tabela de casos) e das invariantes do `Card`.

Aplicação e adapters:
- [ ] Commands: `CreateDeck`, `CreateCard`, `ReviewCard` (idempotente por `reviewId` UUID gerado no cliente, para o sync offline).
- [ ] Queries: `DueCardsQuery` (cartões vencidos por deck), `DeckSummaryQuery`, com `JdbcClient`.
- [ ] Persistência JPA + `V001__srs_init.sql` (`srs_deck`, `srs_card`, `srs_review`).
- [ ] REST: `POST /api/decks`, `GET /api/decks`, `POST /api/decks/{id}/cards`, `GET /api/review/due`, `POST /api/review`.
- [ ] Seed dos decks de Hiragana e Katakana (migração `V002__srs_kana_seed.sql` ou carga de JSON no primeiro login).

**Pronto quando:** há testes de integração que criam um deck, revisam um cartão e conferem o novo `dueAt` e a gravação do evento na tabela de publicação.

---

## Fase 2: Identity + segurança (OAuth2, padrão BFF)

**Agentes:** backend → reviewer

- [ ] Login OAuth2 com Google e GitHub (`spring-boot-starter-oauth2-client`). Endpoints `/oauth2/authorization/{provider}`.
- [ ] No primeiro login, cria o `User` (módulo `identity`) e publica `UserRegistered`. O `srs` escuta e cria os decks de kana.
- [ ] Spring Session com Redis. Cookie `HttpOnly`, `Secure` (em prod) e `SameSite=Lax`.
- [ ] CSRF com `CookieCsrfTokenRepository.withHttpOnlyFalse()` e handler compatível com SPA.
- [ ] `GET /api/me` e `POST /api/logout`.
- [ ] Toda query e command recebe o `UserId` da sessão. Teste garantindo que um usuário não acessa o deck de outro.
- [ ] Rate limiting em `/api/**` (Bucket4j com Redis), devolvendo 429 com `ProblemDetail`.
- [ ] ADR 0002: por que BFF em vez de JWT no navegador.

**Pronto quando:** a rota protegida retorna 401 sem sessão, o teste de acesso entre usuários passa e o POST sem CSRF retorna 403.

---

## Fase 3: Frontend base

**Agentes:** frontend → reviewer

Referência visual: o layout dark mode (desktop com menu lateral, mobile com barra de abas no rodapé).
- [ ] Tema dark com design tokens em CSS custom properties (fundo `#0f1115`, superfície `#171a21`, borda `#262a33`, texto `#e7e9ee`, texto secundário `#9aa1ad`, destaque `#ff7a70`). Fontes Inter e Noto Sans JP.
- [ ] Shell responsivo: menu lateral a partir de 768px e barra de abas abaixo disso. Áreas de toque de pelo menos 44px.
- [ ] `AuthService` com signals (`/api/me`), guard de rota, interceptor HTTP (`withCredentials`, XSRF), tela de login com os botões Google/GitHub.
- [ ] Tela de **Revisão**: frente → mostrar resposta → botões Errei/Difícil/Bom/Fácil, com atalhos de teclado 1–4 e espaço.
- [ ] Tela de **Kana**: tabela e quiz.
- [ ] Tela **Início**: cards pendentes e atalhos.
- [ ] Testes de componente das telas de Revisão e Início.

**Pronto quando:** dá pra logar, revisar kana no celular e no desktop, e os testes passam.

---

## Fase 4: Mídia (legendas + processamento assíncrono)

**Agentes:** backend → frontend → reviewer

- [ ] `POST /api/media/subtitles` (multipart `.srt` + título do dorama + episódio). Faz o parse do SRT (índice, tempo inicial e final, texto), limpa tags `<v ...>`, `➡`, indicações de quem fala e sons, salva as `SubtitleLine` com status `PENDING` e publica `SubtitleImported`.
- [ ] Listener assíncrono (`@ApplicationModuleListener`) tokeniza com o `TokenizerPort` (adapter Kuromoji): forma base, leitura e classe gramatical. Publica `SubtitleTokenized`. Status `PROCESSING` → `DONE`/`FAILED`.
- [ ] Query: linhas do episódio com tokens e palavras "novas" (que não estão nos cartões do usuário).
- [ ] Command no `srs`: `CreateCardFromSentence(lineId, token)`. O cartão guarda a frase como exemplo e a referência (episódio + tempo).
- [ ] Front: upload, acompanhamento de status (polling), **player** com o vídeo local (`<input type="file">` → `URL.createObjectURL`) sincronizado com a legenda, clique na palavra para criar o cartão.
- [ ] Teste de integração com um `.srt` de exemplo em `src/test/resources`.

**Pronto quando:** enviar um `.srt` deixa o status em `DONE`, as palavras ficam clicáveis e o cartão criado aparece na revisão.

---

## Fase 5: Gramática

**Agentes:** backend → frontend

- [ ] Domínio: `Lesson` (nível JLPT, título, explicação, `GrammarPoint`s com padrão, significado e exemplos).
- [ ] Conteúdo inicial em `backend/src/main/resources/content/grammar/*.json` (N5 e N4 primeiro), carregado por migração ou por um loader idempotente.
- [ ] Exemplos podem apontar para linhas de legenda do usuário que contenham o padrão (busca por texto).
- [ ] Cache com Redis (`@Cacheable`) nas queries de lições.
- [ ] Concluir uma lição publica `LessonCompleted`.
- [ ] Front: lista por nível, tela da lição e botão "criar cartões dos exemplos".

---

## Fase 6: Progresso (CQRS) + export/import

**Agentes:** backend → frontend → reviewer

- [ ] Read models: `progress_daily_stats` (revisões e acertos por dia), `progress_streak` e `progress_level` (% por nível JLPT). São atualizados por listeners de `CardReviewed`, `CardCreated` e `LessonCompleted`, todos idempotentes (guardam o ID do evento processado).
- [ ] Query do painel inicial: sequência de dias, total de palavras, revisões pendentes e % por nível.
- [ ] **Export:** `GET /api/progress/export` → JSON `{ "schemaVersion": 1, "exportedAt", "decks", "cards", "reviews", "lessonsCompleted", "subtitles" }`, sem dados de outros usuários.
- [ ] **Import:** `POST /api/progress/import` valida o `schemaVersion`, roda tudo numa transação só e faz upsert por UUID. Depois recalcula os read models.
- [ ] Export em CSV compatível com o Anki (frente;verso;tags).
- [ ] Teste: exportar → apagar → importar → o estado é igual ao original.
- [ ] Front: card "Backup do progresso" (Exportar/Importar) e o painel de progresso.

---

## Fase 7: PWA offline

**Agentes:** frontend → backend → reviewer

- [ ] `@angular/pwa`: service worker com cache do app e das lições (estratégia `freshness` para a API e `performance` para os assets).
- [ ] IndexedDB (Dexie): cache dos cartões vencidos e uma fila de revisões feitas offline, cada uma com `reviewId` UUID.
- [ ] Sincronização ao reconectar: `POST /api/review/batch`, idempotente por `reviewId`, que resolve conflitos pela ordem de `reviewedAt`.
- [ ] Indicador visual de offline/sincronizando.
- [ ] Teste e2e (Playwright): ficar offline, revisar 3 cartões, voltar online e conferir que o servidor registrou as 3 revisões.

---

## Fase 8: Infra de produção + observabilidade

**Agentes:** devops → reviewer

- [ ] `infra/docker-compose.yml` com perfis:
  - `core`: nginx, backend, postgres, redis
  - `full`: core + prometheus, grafana, loki, promtail
- [ ] Dockerfiles multi-stage em ARM64: backend (Temurin 21 JRE, usuário sem root, `-XX:MaxRAMPercentage=75`) e frontend (build Angular → arquivos estáticos copiados para o nginx).
- [ ] Nginx: serve o Angular (fallback de SPA para `index.html`), proxy de `/api`, `/oauth2` e `/login` para o backend, gzip/brotli, `Cache-Control` imutável nos assets com hash e **sem cache** em `ngsw.json`, `ngsw-worker.js` e `index.html`. Também os headers de segurança (CSP, HSTS, X-Content-Type-Options).
- [ ] TLS com Let's Encrypt (container certbot + renovação) ou Cloudflare na frente.
- [ ] Observabilidade: Actuator (`health`, `prometheus`) exposto **só na rede interna**, Prometheus coletando as métricas do backend, logs JSON enviados ao Loki, e um dashboard do Grafana provisionado como código (JVM, HTTP p95, erros, eventos pendentes no outbox, revisões por dia).
- [ ] Limites de memória por container (`mem_limit`), que cabem em 12 GB com folga.
- [ ] Backup: `pg_dump` diário via cron num container, com retenção de 7 dias, mais o export JSON da Fase 6.
- [ ] Deploy (`.github/workflows/deploy.yml`): build das imagens arm64 → GHCR → SSH na VPS → `docker compose pull && up -d`. Segredos no GitHub Secrets.
- [ ] `docs/deploy.md`: passo a passo da VPS (Oracle) e das alternativas.

**Pronto quando:** o app está no ar com HTTPS, o dashboard do Grafana mostra as métricas e um restore do backup foi testado.

---

## Fase 9: Polimento para o portfólio

**Agentes:** reviewer → architect

- [ ] Testes de mutação com PIT no domínio (`srs`, `progress`), mirando mais de 70% de mutantes mortos.
- [ ] Testes e2e com Playwright dos fluxos principais: login (mock), revisão, upload de `.srt` → criar cartão, export/import.
- [ ] README: o que é, um GIF, diagrama C4, lista de ADRs, como rodar em 1 comando e link do deploy.
- [ ] Revisar se todo ADR reflete o que foi implementado.

---

## Hospedagem: plano B (resumo, detalhes em `docs/deploy.md`)

O app precisa rodar em 2 modos, configurados por variáveis de ambiente:
- **VPS** (Oracle ou outra): tudo via Docker Compose.
- **Gerenciado/fragmentado:** Postgres externo (Neon ou Supabase), Redis externo (Upstash), backend num host de container e front estático (Cloudflare Pages). Para esse modo:
  - nenhuma dependência de rede interna do compose
  - `SPRING_DATASOURCE_URL` e `SPRING_DATA_REDIS_URL` configuráveis
  - backend funcionando com 512 MB (`-Xmx300m`, perfil `slim` sem o stack de observabilidade)
