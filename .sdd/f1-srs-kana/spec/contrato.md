# Contrato — Fase 1

Contrato de código (assinaturas) para que agentes diferentes produzam a mesma estrutura. Nomes de métodos privados e detalhes internos ficam livres.

## REST

Ver `docs/sdd/api.md` → "Fase 1 — SRS" (fonte da verdade dos endpoints, corpos e erros).

| Endpoint | Controller | Use case / query |
|---|---|---|
| `POST /api/decks` | `srs.adapter.in.web.DeckController` | `CreateDeck` |
| `GET /api/decks` | `DeckController` | `DeckSummaryQuery` |
| `POST /api/decks/{deckId}/cards` | `DeckController` | `CreateCard` |
| `GET /api/review/due` | `srs.adapter.in.web.ReviewController` | `DueCardsQuery` |
| `POST /api/review` | `ReviewController` | `ReviewCard` |

DTOs de request (records em `srs.adapter.in.web`), com Bean Validation:

```java
record CreateDeckRequest(@NotBlank @Size(max = 100) String name) {}
record CreateCardRequest(@NotBlank @Size(max = 500) String front,
                         @NotBlank @Size(max = 1000) String back,
                         @Size(max = 200) String reading,
                         @Size(max = 1000) String example) {}
record ReviewRequest(@NotNull UUID reviewId, @NotNull UUID cardId, @NotNull Grade grade) {}
```

`GET /api/review/due`: `@RequestParam(required = false) UUID deckId`, `@RequestParam(defaultValue = "50") @Min(1) @Max(200) int limit`.

## `shared` (`dev.nihongolab.shared`)

```java
public record UserId(UUID value) { /* value não nulo */ }

public interface DomainEvent {
    UUID eventId();
    Instant occurredAt();
}

public abstract class AggregateRoot {
    protected final void registerEvent(DomainEvent event);
    public final List<DomainEvent> domainEvents();   // cópia imutável
    public final void clearDomainEvents();
}

public class DomainException extends RuntimeException {
    public enum Kind { NOT_FOUND, CONFLICT, UNPROCESSABLE }
    public DomainException(String code, Kind kind, String message);
    public String code();
    public Kind kind();
}
```

`dev.nihongolab.shared.web.ApiExceptionHandler` (`@RestControllerAdvice`, estende `ResponseEntityExceptionHandler`):

| Exceção | Status | `code` |
|---|---|---|
| `DomainException` | `NOT_FOUND`→404, `CONFLICT`→409, `UNPROCESSABLE`→422 | o da exceção |
| `MethodArgumentNotValidException`, `HandlerMethodValidationException`, `HttpMessageNotReadableException`, `MethodArgumentTypeMismatchException`, `IllegalArgumentException` | 400 | `validation-failed` (com `errors` quando houver campo) |
| `OptimisticLockingFailureException`, `DataIntegrityViolationException` | 409 | `concurrent-update` |

Corpo: `type = "/problems/" + code`, `title`, `status`, `detail`, `instance`, propriedade `code`.

## `srs.domain`

```java
public record DeckId(UUID value)   { public static DeckId newId(); }
public record CardId(UUID value)   { public static CardId newId(); }
public record ReviewId(UUID value) {}
public record DeckName(String value) {}                       // strip; 1..100
public record CardContent(String front, String back, String reading, String example) {}
public enum Grade { AGAIN(2), HARD(3), GOOD(4), EASY(5); public int quality(); }
public record SchedulingState(int repetitions, int intervalDays, BigDecimal ease, Instant dueAt) {
    public static SchedulingState initial(Instant createdAt);   // 0, 0, 2.50, createdAt
}
public enum SourceType { MANUAL, KANA, SUBTITLE, GRAMMAR }
public record CardSource(SourceType type, String reference) { public static CardSource manual(); }
public enum SystemDeck { KANA_HIRAGANA, KANA_KATAKANA }

public interface Scheduler {
    SchedulingState next(SchedulingState current, Grade grade, Instant now);
}
public final class Sm2Scheduler implements Scheduler {}

public final class Deck extends AggregateRoot {
    public static Deck create(DeckId id, UserId owner, DeckName name, Instant now);
    public static Deck createSystem(DeckId id, UserId owner, DeckName name, SystemDeck key, Instant now);
    public static Deck rehydrate(DeckId id, UserId owner, DeckName name, SystemDeck keyOrNull, Instant createdAt);
    public DeckId id(); public UserId ownerId(); public DeckName name();
    public Optional<SystemDeck> systemKey(); public Instant createdAt();
}

public final class Card extends AggregateRoot {
    public static Card create(CardId id, Deck deck, CardContent content, CardSource source, String lemmaOrNull, Instant now);
    public static Card rehydrate(CardId id, DeckId deckId, UserId owner, CardContent content, CardSource source,
                                 String lemmaOrNull, SchedulingState state, Instant createdAt);
    public Review review(ReviewId reviewId, Grade grade, Instant now, Scheduler scheduler);
    public CardId id(); public DeckId deckId(); public UserId ownerId(); public CardContent content();
    public CardSource source(); public Optional<String> lemma(); public SchedulingState state(); public Instant createdAt();
}

public record Review(ReviewId id, CardId cardId, UserId ownerId, Grade grade, Instant reviewedAt,
                     SchedulingState before, SchedulingState after) {}
```

`Card.create` usa `deck.ownerId()` como dono e `deck.id()` como deck (RN-CARD-02 garantido pelo tipo).

