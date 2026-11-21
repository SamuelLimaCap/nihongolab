# Fase 1 — Domínio SRS + Kana (passo a passo)

Spec: `.sdd/f1-srs-kana/spec/`. O contrato de assinaturas está em `contrato.md`; aqui vão as implementações de referência.

Pacote base `dev.nihongolab`; caminhos abaixo relativos a `backend/src/main/java/dev/nihongolab/`.

---

## Passo 1 — Shared kernel

`shared/UserId.java`:

```java
package dev.nihongolab.shared;

import java.util.Objects;
import java.util.UUID;

public record UserId(UUID value) {
    public UserId {
        Objects.requireNonNull(value, "value");
    }
}
```

`shared/DomainEvent.java`:

```java
package dev.nihongolab.shared;

import java.time.Instant;
import java.util.UUID;

public interface DomainEvent {
    UUID eventId();
    Instant occurredAt();
}
```

`shared/AggregateRoot.java`:

```java
package dev.nihongolab.shared;

import java.util.ArrayList;
import java.util.List;

public abstract class AggregateRoot {

    private final List<DomainEvent> events = new ArrayList<>();

    protected final void registerEvent(DomainEvent event) {
        events.add(event);
    }

    public final List<DomainEvent> domainEvents() {
        return List.copyOf(events);
    }

    public final void clearDomainEvents() {
        events.clear();
    }
}
```

`shared/DomainException.java`:

```java
package dev.nihongolab.shared;

public class DomainException extends RuntimeException {

    public enum Kind { NOT_FOUND, CONFLICT, UNPROCESSABLE }

    private final String code;
    private final Kind kind;

    public DomainException(String code, Kind kind, String message) {
        super(message);
        this.code = code;
        this.kind = kind;
    }

    public String code() { return code; }
    public Kind kind() { return kind; }
}
```

`shared/web/ApiExceptionHandler.java` — o tradutor único de exceção para ProblemDetail:

```java
package dev.nihongolab.shared.web;

import java.net.URI;
import java.util.List;
import java.util.Map;

import dev.nihongolab.shared.DomainException;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.dao.OptimisticLockingFailureException;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.ProblemDetail;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.context.request.WebRequest;
import org.springframework.web.method.annotation.HandlerMethodValidationException;
import org.springframework.web.servlet.mvc.method.annotation.ResponseEntityExceptionHandler;
import org.springframework.beans.TypeMismatchException;

@RestControllerAdvice
class ApiExceptionHandler extends ResponseEntityExceptionHandler {

    @ExceptionHandler(DomainException.class)
    ProblemDetail domain(DomainException e) {
        HttpStatus status = switch (e.kind()) {
            case NOT_FOUND -> HttpStatus.NOT_FOUND;
            case CONFLICT -> HttpStatus.CONFLICT;
            case UNPROCESSABLE -> HttpStatus.UNPROCESSABLE_ENTITY;
        };
        return problem(status, e.code(), e.getMessage());
    }

    @ExceptionHandler(IllegalArgumentException.class)
    ProblemDetail illegalArgument(IllegalArgumentException e) {
        return problem(HttpStatus.BAD_REQUEST, "validation-failed", e.getMessage());
    }

    @ExceptionHandler({OptimisticLockingFailureException.class, DataIntegrityViolationException.class})
    ProblemDetail concurrent(RuntimeException e) {
        return problem(HttpStatus.CONFLICT, "concurrent-update", "O recurso foi alterado por outra requisição. Tente de novo.");
    }

    @Override
    protected ResponseEntity<Object> handleMethodArgumentNotValid(MethodArgumentNotValidException e,
            HttpHeaders headers, HttpStatusCode status, WebRequest request) {
        ProblemDetail body = problem(HttpStatus.BAD_REQUEST, "validation-failed", "Dados inválidos.");
        List<Map<String, String>> errors = e.getBindingResult().getFieldErrors().stream()
                .map(f -> Map.of("field", f.getField(), "message", String.valueOf(f.getDefaultMessage())))
                .toList();
        body.setProperty("errors", errors);
        return ResponseEntity.badRequest().body(body);
    }

    @Override
    protected ResponseEntity<Object> handleHandlerMethodValidationException(HandlerMethodValidationException e,
            HttpHeaders headers, HttpStatusCode status, WebRequest request) {
        return ResponseEntity.badRequest().body(problem(HttpStatus.BAD_REQUEST, "validation-failed", "Parâmetro inválido."));
    }

    @Override
    protected ResponseEntity<Object> handleHttpMessageNotReadable(HttpMessageNotReadableException e,
            HttpHeaders headers, HttpStatusCode status, WebRequest request) {
        return ResponseEntity.badRequest().body(problem(HttpStatus.BAD_REQUEST, "validation-failed", "Corpo inválido."));
    }

    @Override
    protected ResponseEntity<Object> handleTypeMismatch(TypeMismatchException e,
            HttpHeaders headers, HttpStatusCode status, WebRequest request) {
        return ResponseEntity.badRequest().body(problem(HttpStatus.BAD_REQUEST, "validation-failed", "Parâmetro inválido."));
    }

    private static ProblemDetail problem(HttpStatus status, String code, String detail) {
        ProblemDetail p = ProblemDetail.forStatusAndDetail(status, detail);
        p.setType(URI.create("/problems/" + code));
        p.setTitle(status.getReasonPhrase());
        p.setProperty("code", code);
        return p;
    }
}
```

