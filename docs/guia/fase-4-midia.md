# Fase 4 — Mídia (roteiro)

Spec: `.sdd/f4-midia/` (em descoberta). Regras: RN-MEDIA-01..06.

## Ordem sugerida

1. Parser de SRT + limpeza no **domínio** (Java puro, muitos testes de unidade com legendas reais).
2. `Subtitle` aggregate, migração `media_*`, upload → `SubtitleImported`.
3. `TokenizerPort` + adapter Kuromoji.
4. Listener assíncrono que tokeniza e publica `SubtitleTokenized`.
5. Query de linhas com tokens e `isNew` (via `srs/api/KnownLemmas`, ver P-05).
6. `POST /api/decks/{deckId}/cards/from-sentence` no `srs`.
7. Front: upload, polling, player, clique na palavra.

## Trechos-chave

Dependência:

```xml
<dependency>
  <groupId>com.atilika.kuromoji</groupId>
  <artifactId>kuromoji-ipadic</artifactId>
  <version>0.9.0</version>
</dependency>
```

Adapter:

```java
@Component
class KuromojiTokenizerAdapter implements TokenizerPort {

    private final Tokenizer tokenizer = new Tokenizer();   // thread-safe; carregar uma vez

    @Override
    public List<TokenData> tokenize(String text) {
        return tokenizer.tokenize(text).stream()
                .map(t -> new TokenData(
                        t.getSurface(),
                        "*".equals(t.getBaseForm()) ? t.getSurface() : t.getBaseForm(),
                        t.getReading(),
                        t.getPartOfSpeechLevel1(),
                        t.getPosition()))
                .toList();
    }
}
```

Listener:

```java
@Component
class SubtitleImportedListener {

    private final TokenizeSubtitle tokenizeSubtitle;

    @ApplicationModuleListener
    void on(SubtitleImported event) {
        tokenizeSubtitle.handle(event.subtitleId());   // só processa se PENDING (RN-MEDIA-05)
    }
}
```

Expressão do tempo SRT: `(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})`.

Player (front):

```ts
protected readonly videoUrl = signal<string | null>(null);

onFile(input: HTMLInputElement): void {
  const file = input.files?.[0];
  if (!file) return;
  const old = this.videoUrl();
  if (old) URL.revokeObjectURL(old);
  this.videoUrl.set(URL.createObjectURL(file));
}

onTime(video: HTMLVideoElement): void {
  const ms = video.currentTime * 1000;
  this.currentLine.set(this.lines().find(l => l.startMs <= ms && ms < l.endMs) ?? null);
}
```

## Armadilhas

- **BOM e CRLF:** remova `﻿` do início; normalize `\r\n` para `\n` antes de separar blocos.
- **Forma base `*`:** palavras desconhecidas do dicionário vêm com base `*`; use a superfície.
- **Leitura em katakana:** o Kuromoji devolve a leitura em katakana; converta para hiragana na exibição se quiser.
- **Memória:** o dicionário IPADIC ocupa dezenas de MB no heap. Conte isso no `mem_limit` (Fase 8).
- **Ciclo entre módulos:** `media` → `srs/api` e `srs` → `media` ao mesmo tempo quebra o `verify()`. Ver P-05.
- **Formato de vídeo:** MKV geralmente não toca; avise o usuário (NFR-COMP-02).
- **Tamanho:** limite 2 MB (`spring.servlet.multipart.max-file-size: 2MB`).

## Testes (prévia)

- Parser: BOM, CRLF, várias linhas por bloco, tags, `（笑）`, falante `（田中）`, bloco inválido contado em `skippedBlocks`.
- `.srt` de exemplo em `src/test/resources/subtitles/` → status `DONE` (esperar o listener).
- Token com lema já existente nos cartões do usuário → `isNew=false`.
