# Testes — Fase 1

Convenções:
- `T0 = 2026-01-10T12:00:00Z`. Testes de integração usam `Clock.fixed(T0, UTC)` como bean `@Primary`.
- `U1 = 00000000-0000-0000-0000-000000000001` (usuário de dev); `U2 = 00000000-0000-0000-0000-000000000002`.
- Integração: base `IntegrationTest` da Fase 0 com `nihongolab.dev-user.enabled=true`.
- Publicação de eventos: `@RecordApplicationEvents` + `ApplicationEvents`.

## Shared

### C01 — `UserId` não aceita nulo
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: unidade
- Quando: `new UserId(null)`
- Então: `NullPointerException`
- Origem: dominio.md → shared

### C02 — `AggregateRoot` acumula e limpa eventos
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: unidade
- Dado: subclasse de teste que registra 2 eventos
- Então: `domainEvents()` tem 2 itens na ordem de registro; a lista devolvida é imutável (`add` lança `UnsupportedOperationException`); após `clearDomainEvents()`, está vazia
- Origem: D-08

## Value objects

### C03 — `DeckName` apara e valida tamanho · RN-DECK-01
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: unidade
- Casos: `"  Verbos "` → `"Verbos"`; 100 × `"a"` → aceito; `""`, `"   "`, 101 × `"a"` → `IllegalArgumentException`
- Origem: dominio.md → VOs

### C04 — `CardContent` valida e normaliza opcionais
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: unidade
- Casos: `front=""` → `IllegalArgumentException`; `front` com 501 caracteres → `IllegalArgumentException`; `back` com 1001 → `IllegalArgumentException`; `reading="  "` → `reading() == null`; `example=" ex "` → `"ex"`
- Origem: dominio.md → VOs

### C05 — `SchedulingState` rejeita estado inválido
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: unidade
- Casos: `repetitions=-1`, `intervalDays=-1`, `ease=1.29` → `IllegalArgumentException`; `ease=null` ou `dueAt=null` → `NullPointerException`; `ease=2.5` é guardado como `2.50` (`new SchedulingState(0,0,2.5,T0).equals(initial(T0))`); `initial(T0)` → `(0, 0, 2.50, T0)`
- Origem: dominio.md → VOs; RN-CARD-01

### C06 — `Grade` mapeia a qualidade do SM-2
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: unidade
- Então: `AGAIN.quality()=2`, `HARD=3`, `GOOD=4`, `EASY=5`
- Origem: dominio.md → VOs

## SM-2

### C10 — Tabela de referência do SM-2 · RN-SM2-01..04
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: unidade (teste parametrizado, 10 linhas)
- Dado/Quando/Então: as 10 linhas da tabela em `docs/sdd/dominio.md` → "SM-2", com `now = T0`
- Exemplo (linha 4): `(2, 6, 2.50)` + `EASY` → `(3, 16, 2.60, 2026-01-26T12:00:00Z)`
- Origem: dominio.md

### C11 — Intervalo arredonda HALF_UP · RN-SM2-02
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: unidade
- Dado: `repetitions=3`, `intervalDays=5`, `ease=2.50`
- Quando: `GOOD` em `T0`
- Então: `repetitions=4`, `intervalDays=13` (5 × 2.5 = 12.5 → 13), `ease=2.50`, `dueAt=2026-01-23T12:00:00Z`
- Origem: RN-SM2-02 (HALF_UP; arredondamento bancário daria 12)

### C12 — Scheduler é determinístico · RN-SM2-05
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: unidade
- Quando: `next(s, GOOD, T0)` chamado duas vezes com o mesmo `s`
- Então: resultados iguais (`equals`); `s` não muda (record imutável)
- Origem: RN-SM2-05

## Aggregates

### C20 — Cartão novo · RN-CARD-01, RN-CARD-02
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: unidade
- Dado: `deck = Deck.create(D1, U1, "Verbos", T0)`
- Quando: `Card.create(C1, deck, content, CardSource.manual(), null, T0)`
- Então: `ownerId=U1`, `deckId=D1`, `state=(0, 0, 2.50, T0)`; `domainEvents()` tem um `CardCreated` com `cardId=C1`, `deckId=D1`, `userId=U1`, `sourceType="MANUAL"`, `lemma=null`, `occurredAt=T0`
- Origem: RN-CARD-01, RN-CARD-02, eventos.md

### C21 — Revisar troca o estado e registra `CardReviewed` · RN-CARD-03
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: unidade
- Dado: cartão reidratado com `(1, 1, 2.50, 2026-01-10T12:00Z)` e sem eventos
- Quando: `review(R1, GOOD, T0, new Sm2Scheduler())`
- Então: `state=(2, 6, 2.50, 2026-01-16T12:00Z)`; `Review.before=(1, 1, 2.50, T0)`, `Review.after=state`; um `CardReviewed` com `reviewId=R1`, `grade="GOOD"`, `reviewedAt=T0`, `newDueAt=2026-01-16T12:00Z`, `intervalDays=6`
- Origem: RN-CARD-03, RN-REV-04, linha 2 da tabela

