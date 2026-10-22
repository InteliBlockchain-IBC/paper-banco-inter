"""Cálculos do roteiro de medição: estatísticas (seção 7), notas (seção 8) e sensibilidade (seção 9).

Funções puras sobre pandas.DataFrame e dicionários; os gráficos ficam em graficos.py.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from statistics import median

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]


def repo_web3() -> Path:
    """Repositório do contrato: WEB3_REPO (ambiente ou .env), relativo a benchmark/."""
    import os

    valor = os.environ.get("WEB3_REPO")
    env = RAIZ / ".env"
    if not valor and env.exists():
        for linha in env.read_text().splitlines():
            if linha.startswith("WEB3_REPO="):
                valor = linha.split("=", 1)[1].strip().strip('"')
    return (RAIZ / (valor or "../../projeto-inter-web3")).resolve()


CRITERIOS = ["C1", "C2", "C3", "C4", "C5"]
NOMES_CRITERIOS = {
    "C1": "Resiliência",
    "C2": "Segurança do contrato",
    "C3": "Latência",
    "C4": "Custo",
    "C5": "Compatibilidade EVM",
}
# Tipo de ambiente de cada rede no experimento. Só testnets públicas entram na comparação;
# o Anvil serve apenas de ensaio local dos coletores.
AMBIENTE = {"sepolia": "testnet", "fuji": "testnet", "monad": "testnet", "anvil": "ensaio"}

# Origem dos números de uma rede, do mais forte para o mais fraco.
#   testnet    medido pela equipe numa testnet pública (Sepolia, Fuji, Monad)
#   projetado  sem teste: valores da documentação oficial e hipóteses, no lugar da medição
#   pendente   sem teste e sem valor provisório: entra na pontuação como faixa
ROTULO_ORIGEM = {
    "testnet": "medido em testnet",
    "projetado": "projeção, sem teste",
    "pendente": "a medir",
}


def origem_rede(rede: str, medido: bool, tem_projecao: bool) -> str:
    if medido:
        return "testnet"
    return "projetado" if tem_projecao else "pendente"


LIMITE_RNF02_S = 30.0
MARCA_HORARIO_BLOCO = "horário do bloco"
FUNCOES_CICLO = ["approve", "createOffer", "acceptOffer"]


# ---------------------------------------------------------------------------
# Leitura
# ---------------------------------------------------------------------------
def carregar_medicoes(pasta: Path) -> pd.DataFrame:
    arquivos = sorted(Path(pasta).glob("medicoes_*.csv"))
    if not arquivos:
        return pd.DataFrame()
    df = pd.concat([pd.read_csv(a, dtype=str, keep_default_na=False) for a in arquivos], ignore_index=True)
    for col in ["latencia_s", "gas_used", "gas_limit", "gas_price_testnet", "taxa_nativa", "lote", "rodada"]:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def janela_coleta_testnets(pasta: Path) -> tuple[str, str] | None:
    """Início da primeira e fim da última coleta nas testnets (metadados da seção 6.2)."""
    inicios, fins = [], []
    for arq in Path(pasta).glob("metadados_*.json"):
        m = json.loads(arq.read_text())
        if AMBIENTE.get(m.get("rede")) != "testnet":
            continue
        for j in (m.get("janelas") or {}).values():
            inicios.append(j["inicio_utc"])
            fins.append(j["fim_utc"])
    return (min(inicios), max(fins)) if inicios else None


def carregar_precos(pasta: Path) -> dict:
    """Mediana das amostras de preço de gas e cotação (seção 3.3) por rede.

    Usa só o arquivo mais recente: a referência é a janela da coleta das testnets; arquivos de
    outros dias ficam em dados/ como registro.
    """
    arquivos = sorted(Path(pasta).glob("precos_referencia_*.json"))
    amostras = json.loads(arquivos[-1].read_text())["amostras"] if arquivos else []
    # Só as amostras dentro da janela de coleta (com 5 min de folga antes, por causa da 1ª amostra).
    janela = janela_coleta_testnets(pasta)
    if janela:
        from datetime import datetime, timedelta
        ini = (datetime.fromisoformat(janela[0].replace("Z", "+00:00")) - timedelta(minutes=5)).isoformat()
        dentro = [a for a in amostras if ini <= a["momento_utc"].replace("Z", "+00:00") <= janela[1].replace("Z", "+00:00")]
        amostras = dentro or amostras
    por_rede: dict[str, dict] = {}
    for a in amostras:
        for rede, v in a["redes"].items():
            if "gas_preco_wei" not in v:
                continue
            p = por_rede.setdefault(rede, {"gas": [], "usd": [], "brl": [], "momentos": []})
            p["gas"].append(int(v["gas_preco_wei"]))
            if v.get("cotacao_usd") is not None:
                p["usd"].append(float(v["cotacao_usd"]))
            if v.get("cotacao_brl") is not None:
                p["brl"].append(float(v["cotacao_brl"]))
            p["momentos"].append(a["momento_utc"])
    return {
        r: {
            "gas_preco_wei": median(p["gas"]),
            "cotacao_usd": median(p["usd"]) if p["usd"] else None,
            "cotacao_brl": median(p["brl"]) if p["brl"] else None,
            "amostras": len(p["gas"]),
            "janela": [min(p["momentos"]), max(p["momentos"])],
        }
        for r, p in por_rede.items()
    }


# ---------------------------------------------------------------------------
# Estatísticas (seção 7)
# ---------------------------------------------------------------------------
def _sem_horario_de_bloco(df: pd.DataFrame) -> pd.DataFrame:
    return df[~df["nome_erro"].str.contains(MARCA_HORARIO_BLOCO, regex=False)]


def latencias_aceite_t1(df: pd.DataFrame, rede: str) -> np.ndarray:
    sel = df[(df.rede == rede) & (df.teste == "T1") & (df.funcao == "acceptOffer") & (df.status == "confirmada")]
    return _sem_horario_de_bloco(sel)["latencia_s"].dropna().to_numpy()


def estatisticas(valores: np.ndarray) -> dict:
    if len(valores) == 0:
        return {"n": 0}
    return {
        "n": int(len(valores)),
        "media": float(np.mean(valores)),
        "mediana": float(np.median(valores)),
        "p95": float(np.percentile(valores, 95)),
        "maximo": float(np.max(valores)),
        "prop_ate_30s": float(np.mean(valores <= LIMITE_RNF02_S)),
    }


def latencia_sob_carga(df: pd.DataFrame, rede: str) -> dict:
    sel = _sem_horario_de_bloco(df[(df.rede == rede) & (df.teste == "T2") & (df.status == "confirmada")])
    return {int(l): estatisticas(g["latencia_s"].dropna().to_numpy()) for l, g in sel.groupby("lote")}


def taxa_sucesso(df: pd.DataFrame) -> dict:
    """C1 = confirmadas ÷ (submetidas − falhas A, B e C) × 100 (seção 3.1). X fica fora e é reportado."""
    t = df[df.teste == "T2"]
    if t.empty:
        return {"n": 0}
    contagem = t["categoria_falha"].value_counts().to_dict()
    confirmadas = int((t.status == "confirmada").sum())
    excluidas = sum(contagem.get(c, 0) for c in ["A", "B", "C", "X"])
    denominador = len(t) - excluidas
    return {
        "n": int(len(t)),
        "confirmadas": confirmadas,
        "falhas": {c: int(contagem.get(c, 0)) for c in ["A", "B", "C", "D", "X"]},
        "denominador": int(denominador),
        "taxa": float(confirmadas / denominador * 100) if denominador else None,
    }


def taxa_por_lote(df: pd.DataFrame, rede: str) -> dict:
    t = df[(df.rede == rede) & (df.teste == "T2")]
    return {int(l): taxa_sucesso(g)["taxa"] for l, g in t.groupby("lote")}


def custo_usd(gas: float, preco_wei: float, cotacao_usd: float) -> float:
    return gas * preco_wei / 1e18 * cotacao_usd


def custos(df: pd.DataFrame, rede: str, cobranca: str, preco: dict | None) -> dict:
    """C4-M1: custo médio por função e por ciclo completo, em USD (seção 3.3).

    `cobranca`: 'gasUsed' (Ethereum, Avalanche) ou 'gasLimit' (Monad cobra o limite).
    """
    t1 = df[(df.rede == rede) & (df.teste == "T1") & (df.status == "confirmada")].copy()
    if t1.empty:
        return {}
    coluna_gas = "gas_limit" if cobranca == "gasLimit" else "gas_used"
    if preco and preco.get("cotacao_usd"):
        t1["usd"] = t1[coluna_gas].astype(float) * preco["gas_preco_wei"] / 1e18 * preco["cotacao_usd"]
    else:
        return {"gas_medio": t1.groupby("funcao")[coluna_gas].mean().to_dict(), "sem_preco": True}
    por_funcao = t1.groupby("funcao")["usd"].mean().to_dict()
    gas_por_funcao = t1.groupby("funcao")[coluna_gas].mean().to_dict()
    ciclos = t1[t1.funcao.isin(FUNCOES_CICLO)].groupby("rodada")
    completos = [g["usd"].sum() for _, g in ciclos if set(g.funcao) == set(FUNCOES_CICLO)]
    gas_ciclos = [g[coluna_gas].sum() for _, g in ciclos if set(g.funcao) == set(FUNCOES_CICLO)]
    return {
        "coluna_gas": coluna_gas,
        "usd_por_funcao": por_funcao,
        "gas_por_funcao": gas_por_funcao,
        "ciclos_completos": len(completos),
        "ciclo_usd_medio": float(np.mean(completos)) if completos else None,
        "ciclo_gas_medio": float(np.mean(gas_ciclos)) if gas_ciclos else None,
    }


# ---------------------------------------------------------------------------
# Notas (seção 8)
# ---------------------------------------------------------------------------
def normalizar(valores: dict[str, float], sentido: str) -> dict[str, float]:
    """Min-max (seção 8.1). sentido: 'beneficio' ou 'custo'. Empate (máx = mín): todos recebem 1."""
    conhecidos = {k: v for k, v in valores.items() if v is not None and not (isinstance(v, float) and math.isnan(v))}
    if not conhecidos:
        return {}
    mn, mx = min(conhecidos.values()), max(conhecidos.values())
    if mx == mn:
        return {k: 1.0 for k in conhecidos}
    if sentido == "beneficio":
        return {k: (v - mn) / (mx - mn) for k, v in conhecidos.items()}
    return {k: (mx - v) / (mx - mn) for k, v in conhecidos.items()}


@dataclass
class Celula:
    valor: float | None  # nota de 0 a 1; None = pendente
    origem: str  # medido, declarado, pendente


@dataclass
class Matriz:
    redes: list[str]
    criterios: dict[str, dict[str, Celula]] = field(default_factory=dict)  # criterio -> rede -> célula
    brutos: dict[str, dict[str, float | None]] = field(default_factory=dict)

    def nota(self, criterio: str, rede: str) -> Celula:
        return self.criterios[criterio][rede]


def _media_celulas(celulas: list[Celula]) -> Celula:
    """Média simples das medidas de um critério (seção 8.3); pendente se alguma medida falta."""
    if any(c.valor is None for c in celulas):
        conhecidas = [c.valor for c in celulas if c.valor is not None]
        # Guarda o intervalo possível: as medidas pendentes podem ir de 0 a 1.
        return Celula(None, "pendente:" + json.dumps([sum(conhecidas) / len(celulas), (sum(conhecidas) + len(celulas) - len(conhecidas)) / len(celulas)]))
    origens = {c.origem for c in celulas}
    return Celula(sum(c.valor for c in celulas) / len(celulas), "medido" if origens == {"medido"} else "declarado" if origens == {"declarado"} else "misto")


def montar_matriz(redes: list[str], brutos: dict, origens: dict, declarados: dict) -> Matriz:
    """brutos: {'C1': {rede: taxa}, 'C3': {rede: s}, 'C4M1': {rede: usd}, 'C4M2': {rede: usd/mês}, 'C2M2': {rede: M}}."""
    m = Matriz(redes)
    m.brutos = brutos

    def celulas(chave: str, sentido: str) -> dict[str, Celula]:
        n = normalizar({r: brutos.get(chave, {}).get(r) for r in redes}, sentido)
        return {r: Celula(n.get(r), origens.get(chave, {}).get(r, "pendente") if r in n else "pendente") for r in redes}

    c1 = celulas("C1", "beneficio")
    c3 = celulas("C3", "custo")
    c4m1 = celulas("C4M1", "custo")
    c4m2 = celulas("C4M2", "custo")
    c2m2 = celulas("C2M2", "custo")
    versao = declarados["versao_codigo"]
    c2m1 = {r: Celula(declarados["C2_M1_verificacao_formal"][versao[r]]["nota"], "declarado") for r in redes}
    c2m3 = {r: Celula(declarados["C2_M3_confidencialidade"][r]["nota"], "declarado") for r in redes}
    c5 = {r: Celula(declarados["C5_compatibilidade_evm"][r]["nota"], "declarado") for r in redes}

    # C4-M2 pendente para todas as redes = medida ainda não levantada: fica fora da média até existir.
    sem_infra = all(c.valor is None for c in c4m2.values())
    m.criterios = {
        "C1": c1,
        "C2": {r: _media_celulas([c2m1[r], c2m2[r], c2m3[r]]) for r in redes},
        "C3": c3,
        "C4": {r: (c4m1[r] if sem_infra else _media_celulas([c4m1[r], c4m2[r]])) for r in redes},
        "C5": c5,
    }
    m.medidas = {"C2-M1": c2m1, "C2-M2": c2m2, "C2-M3": c2m3, "C4-M1": c4m1, "C4-M2": c4m2}
    m.sem_infra = sem_infra
    return m


def intervalo(c: Celula) -> tuple[float, float]:
    if c.valor is not None:
        return c.valor, c.valor
    if c.origem.startswith("pendente:"):
        lo, hi = json.loads(c.origem.split(":", 1)[1])
        return lo, hi
    return 0.0, 1.0


def pontuar(m: Matriz, pesos: dict[str, float]) -> dict[str, dict]:
    """Pontuação ponderada (0 a 100). Células pendentes viram intervalo [mínimo, máximo]."""
    out = {}
    for r in m.redes:
        lo = hi = 0.0
        contrib = {}
        pendentes = []
        for c in CRITERIOS:
            a, b = intervalo(m.nota(c, r))
            lo += pesos[c] * a * 100
            hi += pesos[c] * b * 100
            contrib[c] = pesos[c] * a * 100
            if m.nota(c, r).valor is None:
                pendentes.append(c)
        out[r] = {"minimo": lo, "maximo": hi, "contribuicao_conhecida": contrib, "pendentes": pendentes, "completo": not pendentes}
    return out


def ranking(pontos: dict[str, float]) -> list[str]:
    return sorted(pontos, key=lambda r: -pontos[r])


# ---------------------------------------------------------------------------
# Sensibilidade (seção 9)
# ---------------------------------------------------------------------------
def renormalizar(pesos: dict[str, float]) -> dict[str, float]:
    s = sum(pesos.values())
    return {k: v / s for k, v in pesos.items()}


def cenarios_sensibilidade(pesos: dict[str, float]) -> list[tuple[str, dict[str, float]]]:
    cen = [("Base", dict(pesos)), ("S1 pesos iguais", {c: 1 / len(pesos) for c in pesos})]
    for c in pesos:
        for fator, rot in [(1.5, "+50%"), (0.5, "−50%")]:
            p = dict(pesos)
            p[c] = p[c] * fator
            cen.append((f"S2 {c} {rot}", renormalizar(p)))
    for c in pesos:
        p = {k: v for k, v in pesos.items() if k != c}
        p = renormalizar(p)
        p[c] = 0.0
        cen.append((f"S3 sem {c}", p))
    return cen


def sensibilidade(m: Matriz, pesos: dict[str, float], usar: str = "medio") -> list[dict]:
    """Ranking em cada cenário. `usar`: 'minimo', 'maximo' ou 'medio' do intervalo das células pendentes."""
    base = None
    linhas = []
    for nome, p in cenarios_sensibilidade(pesos):
        pts = pontuar(m, p)
        valor = {r: (v["minimo"] + v["maximo"]) / 2 if usar == "medio" else v[usar] for r, v in pts.items()}
        ordem = ranking(valor)
        if base is None:
            base = ordem[0]
        linhas.append({"cenario": nome, "pesos": p, "pontos": valor, "ordem": ordem, "primeiro_mudou": ordem[0] != base})
    return linhas