## `srs.domain.event` (`@NamedInterface("events")`)

```java
public record DeckCreated(UUID eventId, Instant occurredAt, UUID deckId, UserId userId,
                          String name, String systemKey) implements DomainEvent {}
public record CardCreated(UUID eventId, Instant occurredAt, UUID cardId, UUID deckId, UserId userId,
                          String sourceType, String lemma) implements DomainEvent {}
public record CardReviewed(UUID eventId, Instant occurredAt, UUID reviewId, UUID cardId, UserId userId,
                           String grade, Instant reviewedAt, Instant newDueAt, int intervalDays) implements DomainEvent {}
```

`occurredAt` = o `now` recebido pelo método do aggregate.

## `srs.application.port.in`

```java
public interface CreateDeck { DeckResult handle(CreateDeckCommand command); }
public record CreateDeckCommand(UserId userId, String name) {}
public record DeckResult(UUID id, String name, String systemKey, Instant createdAt) {}

public interface CreateCard { CardResult handle(CreateCardCommand command); }
public record CreateCardCommand(UserId userId, UUID deckId, String front, String back, String reading, String example) {}
public record CardResult(UUID id, UUID deckId, String front, String back, String reading, String example,
                         String sourceType, String sourceReference, Instant dueAt, Instant createdAt) {}

public interface ReviewCard { ReviewResult handle(ReviewCardCommand command); }
public record ReviewCardCommand(UserId userId, UUID reviewId, UUID cardId, Grade grade) {}
public record ReviewResult(UUID reviewId, UUID cardId, Grade grade, Instant reviewedAt,
                           int repetitions, int intervalDays, BigDecimal ease, Instant dueAt) {}

public interface SeedKanaDecks { void handle(UserId userId); }

public interface DueCardsQuery { List<DueCardView> find(UserId userId, UUID deckIdOrNull, int limit); }
public record DueCardView(UUID cardId, UUID deckId, String front, String back, String reading, String example, Instant dueAt) {}

public interface DeckSummaryQuery { List<DeckSummaryView> list(UserId userId); }
public record DeckSummaryView(UUID id, String name, String systemKey, long totalCards, long dueCards) {}
```

Implementações: `application/command/*Service` (`@Service`, `@Transactional`) e `application/query/Jdbc*Query` (`JdbcClient`).

## `srs.application.port.out`

```java
public interface DeckRepository {
    Optional<Deck> findByIdAndOwner(DeckId id, UserId owner);
    boolean existsByOwnerAndNameIgnoreCase(UserId owner, DeckName name);
    boolean existsByOwnerAndSystemKey(UserId owner, SystemDeck key);
    void save(Deck deck);
}
public interface CardRepository {
    Optional<Card> findByIdAndOwner(CardId id, UserId owner);
    void save(Card card);
}
public interface ReviewRepository {
    Optional<Review> findById(ReviewId id);
    void save(Review review);
}
public interface KanaContentSource { List<KanaEntry> load(SystemDeck deck); }
public record KanaEntry(String kana, String romaji) {}
```

Adapters em `srs.adapter.out.persistence` (JPA) e `srs.adapter.out.content` (JSON do classpath).

## Erros de domínio

| `code` | `Kind` | Lançado por |
|---|---|---|
| `deck-name-taken` | CONFLICT | `CreateDeck` |
| `deck-not-found` | NOT_FOUND | `CreateCard`, `DueCardsQuery` |
| `card-not-found` | NOT_FOUND | `ReviewCard` |
| `review-id-conflict` | CONFLICT | `ReviewCard` |

## `identity`

```java
package dev.nihongolab.identity.api;           // @NamedInterface("api")
public interface CurrentUser { UserId currentUserId(); }
```

| Classe (`identity.adapter.in.web`) | Ativa quando |
|---|---|
| `DevCurrentUser` — devolve `UserId(nihongolab.dev-user.id)` | `nihongolab.dev-user.enabled=true` |
| `NoSessionCurrentUser` — lança `IllegalStateException` | `nihongolab.dev-user.enabled=false` ou ausente |

`SecurityConfig`: com `dev-user.enabled=true`, `/api/**` `permitAll()` e CSRF ignorado em `/api/**`. Sem a propriedade: igual à Fase 0.

## Propriedades

| Chave | Padrão | Testes de integração do `srs` |
|---|---|---|
| `nihongolab.dev-user.enabled` | `false` | `true` |
| `nihongolab.dev-user.id` | `00000000-0000-0000-0000-000000000001` | idem |

## Kana

- `srs.adapter.in.startup.DevKanaSeeder`: `@EventListener(ApplicationReadyEvent.class)`, ativo só com `dev-user.enabled=true`; chama `SeedKanaDecks.handle(currentUser.currentUserId())`.
- Arquivos: `backend/src/main/resources/content/kana/hiragana.json` e `katakana.json` (conteúdo em `jornadas/J05-seed-kana.md`).

## Persistência

- Migração `V002__srs_init.sql` com o DDL de `docs/sdd/dados.md` → "Fase 1".
- Entidades com `@Version Long version` (wrapper: nulo = novo).
- `ReviewJpaEntity` implementa `Persistable<UUID>` com `isNew() = true` na criação, para que a chave primária repetida gere erro em vez de `merge`.

## Eventos publicados

`DeckCreated`, `CardCreated`, `CardReviewed` (ver `docs/sdd/eventos.md`). Publicados pelo command com `ApplicationEventPublisher` depois do `save`, na mesma transação; depois `clearDomainEvents()`.
