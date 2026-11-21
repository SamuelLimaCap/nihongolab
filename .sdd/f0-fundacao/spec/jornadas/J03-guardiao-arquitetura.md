# J03 — Build barra violação de arquitetura

- Objetivo: nenhuma violação das regras de camada ou de módulo chega à `main`.
- Ator: desenvolvedor ou agente que escreve código fora da regra.

## Fluxo principal

```fluxo
dev cria classe em srs/domain importando org.springframework...
./mvnw verify                 → ArchitectureTest falha com a regra DOMAIN_IS_PURE e o nome da classe
dev remove o import           → verify passa
```

## Regras (detalhadas em `contrato.md` → "Regras de arquitetura")

- RN-F0-07: `domain` não depende de Spring, JPA, Jackson, `application` nem `adapter`.
- RN-F0-08: `application` não depende de `adapter`.
- RN-F0-09: `@Entity` só em `..adapter.out.persistence..`; `@RestController` só em `..adapter.in.web..`.
- RN-F0-10: `ApplicationModules.verify()` passa (sem ciclo e sem acesso a pacote interno de outro módulo).
- RN-F0-11: as regras não podem passar "por vazio": cada regra tem um auto-teste com uma fixture que a viola.

## Fora de escopo

- Regras específicas de cada módulo (entram nas fases, se necessário).
