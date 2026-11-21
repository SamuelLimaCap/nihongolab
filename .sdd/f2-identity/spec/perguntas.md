# Perguntas — Fase 2 — Identity + segurança (OAuth2, BFF)

### P-F2-01 — Quais provedores no primeiro deploy?
- Contexto: Os dois exigem cadastrar app OAuth com o redirect de dev e de prod.
- Recomendação: Google e GitHub, como no PLAN.
- Quem decide: usuário
- Status: aberta

### P-F2-02 — Como autenticar nos testes de integração depois de remover o `dev-user`?
- Contexto: Afeta testes congelados da f1.
- Recomendação: `oauth2Login()` do `spring-security-test` no MockMvc; para `TestRestTemplate`, sessão criada por um helper de teste.
- Quem decide: usuário
- Status: aberta
