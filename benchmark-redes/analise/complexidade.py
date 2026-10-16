"""Complexidade ciclomática de McCabe (C2-M2, seção 3.4 do roteiro, decisão C).

M por função = pontos de decisão + 1. Contam: if (inclusive o do `else if`), for, while,
operador ternário, && e ||. Não contam modificadores (onlyRole, nonReentrant).

Solidity: só os contratos da pasta src/ (sem interfaces nem OpenZeppelin).
Daml [PROPOSTA, conferir na INTER-15]: if, guardas `|` de função, cada alternativa de `case`
além da primeira, `assert`/`assertMsg`/`ensure` (equivalentes ao `if (...) revert`), && e ||.

Uso: python3 analise/complexidade.py ../../projeto-inter-web3/src canton/daml
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Funcao:
    nome: str
    decisoes: int

    @property
    def m(self) -> int:
        return self.decisoes + 1


@dataclass
class Contrato:
    arquivo: str
    nome: str
    funcoes: list[Funcao] = field(default_factory=list)

    @property
    def decisoes(self) -> int:
        return sum(f.decisoes for f in self.funcoes)

    @property
    def m(self) -> int:
        return sum(f.m for f in self.funcoes)


def _sem_comentarios_e_textos(codigo: str) -> str:
    codigo = re.sub(r"/\*.*?\*/", " ", codigo, flags=re.S)
    codigo = re.sub(r"//[^\n]*", " ", codigo)
    return re.sub(r'"(?:\\.|[^"\\])*"', '""', codigo)


def _bloco(codigo: str, inicio: int) -> tuple[str, int]:
    """Corpo entre a chave em `inicio` e a chave que a fecha."""
    nivel = 0
    for i in range(inicio, len(codigo)):
        if codigo[i] == "{":
            nivel += 1
        elif codigo[i] == "}":
            nivel -= 1
            if nivel == 0:
                return codigo[inicio + 1 : i], i
    raise ValueError("chave sem fechamento")


SOL_DECISOES = re.compile(r"\bif\s*\(|\bfor\s*\(|\bwhile\s*\(|\?|&&|\|\|")


def contar_decisoes_solidity(corpo: str) -> int:
    return len(SOL_DECISOES.findall(corpo))


def analisar_solidity(arquivo: Path) -> list[Contrato]:
    codigo = _sem_comentarios_e_textos(arquivo.read_text())
    contratos = []
    for m in re.finditer(r"\b(contract|library|abstract\s+contract)\s+(\w+)[^{]*\{", codigo):
        corpo, _ = _bloco(codigo, m.end() - 1)
        c = Contrato(arquivo.name, m.group(2))
        for f in re.finditer(r"\b(function\s+(\w+)|constructor)\s*\([^)]*\)[^{;]*\{", corpo):
            nome = f.group(2) or "constructor"
            corpo_f, _ = _bloco(corpo, f.end() - 1)
            c.funcoes.append(Funcao(nome, contar_decisoes_solidity(corpo_f)))
        contratos.append(c)
    return contratos


DAML_DECISOES = re.compile(r"\bif\b|\bassert\b|\bassertMsg\b|\bensure\b|&&|\|\|")


def analisar_daml(arquivo: Path) -> list[Contrato]:
    """Cada choice, função de nível superior e o bloco `ensure` de um template contam como função."""
    linhas = arquivo.read_text().splitlines()
    linhas = [re.sub(r"--.*", "", l) for l in linhas]
    contrato = Contrato(arquivo.name, arquivo.stem)
    atual: Funcao | None = None
    for linha in linhas:
        if not linha.strip():
            continue
        cab_choice = re.match(r"\s+(?:nonconsuming\s+|preconsuming\s+|postconsuming\s+)?choice\s+(\w+)", linha)
        cab_func = re.match(r"^([a-z]\w*)\s*:", linha)
        cab_template = re.match(r"^template\s+(\w+)", linha)
        if cab_choice or cab_func or cab_template:
            nome = (cab_choice or cab_func or cab_template).group(1)
            atual = Funcao(f"template {nome}" if cab_template else nome, 0)
            contrato.funcoes.append(atual)
        if atual is None:
            continue
        atual.decisoes += len(DAML_DECISOES.findall(linha))
        # Guardas de função (`| cond = ...`) e alternativas de case (`padrão ->`).
        if re.match(r"\s+\|\s", linha):
            atual.decisoes += 1
        # Cada alternativa de `case` conta; a primeira é descontada no `case` (n alternativas = n − 1 decisões).
        if re.match(r"\s+[\w(\[][^=]*->", linha):
            atual.decisoes += 1
        if re.search(r"\bcase\b.*\bof\b", linha):
            atual.decisoes -= 1
    # Funções-tipo duplicadas (assinatura + definição) contam uma vez só.
    unicas: dict[str, Funcao] = {}
    for f in contrato.funcoes:
        if f.nome in unicas:
            unicas[f.nome].decisoes += f.decisoes
        else:
            unicas[f.nome] = f
    contrato.funcoes = list(unicas.values())
    # Templates sem `ensure` não têm código executável próprio.
    contrato.funcoes = [f for f in contrato.funcoes if not (f.nome.startswith("template ") and f.decisoes == 0)]
    return [contrato]


def analisar(pasta: Path) -> dict:
    contratos: list[Contrato] = []
    for arq in sorted(pasta.rglob("*.sol")):
        if "interfaces" in arq.parts:
            continue
        contratos += analisar_solidity(arq)
    for arq in sorted(pasta.rglob("*.daml")):
        if arq.stem.startswith("Test") or ".daml" in arq.parts:
            continue
        contratos += analisar_daml(arq)
    return {
        "pasta": str(pasta),
        "contratos": [
            {
                "contrato": c.nome,
                "funcoes": len(c.funcoes),
                "pontos_decisao": c.decisoes,
                "m_total": c.m,
                "por_funcao": {f.nome: f.m for f in c.funcoes},
            }
            for c in contratos
        ],
        "total": {
            "funcoes": sum(len(c.funcoes) for c in contratos),
            "pontos_decisao": sum(c.decisoes for c in contratos),
            "m_total": sum(c.m for c in contratos),
        },
    }


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from benchmark import repo_web3

    for p in sys.argv[1:] or [str(repo_web3() / "src")]:
        print(json.dumps(analisar(Path(p)), indent=2, ensure_ascii=False))
