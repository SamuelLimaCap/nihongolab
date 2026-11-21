# J01 — Dev sobe o ambiente local

- Objetivo: em um clone novo, rodar backend e frontend contra Postgres e Redis locais.
- Ator: desenvolvedor (humano ou agente).
- Pré-condições: Docker, JDK 21 e Node 24 instalados (`docs/guia/00-ambiente.md`).

## Fluxo principal

```fluxo
cp .env.example .env                      → variáveis locais (nunca commitadas)
docker compose --env-file .env -f infra/docker-compose.dev.yml up -d
                                          → postgres:16 e redis:7 sobem e ficam healthy
cd backend && set -a && . ../.env && set +a && ./mvnw spring-boot:run
                                          → Flyway aplica V001; app em :8080
curl localhost:8080/actuator/health       → {"status":"UP"}
cd frontend && npm ci && npm start        → app em :4200; /api, /oauth2 e /login vão para :8080
```

## Regras

- RN-F0-01: Postgres e Redis só escutam em `127.0.0.1`.
- RN-F0-02: o backend lê conexão de `SPRING_DATASOURCE_URL`, `SPRING_DATASOURCE_USERNAME`, `SPRING_DATASOURCE_PASSWORD` e `SPRING_DATA_REDIS_URL`.
- RN-F0-03: `.env` está no `.gitignore`; `.env.example` lista todas as variáveis, sem valor secreto real.

## Erros

- Postgres fora do ar: o backend falha ao subir com erro de conexão (comportamento padrão do Boot; não mascarar).
- `.env` ausente: o compose falha dizendo que falta o arquivo.

## Fora de escopo

- Stack prod-like (`infra/docker-compose.yml`), que é da Fase 8.
