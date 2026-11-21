# Fase 9 — Polimento para o portfólio (roteiro)

Spec: `.sdd/f9-polimento/` (em descoberta).

## Ordem sugerida

1. PIT no domínio de `srs` e `progress`; matar mutantes sobreviventes com testes melhores.
2. E2E dos fluxos principais.
3. README.
4. Revisão dos ADRs contra o código.

## Trechos-chave

PIT (`pom.xml`, confira as últimas versões):

```xml
<plugin>
  <groupId>org.pitest</groupId>
  <artifactId>pitest-maven</artifactId>
  <version><!-- última --></version>
  <dependencies>
    <dependency>
      <groupId>org.pitest</groupId>
      <artifactId>pitest-junit5-plugin</artifactId>
      <version><!-- última --></version>
    </dependency>
  </dependencies>
  <configuration>
    <targetClasses>
      <param>dev.nihongolab.srs.domain.*</param>
      <param>dev.nihongolab.progress.domain.*</param>
    </targetClasses>
    <targetTests>
      <param>dev.nihongolab.srs.domain.*</param>
      <param>dev.nihongolab.progress.domain.*</param>
    </targetTests>
    <mutationThreshold>70</mutationThreshold>
  </configuration>
</plugin>
```

Rodar: `./mvnw org.pitest:pitest-maven:mutationCoverage`. Relatório em `target/pit-reports/`.

Login nos e2e com `mock-oauth2-server` (P-07): sobe como container no compose de teste e é registrado como um terceiro provedor só no perfil `e2e`. Nenhum endpoint de login falso no código de produção.

Estrutura do README:

1. Uma frase do que é + GIF (revisão no celular e mineração de legenda).
2. Link do deploy.
3. Arquitetura: diagrama C4 (de `docs/architecture.md`) e tabela de módulos.
4. Decisões: lista de ADRs com uma linha cada.
5. Como rodar em um comando (`docker compose ... --profile full up -d --build`).
6. Como o projeto foi construído: SDD com múltiplos agentes (`docs/sdd/`), com link para uma fase como exemplo.
7. Testes: pirâmide, mutação, e2e.

## Armadilhas

- **PIT e Spring:** mantenha o PIT só no domínio puro; com contexto Spring ele fica lento demais.
- **Mutante equivalente:** alguns sobrevivem sem ser bug (ex.: `>=` vs `>` num limite que nunca acontece). Documente em vez de forçar teste artificial.
- **GIF pesado:** grave em resolução baixa ou use vídeo curto em MP4.
