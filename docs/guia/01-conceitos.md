# 01 — Conceitos

O mínimo para entender **por que** o código fica onde fica. As regras obrigatórias estão no `AGENTS.md`.

## Monólito modular (Spring Modulith)

Um único processo Java, dividido em módulos que se comportam como se fossem serviços separados:

- Cada pacote direto abaixo de `dev.nihongolab` é um módulo (`srs`, `media`...).
- Outros módulos só enxergam o que o módulo expõe: o pacote raiz dele e as **named interfaces** (`api`, `domain/event`).
- `ApplicationModules.verify()` falha o build se um módulo acessar o interior de outro ou se houver ciclo.

Ganho: a separação de microsserviços sem rede, sem Kafka e com uma transação de banco só.

## Hexagonal (portas e adaptadores)

```fluxo
HTTP ──▶ adapter/in/web ──▶ application/port/in ──▶ application/command|query ──▶ domain
                                                         │
                                                         ▼
                                             application/port/out ◀── adapter/out/persistence ──▶ Postgres
```

- **domain**: regras de negócio em Java puro. Testável sem Spring, sem banco.
- **application**: orquestra casos de uso. Define **portas** (interfaces): `port/in` (o que a aplicação oferece) e `port/out` (o que ela precisa de fora: repositório, tokenizer).
- **adapter**: implementa as portas com tecnologia concreta (controller REST, JPA, Kuromoji).

A seta de dependência aponta sempre para dentro: o domínio não sabe que existe Spring.

## DDD tático

- **Value object**: valor imutável que se valida no construtor (`DeckName`, `SchedulingState`). Se existe, é válido.
- **Aggregate**: objeto com identidade que protege suas regras (`Card`). Só muda por métodos com nome de negócio (`review`), nunca por setter.
- **Evento de domínio**: fato que aconteceu (`CardReviewed`). O aggregate registra; o command publica depois de salvar.

## Eventos e outbox

```fluxo
ReviewCardService (transação)
  ├─ salva card e review
  └─ publishEvent(CardReviewed)
        └─ Modulith grava em event_publication (mesma transação) para cada listener
commit
  └─ listener assíncrono (@ApplicationModuleListener) roda em outra transação
        ├─ sucesso → publicação marcada como concluída
        └─ falha/queda → fica pendente e é reenviada no restart
```

Por isso os listeners precisam ser idempotentes: podem rodar mais de uma vez.

Atenção: sem listener, não há linha em `event_publication` (D-11).

## CQRS leve

- **Command** (escrita): carrega o aggregate, chama o método, salva, publica eventos.
- **Query** (leitura): SQL direto com `JdbcClient`, devolve um record de leitura. Não carrega aggregate.
- Read models do `progress` são tabelas atualizadas por listeners — uma "visão" pronta para o painel.

## BFF (Backend for Frontend) no login

```fluxo
Angular ──▶ /oauth2/authorization/google ──▶ Google ──▶ /login/oauth2/code/google (backend)
backend cria sessão no Redis ──▶ Set-Cookie: SESSION (HttpOnly, Secure, SameSite=Lax)
Angular chama /api/** com o cookie; mutações mandam X-XSRF-TOKEN lido do cookie XSRF-TOKEN
```

O navegador nunca vê token de acesso. Um XSS não consegue roubar a sessão (cookie `HttpOnly`).

## SM-2 em uma frase

Cada acerto multiplica o intervalo pelo ease; cada nota ajusta o ease; um erro zera as repetições. As regras exatas e a tabela de referência estão em `docs/sdd/dominio.md`.
