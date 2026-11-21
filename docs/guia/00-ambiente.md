# 00 — Ambiente

Linux (o seu é Ubuntu-like). Tudo com gerenciador de versão, para não brigar com pacotes do sistema.

## Java 21 e Maven (SDKMAN)

```bash
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"
sdk list java | grep -i tem        # escolha a última 21.x-tem
sdk install java 21.0.<x>-tem
sdk install maven                  # só para gerar o wrapper; depois use ./mvnw
java -version                      # deve mostrar 21
```

## Node 24 LTS e Angular CLI 22

```bash
curl -fsSL https://fnm.vercel.app/install | bash   # ou nvm
fnm install 24 && fnm default 24
node -v                                            # v24.x
npm i -g @angular/cli@22
ng version                                         # confira se o Node está na lista de compatíveis
```

## Docker

```bash
# Docker Engine + plugin compose (docs.docker.com/engine/install)
docker version && docker compose version
sudo usermod -aG docker "$USER"    # depois faça logout/login
```

Para gerar imagens ARM64 numa máquina x86 (Fase 8):

```bash
docker run --privileged --rm tonistiigi/binfmt --install arm64
docker buildx create --name multi --use
docker buildx inspect --bootstrap  # deve listar linux/arm64
```

## IDE

- IntelliJ IDEA (Community serve): plugin do Spring vem no Ultimate; no Community, instale "Spring Boot Assistant" se quiser.
- VS Code: "Extension Pack for Java", "Spring Boot Extension Pack", "Angular Language Service".
- Configure a IDE para usar o JDK 21 do SDKMAN e o `./mvnw` do projeto.

## Conferência final

```bash
java -version && ./backend/mvnw -v 2>/dev/null; node -v && ng version | head -20 && docker compose version
```

(O `./backend/mvnw` só existe depois do passo 3 da Fase 0.)
