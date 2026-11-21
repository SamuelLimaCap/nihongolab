# Perguntas — Fase 8 — Infra de produção + observabilidade

### P-01 — Promtail ou Grafana Alloy? (projeto)
- Recomendação: Alloy. Ver `docs/sdd/decisoes.md`.
- Quem decide: usuário
- Status: aberta

### P-F8-01 — Domínio e TLS: certbot ou Cloudflare na frente?
- Recomendação: Cloudflare (proxy) + certificado de origem, se o domínio estiver lá.
- Quem decide: usuário
- Status: aberta

### P-F8-02 — VPS: Oracle Free (ARM) confirmada?
- Recomendação: Sim, com o plano B gerenciado documentado.
- Quem decide: usuário
- Status: aberta
