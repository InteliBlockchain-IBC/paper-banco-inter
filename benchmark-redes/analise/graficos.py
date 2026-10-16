"""Gráficos do artigo (PNG). Cinza para os dados, uma cor de destaque para a rede líder."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from benchmark import CRITERIOS, LIMITE_RNF02_S, NOMES_CRITERIOS  # noqa: E402

CINZA = "#8a8f98"
CINZA_CLARO = "#c9ccd1"
DESTAQUE = "#2f6fdb"
TEXTO = "#1f2328"
TONS_CRITERIOS = ["#1f4e9c", "#2f6fdb", "#6b9bea", "#a9c4f2", "#d5e3fa"]

plt.rcParams.update({
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": CINZA,
    "axes.labelcolor": TEXTO,
    "xtick.color": TEXTO,
    "ytick.color": TEXTO,
    "figure.dpi": 150,
    "savefig.bbox": "tight",
})


def latencia_t1(lat: dict[str, np.ndarray], nomes: dict, destaque: str | None, arquivo: Path) -> None:
    redes = [r for r in lat if len(lat[r])]
    if not redes:
        return
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    rng = np.random.default_rng(7)
    for i, r in enumerate(redes):
        v = lat[r]
        cor = DESTAQUE if r == destaque else CINZA
        ax.scatter(rng.uniform(-0.15, 0.15, len(v)) + i, v, s=14, color=cor, alpha=0.7, linewidths=0)
        ax.hlines(np.median(v), i - 0.28, i + 0.28, color=TEXTO, linewidth=1.6)
        ax.text(i + 0.32, np.median(v), f"{np.median(v):.2f} s", va="center", fontsize=9, color=TEXTO)
    ax.axhline(LIMITE_RNF02_S, color=CINZA, linestyle="--", linewidth=1)
    ax.text(len(redes) - 0.5, LIMITE_RNF02_S * 1.08, "RNF02: 30 s", ha="right", fontsize=9, color=CINZA)
    ax.set_yscale("log")
    ax.set_xticks(range(len(redes)), [nomes.get(r, r) for r in redes])
    ax.set_ylabel("Latência do acceptOffer (s, escala log)")
    ax.set_title("Latência do aceite no T1 (traço = mediana)", loc="left", fontsize=11, color=TEXTO)
    fig.savefig(arquivo)
    plt.close(fig)


def custo_ciclo(custo: dict[str, float], origem: dict[str, str], nomes: dict, arquivo: Path) -> None:
    redes = [r for r in custo if custo[r] is not None]
    if not redes:
        return
    redes.sort(key=lambda r: custo[r])
    fig, ax = plt.subplots(figsize=(7.5, 0.5 * len(redes) + 1.2))
    vals = [max(custo[r], 1e-6) for r in redes]
    ax.barh(range(len(redes)), vals, color=[CINZA_CLARO if origem.get(r) != "medido" else CINZA for r in redes])
    for i, r in enumerate(redes):
        rot = "gas grátis" if custo[r] == 0 else f"US$ {custo[r]:.4f}"
        ax.text(vals[i] * 1.15, i, f"{rot}  ({origem.get(r, '')})", va="center", fontsize=9, color=TEXTO)
    ax.set_xscale("log")
    ax.set_yticks(range(len(redes)), [nomes.get(r, r) for r in redes])
    ax.set_xlabel("Custo médio do ciclo approve + createOffer + acceptOffer (USD, escala log)")
    ax.set_title("Custo por ciclo completo, a preços da mainnet", loc="left", fontsize=11, color=TEXTO)
    fig.savefig(arquivo)
    plt.close(fig)


def sucesso_por_lote(taxas: dict[str, dict[int, float]], nomes: dict, arquivo: Path) -> None:
    redes = [r for r in taxas if taxas[r]]
    if not redes:
        return
    lotes = sorted({l for r in redes for l in taxas[r]})
    fig, ax = plt.subplots(figsize=(7.5, 3.4))
    largura = 0.8 / len(redes)
    for k, r in enumerate(redes):
        xs = [i + k * largura for i in range(len(lotes))]
        ys = [taxas[r].get(l) or 0 for l in lotes]
        ax.bar(xs, ys, width=largura * 0.9, color=TONS_CRITERIOS[k % len(TONS_CRITERIOS)], label=nomes.get(r, r))
    ax.set_xticks([i + 0.4 - largura / 2 for i in range(len(lotes))], [f"lote de {l}" for l in lotes])
    ax.set_ylim(0, 105)
    ax.set_ylabel("Taxa de sucesso (%)")
    ax.legend(frameon=False, fontsize=9, ncols=min(len(redes), 5), loc="lower center", bbox_to_anchor=(0.5, -0.32))
    ax.set_title("C1: taxa de sucesso no T2 por tamanho de lote", loc="left", fontsize=11, color=TEXTO)
    fig.savefig(arquivo)
    plt.close(fig)


def ranking(pontos: dict[str, dict], nomes: dict, pesos: dict, arquivo: Path) -> None:
    redes = sorted(pontos, key=lambda r: -(pontos[r]["minimo"] + pontos[r]["maximo"]) / 2)
    fig, ax = plt.subplots(figsize=(7.5, 0.55 * len(redes) + 1.6))
    for i, r in enumerate(redes):
        esquerda = 0.0
        for k, c in enumerate(CRITERIOS):
            v = pontos[r]["contribuicao_conhecida"][c]
            ax.barh(i, v, left=esquerda, color=TONS_CRITERIOS[k], height=0.6, label=f"{c} {NOMES_CRITERIOS[c]}" if i == 0 else None)
            esquerda += v
        if pontos[r]["maximo"] > pontos[r]["minimo"] + 1e-9:
            ax.barh(i, pontos[r]["maximo"] - pontos[r]["minimo"], left=pontos[r]["minimo"], height=0.6, color="none", edgecolor=CINZA, hatch="///", linewidth=0.8, label="pendente (pode variar)" if not any(pontos[x]["maximo"] > pontos[x]["minimo"] + 1e-9 for x in redes[:i]) else None)
        rot = f"{pontos[r]['minimo']:.1f}" if pontos[r]["completo"] else f"{pontos[r]['minimo']:.1f} a {pontos[r]['maximo']:.1f}"
        ax.text(pontos[r]["maximo"] + 1, i, rot, va="center", fontsize=9, color=TEXTO)
    ax.set_yticks(range(len(redes)), [nomes.get(r, r) for r in redes])
    ax.invert_yaxis()
    ax.set_xlim(0, 110)
    ax.set_xlabel("Pontuação ponderada (0 a 100)")
    ax.legend(frameon=False, fontsize=8, ncols=3, loc="upper center", bbox_to_anchor=(0.5, -0.16))
    ax.set_title("Pontuação por rede e contribuição de cada critério", loc="left", fontsize=11, color=TEXTO)
    fig.savefig(arquivo)
    plt.close(fig)


def sensibilidade(linhas: list[dict], nomes: dict, arquivo: Path) -> None:
    """Grade cenário × rede com a posição de cada rede; o 1º lugar em destaque."""
    redes = linhas[0]["ordem"]
    fig, ax = plt.subplots(figsize=(7.5, 0.3 * len(linhas) + 1.3))
    for j, l in enumerate(linhas):
        for i, r in enumerate(redes):
            pos = l["ordem"].index(r) + 1
            primeiro = pos == 1
            ax.add_patch(plt.Rectangle((i - 0.45, j - 0.4), 0.9, 0.8, color=DESTAQUE if primeiro else "#eef0f3", zorder=1))
            ax.text(i, j, f"{pos}º", ha="center", va="center", fontsize=8.5, color="white" if primeiro else TEXTO, zorder=2)
    ax.set_xlim(-0.5, len(redes) - 0.5)
    ax.set_ylim(len(linhas) - 0.5, -0.5)
    ax.set_xticks(range(len(redes)), [nomes.get(r, r) for r in redes], fontsize=8.5)
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(linhas)), [l["cenario"] for l in linhas], fontsize=8)
    for lado in ["left", "bottom", "top", "right"]:
        ax.spines[lado].set_visible(False)
    ax.tick_params(length=0)
    mudou = sum(l["primeiro_mudou"] for l in linhas)
    ax.set_title(f"Sensibilidade: o 1º lugar muda em {mudou} de {len(linhas)} cenários de pesos", loc="left", fontsize=11, color=TEXTO, pad=28)
    fig.savefig(arquivo)
    plt.close(fig)
