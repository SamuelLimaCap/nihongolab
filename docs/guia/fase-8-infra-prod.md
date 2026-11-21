# Fase 8 — Infra de produção + observabilidade (roteiro)

Spec: `.sdd/f8-infra-prod/` (em descoberta). Antes de começar: reavaliar Spring Boot 4.x (D-01) e Promtail × Alloy (P-01).

## Ordem sugerida

1. Dockerfiles (backend e frontend) com build `linux/arm64`.
2. `infra/docker-compose.yml` com perfis `core` e `full`, `mem_limit` em todos.
3. Nginx: SPA, proxy, cache, headers de segurança.
4. TLS.
5. Prometheus + Grafana (dashboard como código) + Loki + coletor de logs.
6. Backup diário + teste de restore.
7. Workflow de deploy.
8. `docs/deploy.md` (VPS e plano B).

## Trechos-chave

`backend/Dockerfile`:

```dockerfile
FROM eclipse-temurin:21-jdk AS build
WORKDIR /src
COPY .mvn .mvn
COPY mvnw pom.xml ./
RUN ./mvnw -B -q dependency:go-offline
COPY src src
# os testes já rodaram no CI antes deste build
RUN ./mvnw -B -q package -DskipTests \
 && java -Djarmode=tools -jar target/nihongolab-backend-*.jar extract --layers --launcher --destination /extracted

FROM eclipse-temurin:21-jre
RUN useradd --system --uid 10001 app
WORKDIR /app
COPY --from=build /extracted/dependencies/ ./
COPY --from=build /extracted/spring-boot-loader/ ./
COPY --from=build /extracted/snapshot-dependencies/ ./
COPY --from=build /extracted/application/ ./
USER app
ENV JAVA_TOOL_OPTIONS="-XX:MaxRAMPercentage=75"
EXPOSE 8080 8081
ENTRYPOINT ["java", "org.springframework.boot.loader.launch.JarLauncher"]
```

Build: `docker buildx build --platform linux/arm64 -t ghcr.io/<usuario>/nihongolab-backend:<sha> --push backend`.

Actuator interno (`application-prod.yml`):

```yaml
management:
  server:
    port: 8081       # não publicado pelo nginx; só o Prometheus acessa na rede do compose
```

Nginx (trechos):

```nginx
location / {
    try_files $uri $uri/ /index.html;
}
location ~* \.(?:js|css|woff2)$ {
    add_header Cache-Control "public, max-age=31536000, immutable";
}
location = /index.html       { add_header Cache-Control "no-cache"; }
location = /ngsw.json        { add_header Cache-Control "no-cache"; }
location = /ngsw-worker.js   { add_header Cache-Control "no-cache"; }
location ~ ^/(api|oauth2|login)/ {
    proxy_pass http://backend:8080;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
add_header Content-Security-Policy "default-src 'self'; img-src 'self' data: https:; media-src 'self' blob:; connect-src 'self'; style-src 'self' 'unsafe-inline'; font-src 'self'; frame-ancestors 'none'" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Content-Type-Options nosniff always;
add_header Referrer-Policy strict-origin-when-cross-origin always;
```

No backend: `server.forward-headers-strategy: framework` para o redirect do OAuth sair com `https`.

Atenção: `add_header` dentro de um `location` substitui os do nível de cima. Repita os headers de segurança (ou use um `include`) nos `location` que têm `add_header` próprio.

Compose (trecho):

```yaml
services:
  backend:
    image: ghcr.io/<usuario>/nihongolab-backend:${TAG}
    profiles: [core, full]
    env_file: .env
    mem_limit: 1g
    depends_on:
      postgres: { condition: service_healthy }
      redis: { condition: service_healthy }
  prometheus:
    image: prom/prometheus
    profiles: [full]
    mem_limit: 512m
```

Orçamento sugerido de memória (NFR-RES-01, total ≤ 8 GB): backend 1 GB, postgres 1 GB, redis 256 MB, nginx 128 MB, prometheus 512 MB, grafana 256 MB, loki 512 MB, coletor 256 MB.

Backup (container com cron):

```bash
pg_dump -Fc -h postgres -U "$POSTGRES_USER" "$POSTGRES_DB" > "/backups/nihongolab-$(date +%F).dump"
find /backups -name 'nihongolab-*.dump' -mtime +7 -delete
```

Restore de teste: `pg_restore -c -d <banco_vazio> arquivo.dump` e conferir contagens.

## Armadilhas

- **`add_header` herdado:** ver acima.
- **CSP e vídeo:** sem `media-src blob:` o player da Fase 4 para de funcionar em prod.
- **Service worker em cache:** `ngsw-worker.js` cacheado deixa usuários presos numa versão.
- **Outbox crescendo:** publicações concluídas acumulam em `event_publication`; agende limpeza (> 7 dias).
- **QEMU lento:** build ARM64 emulado demora; use cache do buildx (`cache-from/to: type=gha`) no GitHub Actions ou runner ARM.
- **Segredos:** `.env` de produção só na VPS e nos GitHub Secrets.
