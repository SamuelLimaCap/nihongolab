# Fase 2 — Identity + segurança (roteiro)

Spec: `.sdd/f2-identity/` (ainda em descoberta). Este roteiro vira passo a passo quando a spec for aprovada.

## Ordem sugerida

1. `identity` domínio: `User`, `UserRegistered`; migração `V003__identity_user.sql`.
2. Command `RegisterOrFindUser(provider, subject, displayName, email, avatar)`.
3. `OAuth2UserService` (GitHub) e `OidcUserService` (Google) que chamam o command e devolvem um principal com o nosso `UserId`.
4. `SessionCurrentUser implements CurrentUser` lendo o principal do `SecurityContext`. Apagar `DevCurrentUser`, `NoSessionCurrentUser` e `DevKanaSeeder`.
5. `SecurityConfig` BFF (abaixo), `GET /api/me`, `POST /api/logout`.
6. Listener do `srs` para `UserRegistered` → `SeedKanaDecks`.
7. Rate limit com Bucket4j + Redis.
8. Migrar os testes da Fase 1 para autenticar sem `dev-user` (pedir autorização: são arquivos congelados da f1).
9. ADR 0002 (BFF em vez de JWT no navegador).

## Trechos-chave

Configuração do provedor (`application.yml`; segredos por variável de ambiente):

```yaml
spring:
  security:
    oauth2:
      client:
        registration:
          google:
            client-id: ${GOOGLE_CLIENT_ID}
            client-secret: ${GOOGLE_CLIENT_SECRET}
            scope: openid,profile,email
          github:
            client-id: ${GITHUB_CLIENT_ID}
            client-secret: ${GITHUB_CLIENT_SECRET}
            scope: read:user,user:email
server:
  servlet:
    session:
      cookie:
        http-only: true
        same-site: lax
        secure: ${COOKIE_SECURE:false}   # true em prod
```

`SecurityConfig` (esqueleto):

```java
http
    .authorizeHttpRequests(a -> a
        .requestMatchers("/actuator/health", "/actuator/health/**").permitAll()
        .requestMatchers("/oauth2/**", "/login/**").permitAll()
        .requestMatchers("/api/**").authenticated()
        .anyRequest().denyAll())
    .oauth2Login(o -> o
        .userInfoEndpoint(u -> u.userService(githubUserService).oidcUserService(googleUserService))
        .defaultSuccessUrl("/", true))
    .logout(l -> l
        .logoutUrl("/api/logout")
        .logoutSuccessHandler(new HttpStatusReturningLogoutSuccessHandler(HttpStatus.NO_CONTENT)))
    .csrf(c -> c
        .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
        .csrfTokenRequestHandler(new SpaCsrfTokenRequestHandler()))
    .exceptionHandling(e -> e.defaultAuthenticationEntryPointFor(
        new HttpStatusEntryPoint(HttpStatus.UNAUTHORIZED),
        PathPatternRequestMatcher.withDefaults().matcher("/api/**")));
```

`SpaCsrfTokenRequestHandler`: copie da documentação do Spring Security 6.5, seção "Single-Page Applications" (CSRF). Ele aceita o token cru no header (o que o Angular manda) e força o carregamento do token para o cookie ser escrito.

Principal com o nosso ID:

```java
public record NihongolabPrincipal(UserId userId, String name, Map<String, Object> attributes,
                                  Collection<? extends GrantedAuthority> authorities)
        implements OAuth2User, Serializable { /* getName(), getAttributes(), getAuthorities() */ }
```

Para o Google (OIDC), implemente também `OidcUser` (ou crie um segundo principal).

## Armadilhas

- **GitHub sem e-mail:** o e-mail pode vir nulo. Identifique por `(provider, id)` (RN-ID-01).
- **Serialização da sessão:** o Spring Session guarda o `SecurityContext` no Redis com serialização Java. O principal e tudo dentro dele precisam ser `Serializable`.
- **302 em vez de 401:** sem o `defaultAuthenticationEntryPointFor`, `/api/**` sem sessão redireciona para a página de login.
- **Redirect URI em dev:** o login começa em `localhost:4200` (proxy). Com `changeOrigin: false`, o `{baseUrl}` vira `http://localhost:4200`. Cadastre esse redirect no Google e no GitHub, além do de prod.
- **CSRF no primeiro POST:** o cookie `XSRF-TOKEN` só existe depois de uma requisição. O front chama `/api/me` ao iniciar.
- **Listener e outbox:** `@ApplicationModuleListener` é assíncrono. No teste, espere o efeito (Modulith `Scenario` ou Awaitility) antes de conferir.

## Testes que a spec vai pedir (prévia)

- 401 em `/api/**` sem sessão; 403 em POST sem CSRF; 204 no logout.
- Usuário A não lê deck nem revisa cartão de B (404).
- Primeiro login cria usuário, publica `UserRegistered`, cria os decks de kana e a linha em `event_publication` fica com `completion_date` preenchido.
- Segundo login não publica evento.
- 121ª requisição no minuto → 429 com `Retry-After`.

No MockMvc: `.with(oauth2Login().oauth2User(principal))` e `.with(csrf())` do `spring-security-test`.