Por que no `shared.web`: é infraestrutura comum, sem regra de negócio, e fica fora de `..domain..`.

---

## Passo 2 — Value objects

`srs/domain/DeckName.java`:

```java
package dev.nihongolab.srs.domain;

import java.util.Objects;

public record DeckName(String value) {
    public DeckName {
        Objects.requireNonNull(value, "value");
        value = value.strip();
        if (value.isEmpty() || value.length() > 100) {
            throw new IllegalArgumentException("Nome do deck deve ter de 1 a 100 caracteres.");
        }
    }
}
```

`srs/domain/CardContent.java`:

```java
package dev.nihongolab.srs.domain;

public record CardContent(String front, String back, String reading, String example) {
    public CardContent {
        front = required(front, 500, "front");
        back = required(back, 1000, "back");
        reading = optional(reading, 200, "reading");
        example = optional(example, 1000, "example");
    }

    private static String required(String v, int max, String field) {
        String s = optional(v, max, field);
        if (s == null) throw new IllegalArgumentException(field + " é obrigatório.");
        return s;
    }

    private static String optional(String v, int max, String field) {
        if (v == null) return null;
        String s = v.strip();
        if (s.isEmpty()) return null;
        if (s.length() > max) throw new IllegalArgumentException(field + " passa de " + max + " caracteres.");
        return s;
    }
}
```

`srs/domain/Grade.java`:

```java
package dev.nihongolab.srs.domain;

public enum Grade {
    AGAIN(2), HARD(3), GOOD(4), EASY(5);

    private final int quality;

    Grade(int quality) { this.quality = quality; }

    public int quality() { return quality; }
}
```

`srs/domain/SchedulingState.java`:

```java
package dev.nihongolab.srs.domain;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Instant;
import java.util.Objects;

public record SchedulingState(int repetitions, int intervalDays, BigDecimal ease, Instant dueAt) {

    static final BigDecimal MIN_EASE = new BigDecimal("1.30");
    private static final BigDecimal INITIAL_EASE = new BigDecimal("2.50");

    public SchedulingState {
        if (repetitions < 0) throw new IllegalArgumentException("repetitions < 0");
        if (intervalDays < 0) throw new IllegalArgumentException("intervalDays < 0");
        Objects.requireNonNull(ease, "ease");
        Objects.requireNonNull(dueAt, "dueAt");
        ease = ease.setScale(2, RoundingMode.HALF_UP);
        if (ease.compareTo(MIN_EASE) < 0) throw new IllegalArgumentException("ease < 1.30");
    }

    public static SchedulingState initial(Instant createdAt) {
        return new SchedulingState(0, 0, INITIAL_EASE, createdAt);
    }
}
```

Normalizar a escala para 2 casas no construtor faz o `equals` do record funcionar (`2.5` e `2.50` são diferentes para `BigDecimal.equals`).

IDs (`DeckId`, `CardId`, `ReviewId`):

```java
public record CardId(UUID value) {
    public CardId { Objects.requireNonNull(value, "value"); }
    public static CardId newId() { return new CardId(UUID.randomUUID()); }
}
```

`SourceType`, `CardSource` (com `manual()`), `SystemDeck`: seguem o `contrato.md`.

