# Domínio

Linguagem ubíqua, aggregates, value objects e regras de negócio (RN). Os cartões de teste das fases citam as RNs daqui.

## Glossário

| Termo (pt) | Código (en) | Significado |
|---|---|---|
| Deck | `Deck` | Conjunto de cartões de um usuário. |
| Cartão | `Card` | Item de estudo: frente, verso, leitura opcional, exemplo opcional. |
| Revisão | `Review` | Uma resposta do usuário a um cartão, com uma nota. |
| Nota | `Grade` | `AGAIN` (Errei), `HARD` (Difícil), `GOOD` (Bom), `EASY` (Fácil). |
| Estado de agendamento | `SchedulingState` | repetições, intervalo em dias, ease, data de vencimento. |
| Vencido | due | Cartão com `dueAt <= agora`. |
| Ease | `ease` | Fator de facilidade do SM-2. Mínimo 1.30, inicial 2.50. |
| Fonte do cartão | `CardSource` | `MANUAL`, `KANA`, `SUBTITLE`, `GRAMMAR`, com referência opcional. |
| Legenda | `Subtitle` | Um arquivo `.srt` importado: dorama, episódio, status. |
| Fala | `SubtitleLine` | Uma entrada do `.srt`: índice, início, fim, texto limpo. |
| Token | `Token` | Palavra de uma fala: superfície, forma base (lema), leitura, classe gramatical. |
| Lema | lemma | Forma base de um token (dicionário). Usado para saber se a palavra é nova. |
| Lição | `Lesson` | Conteúdo de gramática de um nível JLPT. |
| Ponto gramatical | `GrammarPoint` | Padrão, significado e exemplos dentro de uma lição. |
| Nível JLPT | `JlptLevel` | `N5`, `N4`, `N3`, `N2`, `N1`. |
| Sequência | streak | Dias seguidos com pelo menos uma revisão. |

## `shared`

| Tipo | Forma | Regra |
|---|---|---|
| `UserId` | `record UserId(UUID value)` | `value` não nulo. |
| `DomainEvent` | interface | `UUID eventId()`, `Instant occurredAt()`. |
| `AggregateRoot` | classe abstrata, Java puro | `registerEvent(DomainEvent)`, `List<DomainEvent> domainEvents()` (imutável), `clearDomainEvents()`. |
| `DomainException` | `RuntimeException` | Base das exceções de regra de negócio. Tem um `code` estável (ex.: `deck-name-taken`). |

## `srs`

### Value objects

| VO | Regra |
|---|---|
| `DeckId`, `CardId`, `ReviewId` | `record(UUID value)`, não nulo; `newId()` gera `UUID.randomUUID()`. |
| `DeckName` | aparado (`strip`); 1 a 100 caracteres. |
| `CardContent` | `front` 1–500, `back` 1–1000, `reading` 0–200 (opcional), `example` 0–1000 (opcional). Textos aparados; vazio vira `null` nos opcionais. |
| `Grade` | enum `AGAIN(2)`, `HARD(3)`, `GOOD(4)`, `EASY(5)`; o número é a qualidade `q` do SM-2. |
| `SchedulingState` | `repetitions >= 0`, `intervalDays >= 0`, `ease >= 1.30` normalizado para 2 casas (HALF_UP), `dueAt` não nulo. Sem teto de ease. |
| `CardSource` | `type` (`MANUAL`, `KANA`, `SUBTITLE`, `GRAMMAR`) + `reference` opcional (até 200 caracteres). |

### Aggregate `Deck`

- Campos: `id`, `ownerId`, `name`, `systemKey` (opcional: `KANA_HIRAGANA`, `KANA_KATAKANA`), `createdAt`.
- **RN-DECK-01** O nome é único por dono, sem diferenciar maiúsculas de minúsculas. Violação: `deck-name-taken` (409).
- **RN-DECK-02** `systemKey` é único por dono. Decks de sistema não podem ser renomeados nem apagados (quando existir apagar).
- Evento: `DeckCreated` ao criar.

### Aggregate `Card`

