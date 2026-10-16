"""Gráficos do artigo (PNG).

Todo gráfico diz de onde vem cada número: medido em rede local, medido em testnet, projeção sem
teste ou a medir. Medido = barra sólida; projeção = barra clara e hachurada; a medir = contorno
tracejado. O nome de cada rede leva a origem logo abaixo.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

from benchmark import CRITERIOS, LIMITE_RNF02_S, NOMES_CRITERIOS, ROTULO_ORIGEM  # noqa: E402

TEXTO = "#1f2328"
CINZA = "#8a8f98"
CINZA_CLARO = "#d5d8dd"
DESTAQUE = "#2f6fdb"
TONS_CRITERIOS = ["#1f4e9c", "#2f6fdb", "#6b9bea", "#a9c4f2", "#d5e3fa"]

# Estilo de barra por origem: medido sólido; projeção clara e hachurada; a medir só contorno.
ESTILO = {
    "local": {"facecolor": "#4a5568", "edgecolor": "#4a5568", "hatch": None},
    "testnet": {"facecolor": DESTAQUE, "edgecolor": DESTAQUE, "hatch": None},
    "projetado": {"facecolor": "#eef0f3", "edgecolor": CINZA, "hatch": "////"},
    "pendente": {"facecolor": "none", "edgecolor": CINZA, "hatch": None, "linestyle": "--"},
}

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
    "hatch.color": CINZA,
    "hatch.linewidth": 0.6,
})


CURTO = {"local": "rede local", "testnet": "testnet", "projetado": "projeção", "pendente": "a medir"}


def _rotulo(nome: str, origem: str, curto: bool = False) -> str:
    return f"{nome}\n({(CURTO if curto else ROTULO_ORIGEM)[origem]})"


def _legenda_origem(ax, origens_usadas, **kw):
    itens = [Patch(**{k: v for k, v in ESTILO[o].items() if k != "linestyle"}, linestyle=ESTILO[o].get("linestyle", "-"), label=ROTULO_ORIGEM[o])
             for o in ["local", "testnet", "projetado", "pendente"] if o in origens_usadas]
    ax.legend(handles=itens, frameon=False, fontsize=8.5, **kw)


def _rodape(fig, texto, y=-0.02):
    fig.text(0.01, y, texto, fontsize=8, color=CINZA, ha="left", va="top", wrap=True)


def _br(v, casas):
    """Número no formato brasileiro (vírgula decimal)."""
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def latencia_t1(lat: dict[str, np.ndarray], nomes: dict, origem: dict[str, str], arquivo: Path) -> None:
    """Só redes medidas: cada ponto é um aceite real."""
    redes = [r for r in lat if len(lat[r])]
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    rng = np.random.default_rng(7)
    for i, r in enumerate(redes):
        v = lat[r]
        cor = ESTILO[origem[r]]["facecolor"]
        ax.scatter(rng.uniform(-0.15, 0.15, len(v)) + i, v, s=14, color=cor, alpha=0.75, linewidths=0)
        ax.hlines(np.median(v), i - 0.28, i + 0.28, color=TEXTO, linewidth=1.6)
        ax.text(i + 0.32, np.median(v), f"{_br(np.median(v), 2)} s", va="center", fontsize=9, color=TEXTO)
    ax.axhline(LIMITE_RNF02_S, color=CINZA, linestyle="--", linewidth=1)
    ax.text(max(len(redes), 1) - 0.45, LIMITE_RNF02_S * 0.86, "limite do RNF02: 30 s", ha="right", va="top", fontsize=9, color=CINZA)
    ax.set_yscale("log")
    marcas = [0.1, 0.2, 0.5, 1, 2, 5, 10, 30]
    todos = np.concatenate([lat[r] for r in redes]) if redes else np.array([1.0])
    ax.set_ylim(min(0.8, todos.min() * 0.7), 45)
    ax.set_yticks([m for m in marcas if m >= min(0.8, todos.min() * 0.7)], [f"{_br(m, 1 if m < 1 else 0)} s" for m in marcas if m >= min(0.8, todos.min() * 0.7)])
    ax.minorticks_off()
    ax.set_xlim(-0.6, max(len(redes), 1) - 0.4)
    ax.set_xticks(range(len(redes)), [_rotulo(nomes[r], origem[r]) for r in redes])
    ax.set_ylabel("Latência do acceptOffer (escala log)")
    ax.set_title("Latência do aceite no T1, só redes medidas (traço = mediana)", loc="left", fontsize=11, color=TEXTO)
    faltam = [nomes[r] for r in lat if not len(lat[r])]
    if faltam:
        _rodape(fig, "Ainda sem medição (entram aqui depois da coleta): " + ", ".join(faltam) + ".")
    fig.savefig(arquivo)
    plt.close(fig)


def custo_ciclo(custo: dict[str, float], origem_custo: dict[str, str], ambiente: dict[str, str], nomes: dict, arquivo: Path) -> None:
    """Barra sólida = custo com gas medido; hachurada = projetado com gas de outra rede."""
    redes = [r for r in custo if custo[r] is not None]
    redes.sort(key=lambda r: custo[r])
    fig, ax = plt.subplots(figsize=(7.5, 0.55 * len(redes) + 1.6))
    usados = set()
    positivos = [custo[r] for r in redes if custo[r] > 0] or [1.0]
    piso = min(positivos) / 20  # início do eixo log; custo zero não tem barra
    for i, r in enumerate(redes):
        o = ambiente[r] if origem_custo.get(r) == "medido" else "projetado"
        usados.add(o)
        if custo[r] > 0:
            ax.barh(i, custo[r], left=piso, **ESTILO[o])
            ax.text(custo[r] * 1.2, i, f"US$ {_br(custo[r], 4)}", va="center", fontsize=9, color=TEXTO)
        else:
            ax.text(piso * 1.3, i, "US$ 0 por transação (gas grátis; o custo dessa rede está na infraestrutura)", va="center", fontsize=9, color=TEXTO)
    ax.set_xscale("log")
    ax.set_xlim(piso, max(positivos) * 8)
    ax.set_ylim(-0.6, len(redes) - 0.4)
    ax.set_yticks(range(len(redes)), [_rotulo(nomes[r], ambiente[r] if origem_custo.get(r) == "medido" else "projetado") for r in redes], fontsize=8.5)
    ax.set_xlabel("Custo médio do ciclo approve + createOffer + acceptOffer (USD, escala log)")
    ax.set_title("Custo por ciclo a preços da mainnet", loc="left", fontsize=11, color=TEXTO)
    _legenda_origem(ax, usados, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncols=3)
    if "projetado" in usados:
        _rodape(fig, "Projeção: gas medido na rede local aplicado ao preço da mainnet de cada rede; vira medição quando a testnet for coletada.", y=-0.17)
    fig.savefig(arquivo)
    plt.close(fig)


def sucesso_por_lote(taxas: dict[str, dict[int, float]], nomes: dict, origem: dict[str, str], arquivo: Path) -> None:
    redes = [r for r in taxas if taxas[r]]
    lotes = sorted({l for r in redes for l in taxas[r]}) or [10, 25, 50]
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    largura = 0.8 / max(len(redes), 1)
    for k, r in enumerate(redes):
        xs = [i + k * largura for i in range(len(lotes))]
        ys = [taxas[r].get(l) or 0 for l in lotes]
        ax.bar(xs, ys, width=largura * 0.9, label=f"{nomes[r]} ({ROTULO_ORIGEM[origem[r]]})", **{k2: v for k2, v in ESTILO[origem[r]].items() if k2 != "linestyle"})
        for x, y in zip(xs, ys):
            ax.text(x, y + 1.5, f"{_br(y, 0)}%", ha="center", fontsize=8.5, color=TEXTO)
    ax.set_xticks([i + 0.4 - largura / 2 for i in range(len(lotes))], [f"lote de {l}" for l in lotes])
    ax.set_ylim(0, 110)
    ax.set_ylabel("Taxa de sucesso (%)")
    ax.legend(frameon=False, fontsize=8.5, loc="lower center", bbox_to_anchor=(0.5, -0.3), ncols=min(max(len(redes), 1), 3))
    ax.set_title("C1: taxa de sucesso no T2 por tamanho de lote, só redes medidas", loc="left", fontsize=11, color=TEXTO)
    faltam = [nomes[r] for r in taxas if not taxas[r]]
    if faltam:
        _rodape(fig, "Ainda sem T2 (entram aqui depois da coleta): " + ", ".join(faltam) + ".", y=-0.1)
    fig.savefig(arquivo)
    plt.close(fig)


def ranking(pontos: dict[str, dict], nomes: dict, origem: dict[str, str], arquivo: Path) -> None:
    """Barra sólida = rede medida; hachurada = projeção; contorno tracejado = faixa ainda a medir."""
    redes = sorted(pontos, key=lambda r: -(pontos[r]["minimo"] + pontos[r]["maximo"]) / 2)
    fig, ax = plt.subplots(figsize=(7.5, 0.62 * len(redes) + 1.8))
    for i, r in enumerate(redes):
        p = pontos[r]
        estilo = ESTILO[origem[r]] if origem[r] != "pendente" else ESTILO["projetado"]
        ax.barh(i, p["minimo"], height=0.6, **{k: v for k, v in estilo.items() if k != "linestyle"})
        if p["maximo"] > p["minimo"] + 1e-9:
            ax.barh(i, p["maximo"] - p["minimo"], left=p["minimo"], height=0.6, facecolor="none", edgecolor=CINZA, linestyle="--", linewidth=1)
        rot = _br(p["minimo"], 1) if p["completo"] else f"{_br(p['minimo'], 1)} a {_br(p['maximo'], 1)}"
        ax.text(p["maximo"] + 1, i, rot, va="center", fontsize=9, color=TEXTO, fontweight="bold" if i == 0 else "normal")
    ax.set_yticks(range(len(redes)), [_rotulo(nomes[r], origem[r]) for r in redes], fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlim(0, 110)
    ax.set_xlabel("Pontuação ponderada (0 a 100)")
    ax.set_title("Pontuação por rede e origem dos dados", loc="left", fontsize=11, color=TEXTO)
    _legenda_origem(ax, set(origem.values()), loc="upper center", bbox_to_anchor=(0.5, -0.14), ncols=4)
    _rodape(fig, "Projeção: valores da documentação oficial e hipótese de 100% de sucesso, no lugar da coleta. "
                 "Faixa tracejada: critérios ainda sem valor, de 0 a 1.", y=-0.06)
    fig.savefig(arquivo)
    plt.close(fig)


def sensibilidade(linhas: list[dict], nomes: dict, origem: dict[str, str], arquivo: Path) -> None:
    """Grade cenário × rede com a posição de cada rede; o 1º lugar em destaque."""
    redes = linhas[0]["ordem"]
    fig, ax = plt.subplots(figsize=(7.5, 0.3 * len(linhas) + 1.6))
    for j, l in enumerate(linhas):
        for i, r in enumerate(redes):
            pos = l["ordem"].index(r) + 1
            primeiro = pos == 1
            ax.add_patch(plt.Rectangle((i - 0.45, j - 0.4), 0.9, 0.8, color=DESTAQUE if primeiro else "#eef0f3", zorder=1))
            ax.text(i, j, f"{pos}º", ha="center", va="center", fontsize=8.5, color="white" if primeiro else TEXTO, zorder=2)
    ax.set_xlim(-0.5, len(redes) - 0.5)
    ax.set_ylim(len(linhas) - 0.5, -0.5)
    ax.set_xticks(range(len(redes)), [_rotulo(nomes[r], origem[r], curto=True) for r in redes], fontsize=8)
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(linhas)), [l["cenario"] for l in linhas], fontsize=8)
    for lado in ["left", "bottom", "top", "right"]:
        ax.spines[lado].set_visible(False)
    ax.tick_params(length=0)
    mudou = sum(l["primeiro_mudou"] for l in linhas)
    ax.set_title(f"Sensibilidade: o 1º lugar muda em {mudou} de {len(linhas)} cenários de pesos", loc="left", fontsize=11, color=TEXTO, pad=40)
    fig.savefig(arquivo)
    plt.close(fig)
