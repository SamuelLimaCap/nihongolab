# Descoberta — Fase 8 — Infra de produção + observabilidade

**Semente.** Escrita em 2026-11-20 a partir do `docs/PLAN.md` e da spec do projeto, antes da conversa de descoberta. O papel `descoberta` parte daqui.

## Já se sabe (da spec do projeto e de armadilhas conhecidas)

- Backend: `eclipse-temurin:21-jre`, usuário sem root, `-XX:MaxRAMPercentage=75`, camadas com `java -Djarmode=tools -jar app.jar extract --layers --launcher`.
- Build `linux/arm64` com `docker buildx`.
- CSP precisa de `media-src 'self' blob:` (vídeo local) e fontes self-hosted (NFR-SEC-08).
- Sem cache em `index.html`, `ngsw.json`, `ngsw-worker.js`; cache imutável nos assets com hash.
- Actuator numa porta de management interna (NFR-SEC-09).
- Reavaliar Spring Boot 4.x antes do deploy (D-01).

## A decidir na descoberta

Ver `perguntas.md`. Leia também a seção da fase em `docs/PLAN.md` e as RNs relacionadas em `docs/sdd/dominio.md`.