### C22 — Revisão antecipada é permitida · RN-CARD-04
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: unidade
- Dado: cartão com `(2, 6, 2.50, dueAt=2026-01-16T12:00Z)` (ainda não vencido em `T0`)
- Quando: `review(R2, GOOD, T0, sm2)`
- Então: `state=(3, 15, 2.50, 2026-01-25T12:00Z)`, sem exceção
- Origem: RN-CARD-04, linha 3 da tabela

### C23 — Deck registra `DeckCreated`
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: unidade
- Casos: `Deck.create(D1, U1, "Verbos", T0)` → `DeckCreated(deckId=D1, userId=U1, name="Verbos", systemKey=null, occurredAt=T0)`; `Deck.createSystem(D2, U1, "Hiragana", KANA_HIRAGANA, T0)` → `systemKey="KANA_HIRAGANA"`
- Origem: eventos.md

## Persistência

### C30 — Ida e volta no banco sem perda
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: integração (Testcontainers)
- Dado: deck, cartão com `reading`, `example`, `lemma` e `state=(3, 15, 2.36, 2026-01-25T12:00Z)`; uma `Review`
- Quando: `save` e `findByIdAndOwner` / `findById`
- Então: os objetos lidos têm todos os campos iguais aos gravados (ease comparado com `compareTo`); `findByIdAndOwner(C1, U2)` → vazio
- Origem: contrato.md → port.out; NFR-SEC-01

## Commands

### C31 — Criar deck grava e publica · J01
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: integração
- Quando: `CreateDeck.handle(U1, "  Verbos ")`
- Então: `DeckResult.name="Verbos"`, `createdAt=T0`; 1 linha em `srs_deck` com `owner_id=U1`; `events.stream(DeckCreated.class).count()=1`
- Origem: J01

### C32 — Nome de deck repetido sem diferenciar maiúsculas · RN-DECK-01
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: integração
- Dado: U1 tem "Verbos"
- Então: `CreateDeck(U1, "verbos")` → `DomainException` com `code="deck-name-taken"`; `CreateDeck(U2, "Verbos")` → ok
- Origem: RN-DECK-01

### C33 — Cartão em deck de outro usuário · RN-CARD-02, NFR-SEC-02
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: integração
- Dado: deck D1 de U1
- Quando: `CreateCard(U2, D1, ...)`
- Então: `DomainException` `deck-not-found`; nenhuma linha nova em `srs_card`
- Origem: RN-CARD-02

### C34 — Revisar grava estado, histórico e evento · J03 (critério do PLAN)
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: integração
- Dado: U1 cria deck e cartão em `T0` (estado inicial)
- Quando: `ReviewCard(U1, R1, C1, GOOD)`
- Então: `ReviewResult = (R1, C1, GOOD, T0, 1, 1, 2.50, 2026-01-11T12:00Z)`; `srs_card.due_at = 2026-01-11T12:00Z`; 1 linha em `srs_review` com `prev_*=(0, 0, 2.50, T0)` e `new_*=(1, 1, 2.50, 2026-01-11T12:00Z)`; `events.stream(CardReviewed.class).count()=1`
- Origem: PLAN Fase 1 "Pronto quando"; linha 1 da tabela; D-11

### C35 — Mesmo `reviewId` duas vezes · RN-REV-02
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: integração
- Dado: C34 executado
- Quando: `ReviewCard(U1, R1, C1, EASY)` (nota diferente, mesmo `reviewId`)
- Então: devolve exatamente o resultado de C34 (grade `GOOD`); `srs_review` continua com 1 linha; `srs_card` inalterado; nenhum `CardReviewed` novo
- Origem: RN-REV-02

### C36 — `reviewId` de outro usuário · RN-REV-03
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: integração
- Dado: R1 gravado por U1; U2 tem o cartão C2
- Quando: `ReviewCard(U2, R1, C2, GOOD)`
- Então: `DomainException` `review-id-conflict`
- Origem: RN-REV-03

### C37 — Revisar cartão de outro usuário · RN-CARD-05
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: integração
- Quando: `ReviewCard(U2, R9, C1, GOOD)` (C1 é de U1)
- Então: `DomainException` `card-not-found`; nada gravado
- Origem: RN-CARD-05

## Queries

### C40 — Vencidos do usuário em ordem · J04
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: integração
- Dado (gravados direto no banco): U1 com cartões A (`due_at=2026-01-09T12:00Z`), B (`=T0`), C (`=2026-01-11T12:00Z`); U2 com D (`=2026-01-01T00:00Z`)
- Quando: `DueCardsQuery.find(U1, null, 50)`
- Então: `[A, B]`, nessa ordem
- Origem: J04

### C41 — Filtro por deck e limite · J04
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: integração
- Dado: U1 com 3 vencidos no deck D1 e 2 no deck D2
- Então: `find(U1, D1, 50)` → 3 itens, todos de D1; `find(U1, null, 2)` → 2 itens (os de menor `due_at`); `find(U1, D9-de-U2, 50)` → `DomainException` `deck-not-found`
- Origem: J04