- Campos: `id`, `deckId`, `ownerId`, `content`, `source`, `state`, `createdAt`.
- **RN-CARD-01** Cartão novo nasce com `repetitions=0`, `intervalDays=0`, `ease=2.50`, `dueAt=createdAt` (já vencido).
- **RN-CARD-02** Cartão só pode ser criado num deck do mesmo dono. Senão: `deck-not-found` (404). Nunca 403: não revelamos que o deck existe.
- **RN-CARD-03** `review(grade, now, scheduler)` troca o estado pelo calculado pelo `Scheduler` e registra `CardReviewed`.
- **RN-CARD-04** Pode revisar um cartão ainda não vencido (revisão antecipada). O cálculo é o mesmo.
- **RN-CARD-05** Só o dono revisa. Cartão de outro dono: `card-not-found` (404).
- Evento: `CardCreated` ao criar.

### Revisão e idempotência

- **RN-REV-01** Toda revisão tem um `reviewId` gerado pelo cliente.
- **RN-REV-02** Repetir um `reviewId` já gravado pelo mesmo usuário devolve o resultado gravado, sem reagendar e sem novo evento.
- **RN-REV-03** Um `reviewId` já gravado por outro usuário: `review-id-conflict` (409).
- **RN-REV-04** A revisão grava o estado antes e depois (permite recalcular na sincronização offline).

### SM-2 (`Sm2Scheduler`)

Notação: `q` = qualidade da nota; `EF` = ease atual; `n` = repetições; `I` = intervalo em dias.

- **RN-SM2-01 — Ease.** Em toda revisão:
  `EF' = EF + (0.1 − (5 − q) × (0.08 + (5 − q) × 0.02))`,
  arredondado para 2 casas (HALF_UP), com mínimo 1.30.
  Variação por nota: `EASY` +0.10 · `GOOD` 0.00 · `HARD` −0.14 · `AGAIN` −0.32.
- **RN-SM2-02 — Acerto** (`HARD`, `GOOD`, `EASY`):
  `n' = n + 1`;
  `I' = 1` se `n' = 1`; `I' = 6` se `n' = 2`; senão `I' = round(I × EF')` (HALF_UP), mínimo 1.
  `dueAt' = now + I' dias`.
- **RN-SM2-03 — Erro** (`AGAIN`): `n' = 0`, `I' = 0`, `dueAt' = now + 10 minutos`.
- **RN-SM2-04** O cálculo usa o `EF'` já atualizado na mesma revisão.
- **RN-SM2-05** O cálculo é determinístico: mesma entrada, mesma saída. Sem `Instant.now()` dentro do scheduler.
- **RN-SM2-06** O `Scheduler` é uma interface; o `Sm2Scheduler` pode ser trocado por FSRS sem mudar o `Card`.

Tabela de referência (todos com `now = 2026-01-10T12:00:00Z`):

| # | n | I | EF | Nota | n' | I' | EF' | dueAt' |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 0 | 2.50 | GOOD | 1 | 1 | 2.50 | 2026-01-11T12:00Z |
| 2 | 1 | 1 | 2.50 | GOOD | 2 | 6 | 2.50 | 2026-01-16T12:00Z |
| 3 | 2 | 6 | 2.50 | GOOD | 3 | 15 | 2.50 | 2026-01-25T12:00Z |
| 4 | 2 | 6 | 2.50 | EASY | 3 | 16 | 2.60 | 2026-01-26T12:00Z |
| 5 | 2 | 6 | 2.50 | HARD | 3 | 14 | 2.36 | 2026-01-24T12:00Z |
| 6 | 3 | 15 | 2.50 | AGAIN | 0 | 0 | 2.18 | 2026-01-10T12:10Z |
| 7 | 0 | 0 | 1.40 | AGAIN | 0 | 0 | 1.30 | 2026-01-10T12:10Z |
| 8 | 1 | 1 | 1.30 | HARD | 2 | 6 | 1.30 | 2026-01-16T12:00Z |
| 9 | 0 | 0 | 2.50 | EASY | 1 | 1 | 2.60 | 2026-01-11T12:00Z |
| 10 | 5 | 100 | 2.50 | GOOD | 6 | 250 | 2.50 | 2026-09-17T12:00Z |

### Kana

