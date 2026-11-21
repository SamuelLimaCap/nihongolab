# Produto

## Visão

Um lugar só para estudar japonês todo dia: revisar vocabulário e kana com repetição espaçada, estudar gramática por nível JLPT e transformar as falas dos doramas que você assiste em cartões de estudo.

Também é peça de portfólio: a arquitetura, os testes e a operação têm que estar à altura de um sistema de produção.

## Usuário

- **Estudante** (dono do projeto e, eventualmente, outras pessoas). Estuda no celular e no desktop. Às vezes sem internet.
- Cada usuário só vê os próprios dados. Não há conteúdo compartilhado entre usuários, exceto o conteúdo de sistema (kana, lições de gramática).

## Capacidades

| # | Capacidade | Fase |
|---|---|---|
| 1 | Criar decks e cartões manualmente | 1 |
| 2 | Revisar cartões vencidos com SM-2 (Errei / Difícil / Bom / Fácil) | 1 (API), 3 (tela) |
| 3 | Decks prontos de hiragana e katakana | 1 (API), 3 (tela) |
| 4 | Login com Google ou GitHub | 2 |
| 5 | Usar no celular e no desktop | 3 |
| 6 | Enviar `.srt` de um episódio e ver as falas tokenizadas | 4 |
| 7 | Assistir ao vídeo local com a legenda sincronizada e clicar numa palavra para virar cartão | 4 |
| 8 | Estudar lições de gramática N5/N4 e gerar cartões dos exemplos | 5 |
| 9 | Ver progresso (sequência de dias, palavras, revisões, % por nível) | 6 |
| 10 | Exportar e importar o progresso (JSON) e exportar para o Anki (CSV) | 6 |
| 11 | Revisar offline e sincronizar depois | 7 |
| 12 | Rodar em produção com HTTPS, métricas, logs e backup | 8 |

## Jornadas principais

### JP-01 — Revisão diária
1. Abre o app (celular ou desktop) e vê quantos cartões estão vencidos.
2. Entra em Revisão. Vê a frente, pensa, mostra a resposta.
3. Escolhe Errei / Difícil / Bom / Fácil (ou teclas 1–4). O próximo cartão aparece.
4. Termina quando não há mais cartão vencido.

### JP-02 — Minerar um episódio
1. Envia o `.srt` do episódio com título e número.
2. Acompanha o status até `DONE`.
3. Abre o player, escolhe o arquivo de vídeo local, assiste com a legenda.
4. Clica numa palavra marcada como nova. Um cartão é criado com a frase como exemplo e a referência ao episódio e ao tempo.
5. O cartão aparece na revisão do dia seguinte.

### JP-03 — Estudar gramática
1. Escolhe o nível (N5) e uma lição.
2. Lê a explicação e os exemplos (inclusive frases das próprias legendas que contêm o padrão).
3. Conclui a lição e, se quiser, gera cartões dos exemplos.

### JP-04 — Backup
1. Exporta o progresso em JSON.
2. Em outro momento (ou outra conta/instância), importa o arquivo e encontra tudo igual.

## Fora de escopo

- Hospedar ou transmitir vídeo. O vídeo nunca sai do navegador.
- Conteúdo social, ranking, compartilhamento de decks entre usuários.
- App nativo (iOS/Android). O PWA cobre o celular.
- Dicionário completo (JMdict) na primeira versão. Pode virar fase futura.
- Áudio/TTS na primeira versão.
- Internacionalização da interface: a interface é em português.