### C42 — Resumo dos decks · J04
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: integração
- Dado: U1 com deck "verbos" (3 cartões, 2 vencidos) e "Adjetivos" (0 cartões)
- Então: `list(U1)` → `[("Adjetivos", total 0, due 0), ("verbos", total 3, due 2)]`
- Origem: J04 (ordem por `lower(name)`)

## API

Todos com `nihongolab.dev-user.enabled=true`, usuário U1, `Clock` fixo em `T0`.

### C50 — `POST /api/decks` cria · J01
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: API (MockMvc ou `TestRestTemplate`)
- Quando: `{"name":"Verbos"}`
- Então: 201; corpo com `id` (UUID), `name="Verbos"`, `systemKey=null`, `createdAt="2026-01-10T12:00:00Z"`
- Origem: api.md

### C51 — Nome vazio · J01
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: API
- Quando: `{"name":"   "}`
- Então: 400; `Content-Type: application/problem+json`; `code="validation-failed"`; `errors[0].field="name"`
- Origem: api.md → Erros

### C52 — Nome repetido · RN-DECK-01
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: API
- Dado: "Verbos" existe
- Quando: `{"name":"VERBOS"}`
- Então: 409; `type="/problems/deck-name-taken"`; `code="deck-name-taken"`
- Origem: api.md

### C53 — `POST /api/decks/{id}/cards` cria · J02
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: API
- Quando: `{"front":"食べる","back":"comer","reading":"たべる","example":"ご飯を食べる。"}`
- Então: 201; `front="食べる"`; `source={"type":"MANUAL","reference":null}`; `dueAt="2026-01-10T12:00:00Z"`; `createdAt` igual a `dueAt`
- Origem: J02; RN-CARD-01

### C54 — Cartão em deck inexistente · J02
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: API
- Quando: deck com UUID aleatório
- Então: 404; `code="deck-not-found"`
- Origem: api.md

### C55 — `limit` fora da faixa · J04
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: API
- Quando: `GET /api/review/due?limit=0` e `?limit=201`
- Então: 400 `validation-failed` nos dois
- Origem: api.md

### C56 — `POST /api/review` reagenda · J03
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: API
- Dado: cartão novo criado em `T0`
- Quando: `{"reviewId":"<R1>","cardId":"<C1>","grade":"GOOD"}`
- Então: 200; `repetitions=1`, `intervalDays=1`, `ease=2.5` (comparação numérica), `dueAt="2026-01-11T12:00:00Z"`, `reviewedAt="2026-01-10T12:00:00Z"`; em seguida `GET /api/review/due` → `[]`
- Origem: J03; linha 1 da tabela

### C57 — `POST /api/review` repetido · RN-REV-02
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: API
- Quando: o mesmo corpo de C56 de novo
- Então: 200 com corpo idêntico ao de C56
- Origem: RN-REV-02

### C58 — `grade` inválida · J03
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: API
- Quando: `"grade":"MEDIUM"`
- Então: 400 `validation-failed`
- Origem: api.md

## Kana

### C60 — Seed cria os dois decks · RN-KANA-01
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: integração
- Quando: `SeedKanaDecks.handle(U2)`
- Então: U2 tem decks "Hiragana" (`KANA_HIRAGANA`) e "Katakana" (`KANA_KATAKANA`), 46 cartões cada; o primeiro cartão de Hiragana é `front="あ"`, `back="a"`, `source=(KANA, "あ")`; 2 `DeckCreated` e 92 `CardCreated`
- Origem: RN-KANA-01; J05

### C61 — Seed é idempotente · RN-KANA-02
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: integração
- Quando: `SeedKanaDecks.handle(U2)` duas vezes
- Então: continuam 2 decks e 92 cartões de U2; a segunda chamada não publica eventos
- Origem: RN-KANA-02

### C62 — Conteúdo dos JSON confere com a tabela oficial · RN-KANA-03
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: unidade (adapter de conteúdo, sem Spring)
- Então: `load(KANA_HIRAGANA)` tem 46 entradas, começa com `(あ, a)`, termina com `(ん, n)`, contém `(し, shi)`, `(ち, chi)`, `(つ, tsu)`, `(ふ, fu)`, `(を, wo)`, sem `kana` repetido; `load(KANA_KATAKANA)` idem com `ア`, `ン`, `シ`, `チ`, `ツ`, `フ`, `ヲ`
- Origem: J05

## Segurança e usuário corrente

### C70 — Sem modo dev, `/api` fica fechado · D-09
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: API (contexto com `nihongolab.dev-user.enabled=false`)
- Quando: `GET /api/decks` e `POST /api/decks`
- Então: 401 nos dois
- Origem: D-09; contrato.md → identity

### C71 — Modo dev usa o usuário configurado · D-09
- [ ] escrito  - [ ] falhando antes  - [ ] verde
- Nível: API
- Dado: `nihongolab.dev-user.enabled=true`, `nihongolab.dev-user.id=U1`
- Quando: `POST /api/decks` e depois consulta em `srs_deck`
- Então: `owner_id = U1`
- Origem: D-09
