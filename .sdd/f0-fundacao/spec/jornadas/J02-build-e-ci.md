# J02 — Build local e CI

- Objetivo: qualquer mudança é testada igual na máquina e no GitHub.
- Ator: desenvolvedor; GitHub Actions.
- Pré-condições: Docker disponível (Testcontainers).

## Fluxo principal

```fluxo
cd backend && ./mvnw verify              → unidade + integração (Testcontainers) + ArchUnit + Modulith
cd frontend && npm test -- --watch=false → testes Vitest
cd frontend && npm run build             → build de produção
git push / PR                            → workflow "ci": jobs backend e frontend em paralelo
```

## Regras

- RN-F0-04: o job `backend` roda `./mvnw -B verify` em `backend/` com Temurin 21 e cache do Maven.
- RN-F0-05: o job `frontend` roda `npm ci`, `npm test -- --watch=false` e `npm run build` em `frontend/` com Node 24 e cache do npm.
- RN-F0-06: o workflow roda em `push` para `main` e em todo `pull_request`.

## Fora de escopo

- Build de imagens e deploy (Fase 8).
