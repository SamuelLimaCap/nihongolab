# Fase 7 — PWA offline (roteiro)

Spec: `.sdd/f7-pwa-offline/` (em descoberta).

## Ordem sugerida

1. `ng add @angular/pwa`; ajustar `ngsw-config.json`.
2. Dexie: tabelas `dueCards` e `pendingReviews`.
3. Revisão lê do cache quando offline e grava a resposta na fila.
4. `POST /api/review/batch` no backend (idempotente, ordem por `reviewedAt`).
5. Sync no evento `online` e ao abrir o app.
6. Indicador offline / sincronizando.
7. E2E Playwright.

## Trechos-chave

`ngsw-config.json` (parte de dados):

```json
{
  "dataGroups": [
    {
      "name": "api-review",
      "urls": ["/api/review/due", "/api/decks"],
      "cacheConfig": { "strategy": "freshness", "maxSize": 50, "maxAge": "1d", "timeout": "3s" }
    },
    {
      "name": "api-grammar",
      "urls": ["/api/grammar/**"],
      "cacheConfig": { "strategy": "performance", "maxSize": 200, "maxAge": "7d" }
    }
  ]
}
```

Os assets ficam nos `assetGroups` gerados pelo `ng add` (`installMode: prefetch`). Ver P-08.

Dexie:

```ts
export class OfflineDb extends Dexie {
  dueCards!: Table<DueCard, string>;
  pendingReviews!: Table<PendingReview, string>;

  constructor() {
    super('nihongolab');
    this.version(1).stores({
      dueCards: 'cardId, dueAt',
      pendingReviews: 'reviewId, reviewedAt',
    });
  }
}
```

Sync:

```ts
async sync(): Promise<void> {
  const pending = await this.db.pendingReviews.orderBy('reviewedAt').toArray();
  if (pending.length === 0) return;
  const results = await firstValueFrom(this.http.post<BatchResult[]>('/api/review/batch', pending));
  const done = results.filter(r => r.status !== 'REJECTED').map(r => r.reviewId);
  await this.db.pendingReviews.bulkDelete(done);
}
```

Playwright (cartão do PLAN):

```ts
test('revisa offline e sincroniza', async ({ page, context }) => {
  await page.goto('/review');
  await context.setOffline(true);
  for (let i = 0; i < 3; i++) {
    await page.keyboard.press(' ');
    await page.keyboard.press('3');
  }
  await context.setOffline(false);
  await expect(page.getByTestId('sync-status')).toHaveText('Sincronizado');
  // conferir no backend: 3 linhas novas em srs_review
});
```

## Armadilhas

- **Service worker só em build de produção:** `ng serve` não registra SW. O e2e roda contra `ng build` servido estático + backend.
- **Safari/iOS:** não há Background Sync; sincronize no `online` e na abertura.
- **Conflito:** revisão offline mais antiga que a última no servidor (P-04).
- **Atualização do app:** use `SwUpdate` para avisar "nova versão disponível"; sem isso o usuário fica preso numa versão velha.
- **Sessão expirada offline:** ao voltar online, o batch pode dar 401; mantenha a fila e peça login.