- **RN-KANA-01** Deck "Hiragana" (`systemKey=KANA_HIRAGANA`) com os 46 kana básicos; deck "Katakana" (`KANA_KATAKANA`) com os 46 básicos. Frente = kana, verso = romaji (Hepburn), `source=KANA`.
- **RN-KANA-02** O seed é idempotente: rodar duas vezes para o mesmo usuário não duplica deck nem cartão.
- **RN-KANA-03** Conteúdo em `backend/src/main/resources/content/kana/hiragana.json` e `katakana.json`. A lista oficial está em `.sdd/f1-srs-kana/spec/jornadas/J05-seed-kana.md`.

## `identity`

- Aggregate `User`: `id` (`UserId`), `provider` (`GOOGLE`, `GITHUB`), `providerSubject`, `displayName`, `email` (opcional — o GitHub pode não informar), `avatarUrl` (opcional), `createdAt`.
- **RN-ID-01** O usuário é identificado por `(provider, providerSubject)`, nunca pelo e-mail.
- **RN-ID-02** No primeiro login, cria o `User` e publica `UserRegistered`. Logins seguintes não publicam.
- API pública: `identity.api.CurrentUser` (`UserId currentUserId()`; lança `unauthenticated` se não houver sessão).

## `media`

- Aggregate `Subtitle`: `id`, `ownerId`, `showTitle` (1–200), `episode` (1–9999), `status` (`PENDING`, `PROCESSING`, `DONE`, `FAILED`), `failureReason`, `importedAt`, linhas.
- `SubtitleLine`: `id`, `index`, `startMs`, `endMs`, `text` (limpo), `tokens` (depois do processamento).
- `Token`: `surface`, `lemma`, `reading` (katakana do Kuromoji), `partOfSpeech`, `startOffset`.
- **RN-MEDIA-01** Parse do SRT: blocos separados por linha vazia; índice; `HH:MM:SS,mmm --> HH:MM:SS,mmm`; uma ou mais linhas de texto. Aceita `\r\n` e BOM UTF-8.
- **RN-MEDIA-02** Limpeza do texto: remove tags (`<i>`, `<v Nome>`, `{\an8}`), setas `➡`/`→`, indicação de quem fala entre parênteses no início (`（田中）`, `(田中)`), e descrições de som entre parênteses (`（笑）`, `(拍手)`). Linhas que ficarem vazias são descartadas.
- **RN-MEDIA-03** `endMs > startMs`. Bloco inválido é ignorado e contado em `skippedBlocks`; se nenhum bloco for válido: `subtitle-empty` (422).
- **RN-MEDIA-04** Transições de status: `PENDING → PROCESSING → DONE | FAILED`. Nenhuma outra.
- **RN-MEDIA-05** Reprocessar um `Subtitle` já `DONE` é no-op (listener idempotente).
- **RN-MEDIA-06** "Palavra nova" = token de classe conteúdo (substantivo, verbo, adjetivo, advérbio) cujo lema não está entre os lemas dos cartões do usuário.

## `grammar`

- Aggregate `Lesson`: `id`, `slug` (único), `level`, `order`, `title`, `explanation` (Markdown), `points`.
- `GrammarPoint`: `pattern`, `meaning`, `examples` (japonês, leitura, tradução).
- **RN-GRAM-01** Conteúdo vem de `backend/src/main/resources/content/grammar/*.json`. O loader é idempotente (por `slug` + hash do conteúdo).
- **RN-GRAM-02** Concluir uma lição já concluída é no-op (sem evento novo).

## `progress`

- Read models: `progress_daily_stats`, `progress_streak`, `progress_level`.
- **RN-PROG-01** Todo listener grava o `eventId` em `progress_processed_event` na mesma transação; evento já processado é ignorado.
- **RN-PROG-02** Sequência: dias seguidos (no fuso do usuário, ver P-02) com pelo menos uma revisão. Um dia sem revisão zera.
- **RN-PROG-03** Export inclui só dados do usuário autenticado.
- **RN-PROG-04** Import roda numa transação só, faz upsert por UUID e **nunca** sobrescreve registro de outro usuário: conflito de ID com outro dono → `import-id-conflict` (409) e nada é gravado.
- **RN-PROG-05** Export → apagar → import resulta no mesmo estado (comparação por conteúdo).
