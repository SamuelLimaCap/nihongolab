# Plano — Fase 0: Fundação

## Visão

Ao final, `git clone` + `.env` + um comando sobe Postgres e Redis; `./mvnw verify` e `npm test` passam; o CI roda os dois; e um import proibido quebra o build.

## Passo 1 — Base do monorepo (S)
- Objetivo: repo git com a estrutura de pastas e arquivos de configuração comuns.
- Entregáveis: `git init`, `.gitignore` (Java, Node, IDE, `.env`), `.editorconfig`, `.env.example`, `README.md` mínimo.
- Depende de: —
- Testes que cobrem: C01
- Pronto quando: `git status` limpo depois do primeiro commit e `.env` ignorado.
- Especialidade: devops
- Status: implementado

## Passo 2 — Postgres e Redis de desenvolvimento (S)
- Objetivo: subir dependências locais com healthcheck.
- Entregáveis: `infra/docker-compose.dev.yml`.
- Depende de: 1
- Testes que cobrem: C02
- Pronto quando: os dois serviços ficam `healthy`.
- Especialidade: devops
- Status: implementado

## Passo 3 — Esqueleto do backend (M)
- Objetivo: app Spring Boot que sobe, com os módulos vazios e a segurança mínima.
- Entregáveis: `backend/pom.xml`, Maven wrapper, `NihongolabApplication`, `application.yml`, `package-info.java` dos 6 módulos e das named interfaces, `SecurityConfig`, bean `Clock`.
- Depende de: 1
- Testes que cobrem: C04, C05
- Pronto quando: `./mvnw verify` passa.
- Especialidade: backend
- Status: implementado

## Passo 4 — Outbox e base de teste de integração (S)
- Objetivo: tabela do outbox via Flyway e base de teste com Postgres e Redis reais.
- Entregáveis: `V001__shared_event_publication.sql`, `TestcontainersConfiguration`, `IntegrationTest` (classe base).
- Depende de: 3
- Testes que cobrem: C04, C05
- Pronto quando: o teste de contexto sobe com os containers e o Flyway aplica a V001.
- Especialidade: backend
- Status: implementado

## Passo 5 — Guardiões de arquitetura (M)
- Objetivo: build falha se alguém quebrar as regras de camada ou de módulo.
- Entregáveis: `ArchitectureRules` (regras como constantes), `ArchitectureTest`, `ArchitectureRulesSelfTest` com fixture proibida em `src/test`, `ModularityTest`.
- Depende de: 3
- Testes que cobrem: C03, C06
- Pronto quando: as regras passam no código real e falham na fixture.
- Especialidade: backend
- Status: implementado

## Passo 6 — Esqueleto do frontend (S)
- Objetivo: app Angular 22 que compila, testa e encaminha `/api` para o backend.
- Entregáveis: `frontend/` via `ng new`, `proxy.conf.json`, script `start` com proxy, um teste do `App`.
- Depende de: 1
- Testes que cobrem: C07, C08
- Pronto quando: `npm test -- --watch=false` e `npm run build` passam.
- Especialidade: frontend
- Status: pendente

## Passo 7 — CI (S)
- Objetivo: todo push e PR roda os testes do back e do front.
- Entregáveis: `.github/workflows/ci.yml` com jobs `backend` e `frontend`.
- Depende de: 3, 6 (paralelizável com 8)
- Testes que cobrem: C09
- Pronto quando: o workflow fica verde no GitHub.
- Especialidade: devops
- Status: pendente

## Passo 8 — Documentação de arquitetura (S)
- Objetivo: registrar a arquitetura e a primeira decisão.
- Entregáveis: `docs/architecture.md` (C4 contexto + containers em Mermaid, módulos e regras), `docs/adr/0001-monolito-modular-hexagonal.md`.
- Depende de: 3 (paralelizável com 7)
- Testes que cobrem: C10
- Pronto quando: os diagramas renderizam no GitHub e o ADR tem contexto, decisão e consequências em até 15 linhas.
- Especialidade: architect
- Status: pendente