---

## Passo 3 — SM-2

`srs/domain/Scheduler.java`:

```java
package dev.nihongolab.srs.domain;

import java.time.Instant;

public interface Scheduler {
    SchedulingState next(SchedulingState current, Grade grade, Instant now);
}
```

`srs/domain/Sm2Scheduler.java`:

```java
package dev.nihongolab.srs.domain;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Duration;
import java.time.Instant;

public final class Sm2Scheduler implements Scheduler {

    private static final Duration AGAIN_DELAY = Duration.ofMinutes(10);
    private static final BigDecimal BASE = new BigDecimal("0.1");
    private static final BigDecimal A = new BigDecimal("0.08");
    private static final BigDecimal B = new BigDecimal("0.02");

    @Override
    public SchedulingState next(SchedulingState current, Grade grade, Instant now) {
        BigDecimal ease = nextEase(current.ease(), grade);

        if (grade == Grade.AGAIN) {
            return new SchedulingState(0, 0, ease, now.plus(AGAIN_DELAY));
        }

        int repetitions = current.repetitions() + 1;
        int interval = switch (repetitions) {
            case 1 -> 1;
            case 2 -> 6;
            default -> Math.max(1, BigDecimal.valueOf(current.intervalDays())
                    .multiply(ease)
                    .setScale(0, RoundingMode.HALF_UP)
                    .intValueExact());
        };
        return new SchedulingState(repetitions, interval, ease, now.plus(Duration.ofDays(interval)));
    }

    static BigDecimal nextEase(BigDecimal ease, Grade grade) {
        BigDecimal d = BigDecimal.valueOf(5 - grade.quality());
        BigDecimal delta = BASE.subtract(d.multiply(A.add(d.multiply(B))));
        return ease.add(delta).setScale(2, RoundingMode.HALF_UP).max(SchedulingState.MIN_EASE);
    }
}
```

`BigDecimal` em vez de `double`: `6 × 2.6` em `double` dá `15.600000000000001`; aqui o resultado é exato e o arredondamento é o da spec (HALF_UP).

Teste parametrizado (C10) — a tabela vem de `docs/sdd/dominio.md`:

```java
class Sm2SchedulerTest {

    static final Instant T0 = Instant.parse("2026-01-10T12:00:00Z");
    final Scheduler sm2 = new Sm2Scheduler();

    @ParameterizedTest(name = "{index}: ({0},{1},{2}) + {3} -> ({4},{5},{6}, {7})")
    @CsvSource({
        "0, 0,   2.50, GOOD,  1, 1,   2.50, 2026-01-11T12:00:00Z",
        "1, 1,   2.50, GOOD,  2, 6,   2.50, 2026-01-16T12:00:00Z",
        // ... as outras 8 linhas da tabela
    })
    void referenceTable(int n, int i, String ef, Grade grade, int n2, int i2, String ef2, String due) {
        var before = new SchedulingState(n, i, new BigDecimal(ef), T0);
        var after = sm2.next(before, grade, T0);
        assertThat(after).isEqualTo(new SchedulingState(n2, i2, new BigDecimal(ef2), Instant.parse(due)));
    }
}
```

Escreva as 10 linhas você mesmo, lendo a tabela. É o melhor exercício para entender o SM-2.

---

## Passo 4 — Aggregates e eventos

`srs/domain/event/package-info.java`:

```java
@NamedInterface("events")
package dev.nihongolab.srs.domain.event;

import org.springframework.modulith.NamedInterface;
```

É a única anotação Spring dentro de `..domain..`, e fica num `package-info`, que a regra `DOMAIN_IS_PURE` ignora desde a Fase 0.

`srs/domain/event/CardReviewed.java`:

```java
package dev.nihongolab.srs.domain.event;

import java.time.Instant;
import java.util.UUID;

import dev.nihongolab.shared.DomainEvent;
import dev.nihongolab.shared.UserId;

public record CardReviewed(UUID eventId, Instant occurredAt, UUID reviewId, UUID cardId, UserId userId,
                           String grade, Instant reviewedAt, Instant newDueAt, int intervalDays)
        implements DomainEvent {
}
```

`DeckCreated` e `CardCreated` no mesmo formato (campos no `contrato.md`).

`srs/domain/Card.java`:

