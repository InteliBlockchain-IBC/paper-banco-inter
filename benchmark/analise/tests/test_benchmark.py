"""Testes dos cálculos do roteiro (seções 3, 7, 8 e 9)."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import benchmark as bm  # noqa: E402
import complexidade  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]


def test_normalizacao_exemplo_do_roteiro():
    # Seção 8.1: latências de 2, 5 e 12 s (custo) viram 1,0; 0,7; 0,0.
    n = bm.normalizar({"r1": 2, "r2": 5, "r3": 12}, "custo")
    assert n == pytest.approx({"r1": 1.0, "r2": 0.7, "r3": 0.0})


def test_normalizacao_beneficio_e_empate():
    assert bm.normalizar({"a": 90, "b": 100}, "beneficio") == {"a": 0.0, "b": 1.0}
    assert bm.normalizar({"a": 100, "b": 100}, "beneficio") == {"a": 1.0, "b": 1.0}


def test_renormalizacao_exemplo_do_roteiro():
    # Seção 9, S2 com latência +50%: C3 vai de 15,78% para 21,94%.
    pesos = {"C1": 0.2978, "C2": 0.2978, "C3": 0.1578, "C4": 0.1578, "C5": 0.0888}
    p = dict(pesos)
    p["C3"] *= 1.5
    r = bm.renormalizar(p)
    assert r["C3"] == pytest.approx(0.2194, abs=1e-4)
    assert r["C1"] == pytest.approx(0.2760, abs=1e-4)
    assert sum(r.values()) == pytest.approx(1.0)


def test_cenarios_de_sensibilidade_sao_16_mais_base():
    pesos = {"C1": 0.2978, "C2": 0.2978, "C3": 0.1578, "C4": 0.1578, "C5": 0.0888}
    assert len(bm.cenarios_sensibilidade(pesos)) == 17


def _t2(categorias):
    linhas = [{"teste": "T2", "status": "confirmada" if c == "" else "falha", "categoria_falha": c} for c in categorias]
    return pd.DataFrame(linhas)


def test_taxa_de_sucesso_exclui_a_b_c_e_conta_d():
    # 8 confirmadas, 1 A, 1 C, 2 D: 8 ÷ (12 − 2) = 80%.
    df = _t2([""] * 8 + ["A", "C", "D", "D"])
    t = bm.taxa_sucesso(df)
    assert t["denominador"] == 10
    assert t["taxa"] == pytest.approx(80.0)


def test_estatisticas_e_proporcao_rnf02():
    s = bm.estatisticas(np.array([1.0, 2.0, 3.0, 40.0]))
    assert s["mediana"] == 2.5
    assert s["maximo"] == 40.0
    assert s["prop_ate_30s"] == 0.75


def test_custo_monad_usa_gas_limit():
    df = pd.DataFrame([
        {"rede": "x", "teste": "T1", "status": "confirmada", "funcao": f, "rodada": 1, "gas_used": 100.0, "gas_limit": 120.0}
        for f in bm.FUNCOES_CICLO
    ])
    preco = {"gas_preco_wei": 1e9, "cotacao_usd": 1.0}
    usado = bm.custos(df, "x", "gasUsed", preco)["ciclo_usd_medio"]
    limite = bm.custos(df, "x", "gasLimit", preco)["ciclo_usd_medio"]
    assert limite / usado == pytest.approx(1.2)
    assert bm.custos(df, "x", "gratis", preco)["ciclo_usd_medio"] == 0.0


def test_complexidade_solidity_bate_com_contagem_preliminar():
    pasta = bm.repo_web3() / "src"
    if not pasta.exists():
        pytest.skip("repositório do contrato ausente")
    total = complexidade.analisar(pasta)["total"]
    assert total == {"funcoes": 24, "pontos_decisao": 25, "m_total": 49}


def test_intervalo_de_celula_pendente():
    c = bm.Celula(None, "pendente")
    assert bm.intervalo(c) == (0.0, 1.0)
