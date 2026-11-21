# Fase 3 — Frontend base (roteiro)

Spec: `.sdd/f3-frontend-base/` (em descoberta).

## Ordem sugerida

1. Design tokens e tema escuro (`src/styles/_tokens.scss` + `styles.scss`), fontes self-hosted.
2. Shell responsivo (menu lateral ≥ 768 px, abas abaixo).
3. `AuthService`, guard, interceptor de 401, tela de Login.
4. Tela Início (pendentes por deck).
5. Tela Revisão (com teclado).
6. Tela Kana (tabela + quiz).
7. Testes de componente de Revisão e Início.

## Trechos-chave

Tokens:

```scss
:root {
  --bg: #0f1115;
  --surface: #171a21;
  --border: #262a33;
  --text: #e7e9ee;
  --text-muted: #9aa1ad;
  --accent: #ff7a70;
  --font-ui: 'Inter', system-ui, sans-serif;
  --font-jp: 'Noto Sans JP', sans-serif;
  --tap: 44px;
}
```

`app.config.ts`:

```ts
export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(withInterceptors([unauthorizedInterceptor])),
    provideAppInitializer(() => inject(AuthService).load()),
  ],
};
```

O `HttpClient` já lê `XSRF-TOKEN` e manda `X-XSRF-TOKEN` em POST/PUT/DELETE para URL relativa; os nomes padrão do Angular são os mesmos do Spring.

`AuthService` com signals:

```ts
@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  readonly user = signal<Me | null | undefined>(undefined);   // undefined = ainda não sabe
  readonly loggedIn = computed(() => !!this.user());

  async load(): Promise<void> {
    try {
      this.user.set(await firstValueFrom(this.http.get<Me>('/api/me')));
    } catch {
      this.user.set(null);
    }
  }

  login(provider: 'google' | 'github'): void {
    window.location.href = `/oauth2/authorization/${provider}`;
  }

  async logout(): Promise<void> {
    await firstValueFrom(this.http.post('/api/logout', null));
    this.user.set(null);
  }
}
```

Guard:

```ts
export const authGuard: CanActivateFn = () =>
  inject(AuthService).loggedIn() ? true : inject(Router).createUrlTree(['/login']);
```

Revisão por teclado:

```ts
@Component({
  selector: 'app-review',
  host: { '(document:keydown)': 'onKey($event)' },
  templateUrl: './review.html',
})
export class Review {
  protected readonly revealed = signal(false);

  onKey(e: KeyboardEvent): void {
    if (e.key === ' ') { e.preventDefault(); this.revealed.set(true); return; }
    const grade = ({ '1': 'AGAIN', '2': 'HARD', '3': 'GOOD', '4': 'EASY' } as const)[e.key as '1'];
    if (grade && this.revealed()) this.answer(grade);
  }
  // answer(): POST /api/review com reviewId = crypto.randomUUID()
}
```

## Armadilhas

- **Noto Sans JP:** o arquivo completo tem vários MB. Use subsets por `unicode-range` (os pacotes `@fontsource/noto-sans-jp` já vêm assim) e `font-display: swap`.
- **Fontes externas:** não use Google Fonts por CDN; a CSP da Fase 8 bloqueia e o PWA offline precisa delas em cache.
- **Teclas com foco em input:** ignore atalhos quando o foco estiver num campo de texto.
- **`reviewId`:** gere uma vez por resposta; se o POST falhar e for reenviado, reaproveite o mesmo (idempotência).
- **Zoneless:** atualize estado com signals; mutar objeto comum não re-renderiza.

## Testes (prévia)

- Revisão: espaço revela; `3` envia `GOOD` com um `reviewId` UUID; próximo cartão aparece; lista vazia mostra "nada para revisar".
- Início: mostra a contagem de pendentes por deck a partir de um `HttpTestingController`.
