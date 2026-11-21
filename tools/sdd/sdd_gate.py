#!/usr/bin/env python3
"""Gate de congelamento dos testes protegidos de uma tarefa SDD.

Uso:
  python3 sdd_gate.py <SLUG>                 # verifica
  python3 sdd_gate.py <SLUG> --congelar      # grava hashes atuais dos protegidos

Lê `.sdd/<SLUG>/spec/ficha.md` e o campo `protegidos:` (lista YAML simples ou
linhas com `- caminho`). Para cada caminho, calcula SHA-256 e compara com
`.sdd/<SLUG>/spec/.gate.json`.

Saída: PASS ou FAIL n=<N>. Código 0 em PASS, 1 em FAIL, 2 em erro de uso.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


def carregar_protegidos(ficha: Path) -> list[str]:
    texto = ficha.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", texto, re.DOTALL)
    if not m:
        return []
    frontmatter = m.group(1)
    # procura linha protegidos: ... ou bloco com - item
    m_inline = re.search(r"^protegidos:\s*\[(.*?)\]\s*(?:#.*)?$", frontmatter, re.MULTILINE)
    if m_inline:
        bruto = m_inline.group(1)
        itens = [x.strip().strip("'\"") for x in bruto.split(",")]
        return [x for x in itens if x]
    m_bloco = re.search(
        r"^protegidos:\s*(?:#.*)?\n((?:\s*-\s*.+\n?)+)", frontmatter, re.MULTILINE
    )
    if m_bloco:
        linhas = m_bloco.group(1).splitlines()
        return [re.sub(r"^\s*-\s*", "", linha).strip().strip("'\"") for linha in linhas if linha.strip()]
    return []


def sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(65536), b""):
            h.update(bloco)
    return h.hexdigest()


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("uso: sdd_gate.py <SLUG> [--congelar]", file=sys.stderr)
        return 2
    slug = argv[1]
    congelar = "--congelar" in argv[2:]

    raiz = Path(".sdd") / slug
    ficha = raiz / "spec" / "ficha.md"
    gate_arq = raiz / "spec" / ".gate.json"

    if not ficha.is_file():
        print(f"FAIL n=1\n- ficha ausente: {ficha}")
        return 1

    protegidos = carregar_protegidos(ficha)
    if not protegidos:
        if congelar:
            gate_arq.write_text("{}\n", encoding="utf-8")
            print("PASS")
            return 0
        print("PASS")
        return 0

    atuais: dict[str, str] = {}
    faltando: list[str] = []
    for rel in protegidos:
        p = Path(rel)
        if not p.is_file():
            faltando.append(rel)
            continue
        atuais[rel] = sha256(p)

    if congelar:
        if faltando:
            print(f"FAIL n={len(faltando)}")
            for f in faltando:
                print(f"- arquivo protegido ausente: {f}")
            return 1
        gate_arq.write_text(json.dumps(atuais, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("PASS")
        return 0

    if not gate_arq.is_file():
        print("FAIL n=1\n- gate não congelado (rode com --congelar)")
        return 1

    congelados: dict[str, str] = json.loads(gate_arq.read_text(encoding="utf-8"))
    problemas: list[str] = []
    for rel in protegidos:
        if rel in faltando:
            problemas.append(f"protegido ausente: {rel}")
            continue
        esperado = congelados.get(rel)
        if esperado is None:
            problemas.append(f"protegido fora do gate (recongele): {rel}")
        elif esperado != atuais[rel]:
            problemas.append(f"protegido alterado: {rel}")

    if problemas:
        print(f"FAIL n={len(problemas)}")
        for p in problemas:
            print(f"- {p}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
