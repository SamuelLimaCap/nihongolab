#!/usr/bin/env python3
"""Mantém `.sdd/PAINEL.md` com uma linha por tarefa.

Uso:
  python3 tarefa_status.py --painel       # regenera .sdd/PAINEL.md

Lê cada `.sdd/<SLUG>/spec/ficha.md`, extrai `slug`, `titulo`, `etapa`, `status`,
`fase_atual`, e escreve a tabela ordenada.
"""
from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path


def parse_frontmatter(texto: str) -> dict[str, str]:
    m = re.match(r"^---\n(.*?)\n---", texto, re.DOTALL)
    if not m:
        return {}
    campos: dict[str, str] = {}
    for linha in m.group(1).splitlines():
        if ":" not in linha or linha.lstrip().startswith("#"):
            continue
        chave, _, valor = linha.partition(":")
        valor = re.sub(r"\s+#.*$", "", valor)
        campos[chave.strip()] = valor.strip().strip("'\"")
    return campos


def gerar_painel(raiz: Path) -> str:
    linhas = [
        "# Painel de tarefas SDD",
        "",
        f"_Atualizado: {datetime.now().strftime('%Y-%m-%d %H:%M')}_",
        "",
        "| Slug | Título | Etapa | Status | Passo | Em andamento por |",
        "|---|---|---|---|---|---|",
    ]
    tarefas: list[dict[str, str]] = []
    for ficha in sorted(raiz.glob("*/spec/ficha.md")):
        campos = parse_frontmatter(ficha.read_text(encoding="utf-8"))
        if not campos:
            continue
        tarefas.append(campos)
    tarefas.sort(key=lambda c: c.get("slug", ""))
    for c in tarefas:
        linhas.append(
            "| {slug} | {titulo} | {etapa} | {status} | {fase} | {quem} |".format(
                slug=c.get("slug", "?"),
                titulo=c.get("titulo", "?"),
                etapa=c.get("etapa", "?"),
                status=c.get("status", "?"),
                fase=c.get("fase_atual", "-"),
                quem=c.get("em_andamento_por", "") or "—",
            )
        )
    linhas.append("")
    return "\n".join(linhas)


def main(argv: list[str]) -> int:
    if "--painel" not in argv:
        print("uso: tarefa_status.py --painel", file=sys.stderr)
        return 2
    raiz = Path(".sdd")
    if not raiz.is_dir():
        print("nada a fazer: .sdd/ não existe")
        return 0
    conteudo = gerar_painel(raiz)
    (raiz / "PAINEL.md").write_text(conteudo, encoding="utf-8")
    print(f"painel atualizado: {raiz / 'PAINEL.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
