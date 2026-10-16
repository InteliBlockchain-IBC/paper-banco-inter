"""Gera pesquisa/3-resultados/resultados.md: situação da coleta, ranking, sensibilidade e uma seção por rede.

Redes ainda não medidas aparecem com a seção pronta ("aguardando coleta"), o comando para medir
e os valores provisórios que a matriz está usando no lugar dos medidos.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import benchmark as bm

AMBIENTES = {
    "sepolia": "Testnet pública Sepolia (chain ID 11155111)",
    "fuji": "Testnet pública Fuji, C-Chain (chain ID 43113)",
    "monad": "Testnet pública Monad (chain ID 10143)",
    "besu": "Rede local QBFT, 4 validadores, gas grátis (chain ID 13371)",
    "canton": "LocalNet do cn-quickstart",
}
COMANDOS = {
    "canton": "npm run coletar:canton",
}


def _n(v, casas=2, sufixo=""):
    if v is None:
        return "—"
    s = f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s}{sufixo}"


def carregar_metadados(pasta: Path) -> dict[str, dict]:
    """Metadados mais recentes de cada rede (seção 6.2 do roteiro)."""
    out = {}
    for arq in sorted(Path(pasta).glob("metadados_*.json")):
        m = json.loads(arq.read_text())
        out[m.get("rede", arq.stem.split("_")[1])] = {**m, "_arquivo": arq.name}
    return out


def _origem(o: str) -> str:
    return {"medido": "medido", "declarado": "declarado", "projetado": "projetado", "hipótese": "hipótese", "misto": "misto"}.get(o, "a medir")


def _secao_rede(r, nome, d, meta, matriz, origens, projecao, pasta_dados_rel) -> list[str]:
    L = [f"### {nome}", ""]
    medido = d["latencia_t1"].get("n") or d["taxa_sucesso_t2"].get("n")
    L.append(f"**Ambiente:** {AMBIENTES.get(r, '')}.")
    if not medido:
        cmd = COMANDOS.get(r, f"npm run implantar -- --rede {r} && npm run coletar -- --rede {r}")
        L += ["", f"**Situação:** aguardando coleta. Comando, dentro de `benchmark/`: `{cmd}`.", ""]
        fb = (projecao or {}).get("fallback_declarado", {})
        prov = []
        for chave, crit, unidade in [("C3_latencia_s", "C3", " s"), ("C1_taxa_sucesso", "C1", "%")]:
            if r in fb.get(chave, {}):
                prov.append(f"| {crit} | {_n(fb[chave][r]['valor'], 1 if crit == 'C1' else 2, unidade)} | {fb[chave][r]['fonte']} |")
        c = d.get("custo") or {}
        if c.get("projetado_com_gas_de"):
            prov.append(f"| C4-M1 | US$ {_n(matriz.brutos['C4M1'].get(r), 5)} por ciclo | gas medido em {c['projetado_com_gas_de']} × preço da mainnet desta rede |")
        if prov:
            L += ["Valores provisórios usados na matriz até a coleta:", "", "| Critério | Valor | Fonte |", "|---|---|---|", *prov, ""]
        faltam = [c for c, k in [("C3 latência", "C3"), ("C4-M1 custo", "C4M1")] if matriz.brutos[k].get(r) is None]
        if faltam:
            L += [f"Sem valor provisório para {' e '.join(faltam)}: a pontuação desta rede aparece como faixa até a coleta.", ""]
        return L

    janelas = meta.get("janelas", {})
    jan = "; ".join(f"{t} de {v['inicio_utc'][:16].replace('T', ' ')} a {v['fim_utc'][11:16]} UTC" for t, v in janelas.items())
    L += [
        "",
        f"**Coleta:** {jan or 'janela não registrada'}. RPC: {meta.get('tipo_rpc', '—')}. Cliente: `{meta.get('versao_cliente') or '—'}`.",
        "",
    ]
    if meta.get("pausas_observador"):
        L += [f"**Atenção:** o observador registrou {len(meta['pausas_observador'])} pausa(s) (máquina suspensa ou processo parado); linhas afetadas usam o horário do bloco e ficam fora das estatísticas de latência.", ""]

    s = d["latencia_t1"]
    if s.get("n"):
        L += [
            "**T1, latência do `acceptOffer` (C3):**",
            "",
            "| n | Média | Mediana | p95 | Máximo | Até 30 s |",
            "|---|---|---|---|---|---|",
            f"| {s['n']} | {_n(s['media'])} s | {_n(s['mediana'])} s | {_n(s['p95'])} s | {_n(s['maximo'])} s | {_n(s['prop_ate_30s'] * 100, 0, '%')} |",
            "",
        ]
    c = d.get("custo") or {}
    if c.get("gas_por_funcao") and not c.get("projetado_com_gas_de"):
        L += ["**T1, gas e custo por função (C4-M1):**", "", f"| Função | Gas médio ({c.get('coluna_gas', 'gas_used')}) | Custo médio (USD) |", "|---|---|---|"]
        for f in ["approve", "createOffer", "acceptOffer", "cancelOffer"]:
            if f in c["gas_por_funcao"]:
                L.append(f"| `{f}` | {_n(c['gas_por_funcao'][f], 0)} | {_n((c.get('usd_por_funcao') or {}).get(f), 5)} |")
        L += [f"| **Ciclo completo** | **{_n(c.get('ciclo_gas_medio'), 0)}** | **{_n(c.get('ciclo_usd_medio'), 5)}** |", ""]

    t = d["taxa_sucesso_t2"]
    if t.get("n"):
        f = t["falhas"]
        L += [
            "**T2, carga simultânea (C1):**",
            "",
            "| Lote | Taxa de sucesso | Latência mediana sob carga | p95 sob carga |",
            "|---|---|---|---|",
        ]
        for lote, taxa in sorted(d["taxa_por_lote"].items()):
            lat = d["latencia_t2_por_lote"].get(lote, {})
            L.append(f"| {lote} | {_n(taxa, 1, '%')} | {_n(lat.get('mediana'))} s | {_n(lat.get('p95'))} s |")
        L += [
            f"| **Total** | **{_n(t['taxa'], 1, '%')}** ({t['confirmadas']} de {t['denominador']}) | | |",
            "",
            f"Falhas: A {f['A']} · B {f['B']} · C {f['C']} · D {f['D']} · X {f['X']} (só D conta contra a rede).",
            "",
        ]
    L += [f"Dados brutos: `{pasta_dados_rel}/{meta.get('_arquivo', '').replace('metadados_', 'medicoes_').replace('.json', '.csv')}`.", ""]
    return L


def gerar(*, redes, nomes, detalhes, matriz, pontos, sens, precos, origens, pesos, projecao, pasta_dados, pasta_imagens, destino: Path) -> str:
    meta = carregar_metadados(pasta_dados)
    img = os.path.relpath(pasta_imagens, destino.parent)
    dados_rel = os.path.relpath(pasta_dados, destino.parent)
    agora = datetime.now(timezone.utc)
    medidas = [r for r in redes if detalhes[r]["latencia_t1"].get("n") or detalhes[r]["taxa_sucesso_t2"].get("n")]

    L = [
        "# Resultados do benchmark",
        "",
        f"> Arquivo gerado por `benchmark/analise/analisar.py` em {agora:%d/%m/%Y %H:%M} UTC. Não edite à mão: depois de cada coleta, rode `npm run analisar` dentro de `benchmark/`.",
        "",
        f"Redes medidas até agora: {', '.join(nomes[r] for r in medidas) or 'nenhuma'}. "
        "Onde ainda não há medição, a matriz usa valores declarados ou projetados, marcados na tabela de notas.",
        "",
        "## Situação da coleta",
        "",
        "| Rede | Ambiente | T1 | T2 | Coletado em |",
        "|---|---|---|---|---|",
    ]
    for r in redes:
        d = detalhes[r]
        m = meta.get(r, {})
        quando = next(iter(m.get("janelas", {}).values()), {}).get("inicio_utc", "")[:10]
        t1 = f"{d['latencia_t1']['n']} aceites" if d["latencia_t1"].get("n") else "pendente"
        t2 = f"{d['taxa_sucesso_t2']['n']} aceites" if d["taxa_sucesso_t2"].get("n") else "pendente"
        L.append(f"| {nomes[r]} | {AMBIENTES.get(r, '')} | {t1} | {t2} | {quando or '—'} |")

    ordem = sorted(redes, key=lambda x: -(pontos[x]["minimo"] + pontos[x]["maximo"]) / 2)
    L += ["", "## Ranking atual", "", f"![Pontuação por rede]({img}/ranking.png)", "",
          "| Posição | Rede | C1 | C2 | C3 | C4 | C5 | Pontuação |", "|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(ordem, 1):
        cel = []
        for c in bm.CRITERIOS:
            n = matriz.nota(c, r)
            o = origens.get({"C1": "C1", "C3": "C3", "C4": "C4M1"}.get(c, ""), {}).get(r)
            cel.append("a medir" if n.valor is None else f"{_n(n.valor)}" + (f" ({_origem(o)})" if o and o != "medido" else ""))
        p = pontos[r]
        tot = _n(p["minimo"], 1) if p["completo"] else f"{_n(p['minimo'], 1)} a {_n(p['maximo'], 1)}"
        L.append(f"| {i} | {nomes[r]} | " + " | ".join(cel) + f" | **{tot}** |")
    L += [
        "",
        "Notas de 0 a 1 (min-max entre as cinco redes); pesos " + ", ".join(f"{c} {_n(pesos[c] * 100)}%" for c in bm.CRITERIOS) + ". "
        "Entre parênteses, a origem quando o valor não foi medido. Pontuação em faixa: critérios ainda sem valor podem ir de 0 a 1.",
    ]
    if matriz.sem_infra:
        L.append("C4 usa só o custo por transação (C4-M1): o custo de infraestrutura (C4-M2) ainda não foi levantado.")

    mudou = [l["cenario"] for l in sens if l["primeiro_mudou"]]
    L += ["", "## Sensibilidade aos pesos", "", f"![Sensibilidade]({img}/sensibilidade.png)", "",
          f"O primeiro lugar muda em {len(mudou)} de {len(sens)} cenários" + (f": {', '.join(mudou)}." if mudou else "."), ""]

    L += ["## Custo por ciclo a preços da mainnet (C4-M1)", "",
          "| Rede | Gas cobrado por ciclo | Preço de referência | Cotação | Custo do ciclo | Origem |", "|---|---|---|---|---|---|"]
    for r in redes:
        c = detalhes[r].get("custo") or {}
        p = precos.get(r) or {}
        L.append(f"| {nomes[r]} | {_n(c.get('ciclo_gas_medio'), 0)} | {_n(p['gas_preco_wei'] / 1e9, 3) + ' gwei' if p else '—'} | "
                 f"{'US$ ' + _n(p['cotacao_usd'], 2 if p['cotacao_usd'] >= 1 else 4) if p.get('cotacao_usd') else '—'} | "
                 f"{'US$ ' + _n(matriz.brutos['C4M1'].get(r), 5) if matriz.brutos['C4M1'].get(r) is not None else 'a medir'} | {_origem(origens['C4M1'].get(r, ''))} |")
    janela = next(iter(precos.values()), {}).get("janela") if precos else None
    if janela:
        L += ["", f"Preços: mediana de {next(iter(precos.values()))['amostras']} amostra(s) entre {janela[0][:16]} e {janela[1][:16]} UTC (eth_feeHistory e CoinGecko)."]

    L += ["", "## Resultados por rede", ""]
    for r in redes:
        L += _secao_rede(r, nomes[r], detalhes[r], meta.get(r, {}), matriz, origens, projecao, dados_rel)

    L += ["## Gráficos", "",
          f"- Latência do aceite no T1: `{img}/latencia_t1.png`",
          f"- Custo por ciclo: `{img}/custo_ciclo.png`",
          f"- Taxa de sucesso no T2 por lote: `{img}/sucesso_t2.png`", ""]
    return "\n".join(L)
