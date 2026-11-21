# Fase 5 — Gramática (roteiro)

Spec: `.sdd/f5-gramatica/` (em descoberta). Regras: RN-GRAM-01, RN-GRAM-02.

## Ordem sugerida

1. Formato do JSON de conteúdo e 1 lição de exemplo (combine com a descoberta).
2. Domínio `Lesson`/`GrammarPoint`; migração `grammar_*`.
3. Loader idempotente (por `slug` + hash do conteúdo) no `ApplicationReadyEvent`.
4. Queries de lista e de lição, com cache Redis.
5. `CompleteLesson` → `LessonCompleted` (idempotente).
6. Exemplos das legendas do usuário (busca de texto em `media`, via `media/api`).
7. "Criar cartões dos exemplos" (command no `srs`, `source=GRAMMAR`).
8. Front: lista por nível, tela da lição.

## Trechos-chave

Formato sugerido de conteúdo (`content/grammar/n5-001-desu.json`):

```json
{
  "slug": "n5-desu",
  "level": "N5",
  "order": 1,
  "title": "です — ser/estar (polido)",
  "explanation": "Markdown com a explicação…",
  "points": [
    {
      "pattern": "N + です",
      "meaning": "é / está (forma polida)",
      "examples": [
        { "japanese": "学生です。", "reading": "がくせいです。", "translation": "Sou estudante." }
      ]
    }
  ]
}
```

Cache com JSON no Redis:

```java
@Configuration
@EnableCaching
class CacheConfig {
    @Bean
    RedisCacheConfiguration redisCacheConfiguration() {
        return RedisCacheConfiguration.defaultCacheConfig()
                .entryTtl(Duration.ofHours(12))
                .serializeValuesWith(RedisSerializationContext.SerializationPair
                        .fromSerializer(new GenericJackson2JsonRedisSerializer()));
    }
}
```

```java
@Cacheable(cacheNames = "grammar-lessons", key = "#level")
public List<LessonSummaryView> listByLevel(String level) { ... }
```

## Armadilhas

- **Cache por usuário:** a lista tem o campo `completed`, que é por usuário. Faça cache só do conteúdo (igual para todos) e junte `completed` depois, ou use o `userId` na chave.
- **Invalidação:** quando o loader atualizar uma lição (hash mudou), limpe o cache (`@CacheEvict(allEntries = true)`).
- **Records no cache:** o `GenericJackson2JsonRedisSerializer` grava o tipo (`@class`); renomear um record invalida o cache antigo. Use um prefixo de versão no nome do cache.
- **Conteúdo:** é autoral. Revise com cuidado; um exemplo errado ensina errado.

## Testes (prévia)

- Loader rodando duas vezes não duplica; mudar o JSON atualiza a lição.
- Concluir duas vezes publica um `LessonCompleted` só.
- Segunda leitura de `/api/grammar/lessons?level=N5` não consulta o banco (conferir com contador ou log de SQL).