```java
package dev.nihongolab.srs.domain;

import java.time.Instant;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

import dev.nihongolab.shared.AggregateRoot;
import dev.nihongolab.shared.UserId;
import dev.nihongolab.srs.domain.event.CardCreated;
import dev.nihongolab.srs.domain.event.CardReviewed;

public final class Card extends AggregateRoot {

    private final CardId id;
    private final DeckId deckId;
    private final UserId ownerId;
    private final CardContent content;
    private final CardSource source;
    private final String lemma;
    private final Instant createdAt;
    private SchedulingState state;

    private Card(CardId id, DeckId deckId, UserId ownerId, CardContent content, CardSource source,
                 String lemma, SchedulingState state, Instant createdAt) {
        this.id = Objects.requireNonNull(id);
        this.deckId = Objects.requireNonNull(deckId);
        this.ownerId = Objects.requireNonNull(ownerId);
        this.content = Objects.requireNonNull(content);
        this.source = Objects.requireNonNull(source);
        this.lemma = lemma;
        this.state = Objects.requireNonNull(state);
        this.createdAt = Objects.requireNonNull(createdAt);
    }

    public static Card create(CardId id, Deck deck, CardContent content, CardSource source, String lemma, Instant now) {
        Card card = new Card(id, deck.id(), deck.ownerId(), content, source, lemma, SchedulingState.initial(now), now);
        card.registerEvent(new CardCreated(UUID.randomUUID(), now, id.value(), deck.id().value(),
                deck.ownerId(), source.type().name(), lemma));
        return card;
    }

    public static Card rehydrate(CardId id, DeckId deckId, UserId ownerId, CardContent content, CardSource source,
                                 String lemma, SchedulingState state, Instant createdAt) {
        return new Card(id, deckId, ownerId, content, source, lemma, state, createdAt);
    }

    public Review review(ReviewId reviewId, Grade grade, Instant now, Scheduler scheduler) {
        SchedulingState before = state;
        state = scheduler.next(before, grade, now);
        registerEvent(new CardReviewed(UUID.randomUUID(), now, reviewId.value(), id.value(), ownerId,
                grade.name(), now, state.dueAt(), state.intervalDays()));
        return new Review(reviewId, id, ownerId, grade, now, before, state);
    }

    public CardId id() { return id; }
    public DeckId deckId() { return deckId; }
    public UserId ownerId() { return ownerId; }
    public CardContent content() { return content; }
    public CardSource source() { return source; }
    public Optional<String> lemma() { return Optional.ofNullable(lemma); }
    public SchedulingState state() { return state; }
    public Instant createdAt() { return createdAt; }
}
```

Repare: não há setter. O único jeito de mudar o estado é `review`. `Card.create` recebe o `Deck`, então é impossível criar cartão com dono diferente do deck (RN-CARD-02 garantido pelo tipo).

`Deck` segue o mesmo padrão (`create`, `createSystem`, `rehydrate`; registra `DeckCreated`).

---

## Passo 5 — Persistência

`backend/src/main/resources/db/migration/V002__srs_init.sql`: DDL de `docs/sdd/dados.md` → "Fase 1".

`srs/adapter/out/persistence/CardJpaEntity.java` (trecho):

```java
@Entity
@Table(name = "srs_card")
public class CardJpaEntity {

    @Id
    private UUID id;

    @Column(name = "deck_id", nullable = false)
    private UUID deckId;

    @Column(name = "owner_id", nullable = false)
    private UUID ownerId;

    private String front;
    private String back;
    private String reading;
    private String example;
    private String lemma;

    @Column(name = "source_type", nullable = false)
    private String sourceType;

    @Column(name = "source_ref")
    private String sourceRef;

    private int repetitions;

    @Column(name = "interval_days")
    private int intervalDays;

    private BigDecimal ease;

    @Column(name = "due_at")
    private Instant dueAt;

    @Column(name = "created_at")
    private Instant createdAt;

    @Version
    private Long version;

    protected CardJpaEntity() {
    }

    // getters e setters: a entidade JPA é só um saco de dados; as regras estão no Card
}
```

`@Version Long` (wrapper): `null` faz o Spring Data tratar como novo e usar `persist`.

`CardJpaRepository`:

```java
public interface CardJpaRepository extends JpaRepository<CardJpaEntity, UUID> {
    Optional<CardJpaEntity> findByIdAndOwnerId(UUID id, UUID ownerId);
}
```

