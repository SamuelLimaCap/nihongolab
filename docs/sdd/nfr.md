# Requisitos não funcionais

Cada item tem um ID. As specs de fase citam o ID quando um teste cobre o requisito.

## Segurança

- **NFR-SEC-01** Toda query e todo command filtram pelo `UserId` autenticado. Teste de acesso cruzado entre dois usuários em cada fase que cria endpoint (a partir da Fase 2).
- **NFR-SEC-02** Recurso de outro usuário responde 404, nunca 403.
- **NFR-SEC-03** Sessão só em cookie `HttpOnly`, `Secure` (prod), `SameSite=Lax`. Nada de token no `localStorage`/`sessionStorage`.
- **NFR-SEC-04** CSRF ativo em todo método que muda estado. Cookie `XSRF-TOKEN`, header `X-XSRF-TOKEN`.
- **NFR-SEC-05** Rate limit em `/api/**` (Fase 2): 120 requisições por minuto por usuário (ou por IP sem sessão). Excedeu: 429 `rate-limited` com `Retry-After`.
- **NFR-SEC-06** Upload: `.srt` até 2 MB; multipart total até 3 MB.
- **NFR-SEC-07** Nenhum segredo no repositório. `.env` no `.gitignore`; `.env.example` atualizado.
- **NFR-SEC-08** Headers em prod (Fase 8): CSP (com `media-src 'self' blob:` para o vídeo local), HSTS, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`.
- **NFR-SEC-09** Actuator só na rede interna (porta de management separada, não publicada pelo nginx).

## Desempenho

- **NFR-PERF-01** `GET /api/review/due` e `POST /api/review`: p95 < 150 ms com 10 mil cartões por usuário, medido no ambiente de prod.
- **NFR-PERF-02** Tokenizar um episódio de 1.000 falas: < 30 s.
- **NFR-PERF-03** Primeira carga do front (rede 4G simulada): LCP < 2,5 s. Bundle inicial < 300 kB gzip, sem contar fontes.

## Recursos

- **NFR-RES-01** Stack `full` cabe em 12 GB com folga (soma de `mem_limit` ≤ 8 GB).
- **NFR-RES-02** Modo `slim` (plano B): backend funciona com 512 MB de container (`-Xmx300m`), sem observabilidade.
- **NFR-RES-03** Todas as imagens com build `linux/arm64`.

## Confiabilidade

- **NFR-REL-01** Nenhum evento perdido se a app cair (outbox do Modulith).
- **NFR-REL-02** Listeners idempotentes (ver `eventos.md`).
- **NFR-REL-03** Backup diário do Postgres com retenção de 7 dias; restore testado (Fase 8).
- **NFR-REL-04** Revisões feitas offline nunca se perdem nem duplicam (Fase 7).

## Observabilidade

- **NFR-OBS-01** Logs JSON (ECS) com `traceId` e `userId` no MDC.
- **NFR-OBS-02** Métricas Prometheus: JVM, HTTP (p95 por rota), erros, publicações pendentes no outbox, revisões por dia.
- **NFR-OBS-03** Dashboard do Grafana versionado no repo.

## Usabilidade

- **NFR-UX-01** Tema escuro com os tokens de cor do PLAN (Fase 3).
- **NFR-UX-02** Layout: menu lateral a partir de 768 px; barra de abas abaixo disso. Áreas de toque ≥ 44 px.
- **NFR-UX-03** Revisão inteira por teclado: espaço mostra a resposta; 1–4 escolhem a nota.
- **NFR-UX-04** Contraste WCAG AA no texto.
- **NFR-UX-05** Interface em português; conteúdo de estudo em japonês com Noto Sans JP.

## Compatibilidade

- **NFR-COMP-01** Navegadores: as duas últimas versões de Chrome, Firefox e Safari (inclusive iOS).
- **NFR-COMP-02** Vídeo local: formatos que o navegador toca (MP4/H.264, WebM). MKV não é garantido.

## Qualidade

- **NFR-QA-01** `./mvnw verify` e `npm test` verdes em todo commit da `main`.
- **NFR-QA-02** Testes de mutação (PIT) no domínio de `srs` e `progress`: > 70% de mutantes mortos (Fase 9).
- **NFR-QA-03** ArchUnit e `ApplicationModules.verify()` rodam em todo build.
