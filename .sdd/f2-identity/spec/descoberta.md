# Descoberta — Fase 2 — Identity + segurança (OAuth2, BFF)

**Semente.** Escrita em 2026-11-20 a partir do `docs/PLAN.md` e da spec do projeto, antes da conversa de descoberta. O papel `descoberta` parte daqui.

## Já se sabe (da spec do projeto e de armadilhas conhecidas)

- Usuário identificado por `(provider, providerSubject)`, nunca por e-mail (RN-ID-01). O GitHub pode não devolver e-mail.
- `UserRegistered` só no primeiro login (RN-ID-02); o `srs` escuta com `@ApplicationModuleListener` e roda `SeedKanaDecks` (idempotente).
- API devolve 401 (não redirect 302) para `/api/**` sem sessão: `defaultAuthenticationEntryPointFor(HttpStatusEntryPoint(UNAUTHORIZED), /api/**)`.
- CSRF para SPA no Spring Security 6.x: `CookieCsrfTokenRepository.withHttpOnlyFalse()` + handler SPA (padrão da documentação do Security 6) + filtro que força o carregamento do token deferido.
- Logout: `POST /api/logout` com `HttpStatusReturningLogoutSuccessHandler(NO_CONTENT)`.
- Em dev, o Angular (4200) faz proxy de `/oauth2` e `/login`; com `changeOrigin: false`, o `redirect-uri` `{baseUrl}/login/oauth2/code/{registrationId}` sai com a origem 4200.
- Rate limit: Bucket4j com Redis (Lettuce), 120 req/min por usuário ou IP (NFR-SEC-05).
- Remover `DevCurrentUser`, `NoSessionCurrentUser`, `DevKanaSeeder` e o modo aberto do `SecurityConfig`. Os testes da Fase 1 que usam `dev-user` precisam de outra forma de autenticar (ex.: `SecurityMockMvcRequestPostProcessors.oauth2Login()` ou sessão de teste). Isso altera arquivos congelados da f1: registrar no `delta.md` e pedir autorização ao usuário.

## A decidir na descoberta

Ver `perguntas.md`. Leia também a seção da fase em `docs/PLAN.md` e as RNs relacionadas em `docs/sdd/dominio.md`.