`CardPersistenceAdapter`:

```java
@Component
class CardPersistenceAdapter implements CardRepository {

    private final CardJpaRepository repository;

    CardPersistenceAdapter(CardJpaRepository repository) {
        this.repository = repository;
    }

    @Override
    public Optional<Card> findByIdAndOwner(CardId id, UserId owner) {
        return repository.findByIdAndOwnerId(id.value(), owner.value()).map(CardMapper::toDomain);
    }

    @Override
    public void save(Card card) {
        CardJpaEntity entity = repository.findById(card.id().value()).orElseGet(CardJpaEntity::new);
        CardMapper.copyInto(card, entity);
        repository.save(entity);
    }
}
```

Dentro da mesma transação, o `findById` devolve a entidade já gerenciada (com `version`), e o lock otimista funciona sem o domínio conhecer `version`.

`ReviewJpaEntity` implementa `Persistable<UUID>`:

```java
@Transient
private boolean isNew = true;

@Override public boolean isNew() { return isNew; }

@PostLoad @PostPersist
void markNotNew() { isNew = false; }
```

Assim um `reviewId` repetido gera erro de chave primária (→ 409 `concurrent-update`) em vez de virar `merge` silencioso.

---

## Passo 6 — Usuário corrente

`identity/api/package-info.java` com `@NamedInterface("api")` e `identity/api/CurrentUser.java`:

```java
package dev.nihongolab.identity.api;

import dev.nihongolab.shared.UserId;

public interface CurrentUser {
    UserId currentUserId();
}
```

`identity/adapter/in/web/DevCurrentUser.java`:

```java
@Component
@ConditionalOnProperty(name = "nihongolab.dev-user.enabled", havingValue = "true")
class DevCurrentUser implements CurrentUser {

    private final UserId userId;

    DevCurrentUser(@Value("${nihongolab.dev-user.id:00000000-0000-0000-0000-000000000001}") UUID id) {
        this.userId = new UserId(id);
    }

    @Override
    public UserId currentUserId() {
        return userId;
    }
}
```

`NoSessionCurrentUser`: mesmo esquema com `havingValue = "false", matchIfMissing = true`, lançando `IllegalStateException`.

`SecurityConfig` ganha o modo dev:

```java
@Bean
SecurityFilterChain securityFilterChain(HttpSecurity http,
        @Value("${nihongolab.dev-user.enabled:false}") boolean devUser) throws Exception {
    http.authorizeHttpRequests(auth -> {
        auth.requestMatchers("/actuator/health", "/actuator/health/**").permitAll();
        if (devUser) {
            auth.requestMatchers("/api/**").permitAll();
        }
        auth.anyRequest().authenticated();
    });
    if (devUser) {
        http.csrf(csrf -> csrf.ignoringRequestMatchers("/api/**"));
    }
    // httpBasic, formLogin e entry point 401 como na Fase 0
    return http.build();
}
```

Isso é **temporário** (D-09). A Fase 2 apaga tudo.

---

## Passo 7 — Commands

`srs/application/command/ReviewCardService.java`:

```java
@Service
@Transactional
class ReviewCardService implements ReviewCard {

    private final CardRepository cards;
    private final ReviewRepository reviews;
    private final Scheduler scheduler;
    private final Clock clock;
    private final ApplicationEventPublisher events;

    ReviewCardService(CardRepository cards, ReviewRepository reviews, Scheduler scheduler,
                      Clock clock, ApplicationEventPublisher events) {
        this.cards = cards;
        this.reviews = reviews;
        this.scheduler = scheduler;
        this.clock = clock;
        this.events = events;
    }

    @Override
    public ReviewResult handle(ReviewCardCommand command) {
        ReviewId reviewId = new ReviewId(command.reviewId());

        Optional<Review> existing = reviews.findById(reviewId);
        if (existing.isPresent()) {
            Review review = existing.get();
            if (!review.ownerId().equals(command.userId())) {
                throw new DomainException("review-id-conflict", Kind.CONFLICT, "Esse reviewId já foi usado.");
            }
            return toResult(review);
        }

        Card card = cards.findByIdAndOwner(new CardId(command.cardId()), command.userId())
                .orElseThrow(() -> new DomainException("card-not-found", Kind.NOT_FOUND, "Cartão não encontrado."));

        Review review = card.review(reviewId, command.grade(), clock.instant(), scheduler);
        cards.save(card);
        reviews.save(review);
        card.domainEvents().forEach(events::publishEvent);
        card.clearDomainEvents();
        return toResult(review);
    }

    private static ReviewResult toResult(Review r) {
        return new ReviewResult(r.id().value(), r.cardId().value(), r.grade(), r.reviewedAt(),
                r.after().repetitions(), r.after().intervalDays(), r.after().ease(), r.after().dueAt());
    }
}
```

