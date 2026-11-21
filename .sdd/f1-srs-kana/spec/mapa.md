# Mapa — Fase 1

**Provisório.** Escrito em 2026-11-20, antes da Fase 0 existir no repo. Descreve o que o contrato da f0 promete. O papel `mapa` precisa confirmar cada linha com `caminho:linha` reais quando a f0 estiver concluída, e só então a spec pode ser aprovada.

## Esperado da Fase 0

| O quê | Onde (esperado) | Uso na Fase 1 |
|---|---|---|
| Classe principal com `@EnableAsync` | `backend/src/main/java/dev/nihongolab/NihongolabApplication.java` | — |
| Bean `Clock` UTC | pacote raiz | injetado nos commands; substituído por `Clock.fixed` nos testes |
| `package-info.java` do `srs`, `identity`, `shared` | `backend/src/main/java/dev/nihongolab/<modulo>/` | novos subpacotes `api` e `domain/event` ganham named interface |
| `SecurityConfig` | `identity/adapter/in/web/SecurityConfig.java` | ganha o modo `dev-user` |
| `V001__shared_event_publication.sql` | `backend/src/main/resources/db/migration/` | próxima migração é `V002` |
| `IntegrationTest` + `TestcontainersConfiguration` | `backend/src/test/java/dev/nihongolab/` | base dos testes de integração |
| `ArchitectureRules` | `backend/src/test/java/dev/nihongolab/architecture/` | regras valem para todo o código novo |

## Buracos

- Confirmar nomes reais das classes e propriedades depois da f0.
