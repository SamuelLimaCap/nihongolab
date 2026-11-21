# J05 — Decks de kana

- Objetivo: todo usuário começa com os decks de hiragana e katakana.
- Ator: sistema. Na Fase 1, no `ApplicationReadyEvent` para o usuário de dev; na Fase 2, no `UserRegistered`.
- Pós-condições: 2 decks de sistema com 46 cartões cada.

## Fluxo principal

```fluxo
SeedKanaDecks(userId)
  para HIRAGANA e KATAKANA:
    DeckRepository.existsByOwnerAndSystemKey → true: pula
                                             → false: cria deck + 46 cartões (source KANA, reference = kana)
```

## Regras

- RN-KANA-01..03.
- Nome dos decks: `Hiragana` e `Katakana`.
- Cartão: `front` = kana, `back` = romaji, `reading` = nulo, `source = {type: KANA, reference: <kana>}`.
- A ordem de criação segue a tabela abaixo (linha por linha, da esquerda para a direita).

## Conteúdo oficial (fonte de `hiragana.json` e `katakana.json`)

| Linha | Hiragana | Katakana | Romaji |
|---|---|---|---|
| a | あ い う え お | ア イ ウ エ オ | a i u e o |
| k | か き く け こ | カ キ ク ケ コ | ka ki ku ke ko |
| s | さ し す せ そ | サ シ ス セ ソ | sa shi su se so |
| t | た ち つ て と | タ チ ツ テ ト | ta chi tsu te to |
| n | な に ぬ ね の | ナ ニ ヌ ネ ノ | na ni nu ne no |
| h | は ひ ふ へ ほ | ハ ヒ フ ヘ ホ | ha hi fu he ho |
| m | ま み む め も | マ ミ ム メ モ | ma mi mu me mo |
| y | や ゆ よ | ヤ ユ ヨ | ya yu yo |
| r | ら り る れ ろ | ラ リ ル レ ロ | ra ri ru re ro |
| w | わ を | ワ ヲ | wa wo |
| — | ん | ン | n |

Total: 46 por silabário.

Formato do JSON: `[{"kana":"あ","romaji":"a"}, ...]`, UTF-8, na ordem acima.

## Erro

- JSON ausente ou com quantidade diferente de 46: falha ao subir a app (erro de configuração, não de usuário).

## Fora de escopo

Dakuten, handakuten e yōon (P-06).