O bean `Scheduler` vem de uma `@Configuration` em `srs/application`:

```java
@Configuration
class SrsApplicationConfig {
    @Bean
    Scheduler scheduler() {
        return new Sm2Scheduler();
    }
}
```

`CreateDeckService` e `CreateCardService` seguem o mesmo esqueleto: validar → carregar → chamar o aggregate → salvar → publicar → limpar eventos.

---

## Passo 8 — Queries

`srs/application/query/JdbcDueCardsQuery.java`:

```java
@Component
@Transactional(readOnly = true)
class JdbcDueCardsQuery implements DueCardsQuery {

    private static final String BASE = """
            select id, deck_id, front, back, reading, example, due_at
              from srs_card
             where owner_id = :owner
               and due_at <= :now
            """;

    private final JdbcClient jdbc;
    private final Clock clock;

    JdbcDueCardsQuery(JdbcClient jdbc, Clock clock) {
        this.jdbc = jdbc;
        this.clock = clock;
    }

    @Override
    public List<DueCardView> find(UserId userId, UUID deckId, int limit) {
        if (deckId != null && !ownsDeck(userId, deckId)) {
            throw new DomainException("deck-not-found", Kind.NOT_FOUND, "Deck não encontrado.");
        }
        String sql = BASE + (deckId != null ? " and deck_id = :deck" : "") + " order by due_at, id limit :limit";

        var spec = jdbc.sql(sql)
                .param("owner", userId.value())
                .param("now", OffsetDateTime.ofInstant(clock.instant(), ZoneOffset.UTC))
                .param("limit", limit);
        if (deckId != null) {
            spec = spec.param("deck", deckId);
        }
        return spec.query((rs, i) -> new DueCardView(
                rs.getObject("id", UUID.class),
                rs.getObject("deck_id", UUID.class),
                rs.getString("front"),
                rs.getString("back"),
                rs.getString("reading"),
                rs.getString("example"),
                rs.getObject("due_at", OffsetDateTime.class).toInstant())).list();
    }

    private boolean ownsDeck(UserId userId, UUID deckId) {
        return jdbc.sql("select exists(select 1 from srs_deck where id = :id and owner_id = :owner)")
                .param("id", deckId).param("owner", userId.value())
                .query(Boolean.class).single();
    }
}
```

**Armadilha:** o driver do Postgres não aceita `Instant` como parâmetro. Use `OffsetDateTime` na ida e na volta.

`DeckSummaryQuery`: um `left join` de `srs_deck` com `srs_card`, `count(c.id)` e `count(*) filter (where c.due_at <= :now)`, `order by lower(d.name)`.

---

## Passo 9 — API REST

`srs/adapter/in/web/ReviewController.java`:

```java
@RestController
@RequestMapping("/api/review")
class ReviewController {

    private final ReviewCard reviewCard;
    private final DueCardsQuery dueCards;
    private final CurrentUser currentUser;

    ReviewController(ReviewCard reviewCard, DueCardsQuery dueCards, CurrentUser currentUser) {
        this.reviewCard = reviewCard;
        this.dueCards = dueCards;
        this.currentUser = currentUser;
    }

    @GetMapping("/due")
    List<DueCardView> due(@RequestParam(required = false) UUID deckId,
                          @RequestParam(defaultValue = "50") @Min(1) @Max(200) int limit) {
        return dueCards.find(currentUser.currentUserId(), deckId, limit);
    }

    @PostMapping
    ReviewResponse review(@Valid @RequestBody ReviewRequest request) {
        ReviewResult r = reviewCard.handle(new ReviewCardCommand(
                currentUser.currentUserId(), request.reviewId(), request.cardId(), request.grade()));
        return ReviewResponse.from(r);
    }
}
```

