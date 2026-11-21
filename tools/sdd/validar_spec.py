#!/usr/bin/env python3
"""Valida a estrutura mínima de uma spec SDD.

Uso: python3 validar_spec.py <caminho/.sdd/{SLUG}>

Checa:
- ficha.md com frontmatter YAML e campos obrigatórios
- descoberta.md existe e não está vazio quando etapa > descoberta
- mapa.md idem para etapa > mapa
- plano.md com pelo menos uma fase quando etapa > planejamento
- jornadas/ com pelo menos um arquivo quando etapa >= spec
- contrato.md e testes.md existem quando etapa >= spec

Saída: imprime PASS ou FAIL n=<N> e lista problemas.
Sai com código 0 em PASS, 1 em FAIL.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ETAPAS_ORDEM = [
    "descoberta",
    "mapa",
    "planejamento",
    "spec",
    "testes",
    "codigo",
    "validacao",
    "concluida",
]


def parse_frontmatter(texto: str) -> dict[str, str]:
    m = re.match(r"^---\n(.*?)\n---", texto, re.DOTALL)
    if not m:
        return {}
    campos: dict[str, str] = {}
    for linha in m.group(1).splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        if ":" not in linha:
            continue
        chave, _, valor = linha.partition(":")
        valor = re.sub(r"\s+#.*$", "", valor)
        campos[chave.strip()] = valor.strip().strip("'\"")
    return campos


def idx_etapa(nome: str) -> int:
    try:
        return ETAPAS_ORDEM.index(nome)
    except ValueError:
        return -1


def validar(raiz: Path) -> list[str]:
    problemas: list[str] = []
    spec = raiz / "spec"
    ficha = spec / "ficha.md"

    if not ficha.is_file():
        return [f"{ficha} não existe"]

    campos = parse_frontmatter(ficha.read_text(encoding="utf-8"))
    for obrig in ("slug", "titulo", "etapa", "status"):
        if obrig not in campos:
            problemas.append(f"ficha.md: frontmatter sem campo '{obrig}'")

    etapa = campos.get("etapa", "")
    if idx_etapa(etapa) < 0:
        problemas.append(f"ficha.md: etapa desconhecida '{etapa}'")
        return problemas

    nivel = idx_etapa(etapa)

    def arquivo_nao_vazio(p: Path, label: str) -> None:
        if not p.is_file() or not p.read_text(encoding="utf-8").strip():
            problemas.append(f"{label} ausente ou vazio: {p}")

    if nivel > idx_etapa("descoberta"):
        arquivo_nao_vazio(spec / "descoberta.md", "descoberta")

    if nivel > idx_etapa("mapa"):
        arquivo_nao_vazio(spec / "mapa.md", "mapa")

    if nivel > idx_etapa("planejamento"):
        plano = spec / "plano.md"
        arquivo_nao_vazio(plano, "plano")
        if plano.is_file() and not re.search(r"^## (Passo|Fase) 1\b", plano.read_text(encoding="utf-8"), re.MULTILINE):
            problemas.append("plano.md: sem seção '## Passo 1 —' (ou '## Fase 1 —')")

    if nivel >= idx_etapa("spec"):
        jornadas = spec / "jornadas"
        if not jornadas.is_dir() or not any(jornadas.glob("J*.md")):
            problemas.append("jornadas/: nenhum arquivo 'J*.md'")
        arquivo_nao_vazio(spec / "contrato.md", "contrato")
        arquivo_nao_vazio(spec / "testes.md", "testes")
        testes = spec / "testes.md"
        if campos.get("status") == "aprovada" and testes.is_file() and "a calcular" in testes.read_text(encoding="utf-8"):
            problemas.append("testes.md: spec aprovada ainda tem valor 'a calcular'")

    return problemas


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("uso: validar_spec.py <caminho/.sdd/{SLUG}>", file=sys.stderr)
        return 2
    raiz = Path(argv[1]).expanduser().resolve()
    if not raiz.is_dir():
        print(f"FAIL n=1\n- diretório não existe: {raiz}")
        return 1
    problemas = validar(raiz)
    if not problemas:
        print("PASS")
        return 0
    print(f"FAIL n={len(problemas)}")
    for p in problemas:
        print(f"- {p}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