O controller só traduz HTTP ↔ caso de uso. Nenhuma regra aqui.

Para respostas cujo formato difere do resultado da aplicação (o cartão tem `source` aninhado), crie um record de resposta no `adapter/in/web` com um `from(...)`.

Teste de API (C56), com relógio fixo:

```java
@TestPropertySource(properties = "nihongolab.dev-user.enabled=true")
@Import(SrsTestConfig.class)                 // @Bean @Primary Clock fixo em T0
class ReviewApiIntegrationTest extends IntegrationTest {

    @Autowired TestRestTemplate rest;
    @Autowired JdbcClient jdbc;

    @BeforeEach
    void clean() {
        jdbc.sql("truncate srs_review, srs_card, srs_deck cascade").update();
    }

    @Test
    void reviewReschedulesNewCard() {
        // cria deck e cartão via API, depois:
        var body = Map.of("reviewId", UUID.randomUUID(), "cardId", cardId, "grade", "GOOD");
        var response = rest.postForEntity("/api/review", body, JsonNode.class);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody().get("intervalDays").asInt()).isEqualTo(1);
        assertThat(response.getBody().get("dueAt").asText()).isEqualTo("2026-01-11T12:00:00Z");
    }
}
```

Dica: crie uma classe base `SrsIntegrationTest` com o `@TestPropertySource` e o `@Import` e use em todos os testes do `srs`. Um contexto só, um par de containers só.

Conferir eventos (C31, C34): anote a classe com `@RecordApplicationEvents` e injete `ApplicationEvents events`; `events.stream(CardReviewed.class).count()`.

---

## Passo 10 — Kana

`backend/src/main/resources/content/kana/hiragana.json` (início):

```json
[
  {"kana": "あ", "romaji": "a"}, {"kana": "い", "romaji": "i"}, {"kana": "う", "romaji": "u"},
  {"kana": "え", "romaji": "e"}, {"kana": "お", "romaji": "o"}
]
```

Complete com a tabela de `.sdd/f1-srs-kana/spec/jornadas/J05-seed-kana.md` (46 itens, na ordem). Faça o mesmo para `katakana.json`.

Adapter de conteúdo (`srs/adapter/out/content/ClasspathKanaContentSource`): lê o JSON com o `ObjectMapper`, valida 46 itens e devolve `List<KanaEntry>`.

`SeedKanaDecksService`:

```java
@Override
public void handle(UserId userId) {
    seed(userId, SystemDeck.KANA_HIRAGANA, "Hiragana");
    seed(userId, SystemDeck.KANA_KATAKANA, "Katakana");
}

private void seed(UserId userId, SystemDeck key, String name) {
    if (decks.existsByOwnerAndSystemKey(userId, key)) {
        return;
    }
    Instant now = clock.instant();
    Deck deck = Deck.createSystem(DeckId.newId(), userId, new DeckName(name), key, now);
    decks.save(deck);
    publish(deck);
    for (KanaEntry entry : content.load(key)) {
        Card card = Card.create(CardId.newId(), deck,
                new CardContent(entry.kana(), entry.romaji(), null, null),
                new CardSource(SourceType.KANA, entry.kana()), null, now);
        cards.save(card);
        publish(card);
    }
}
```

`DevKanaSeeder` (`srs/adapter/in/startup`): `@EventListener(ApplicationReadyEvent.class)`, `@ConditionalOnProperty(name = "nihongolab.dev-user.enabled", havingValue = "true")`, chama `seedKanaDecks.handle(currentUser.currentUserId())`.

---

## Rodar e testar à mão

```bash
cd backend
set -a && . ../.env && set +a
./mvnw spring-boot:run -Dspring-boot.run.arguments=--nihongolab.dev-user.enabled=true
# (por variável de ambiente seria NIHONGOLAB_DEVUSER_ENABLED=true: o Spring remove o hífen)

curl -s localhost:8080/api/decks | jq
curl -s -X POST localhost:8080/api/decks -H 'Content-Type: application/json' -d '{"name":"Verbos"}' | jq
curl -s 'localhost:8080/api/review/due?limit=5' | jq
```

## Conferência da fase

- [ ] C01–C71 verdes
- [ ] `./mvnw verify` verde (ArchUnit e Modulith incluídos)
- [ ] Papel `validar` por outro agente/modelo
