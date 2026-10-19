"""Gera pesquisa/3-resultados/resultados.md.

Cada número diz de onde veio (medido em rede local, medido em testnet, projeção sem teste, a medir)
e cada rede tem sempre a mesma ficha de resultados. Nas redes ainda não coletadas a ficha fica com
"—": é ali que os números entram quando `npm run analisar` rodar depois da coleta.
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
    "besu": "Rede local na máquina da equipe: QBFT, 4 validadores em Docker, gas grátis (chain ID 13371)",
    "canton": "Rede local na máquina da equipe: LocalNet do cn-quickstart (Docker)",
}
TIPO = {"testnet": "testnet pública", "local": "rede local"}
COMANDOS = {"canton": "npm run coletar:canton"}
MARCA = {"local": "`LOCAL`", "testnet": "`TESTNET`", "projetado": "`PROJEÇÃO`", "pendente": "`A MEDIR`"}


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


def _origem_celula(o: str | None) -> str:
    return {"declarado": "projeção", "projetado": "projeção", "hipótese": "hipótese"}.get(o or "", "")


def _ficha(r, nome, d, meta, matriz, origens, origem, projecao, dados_rel) -> list[str]:
    tipo = TIPO[bm.AMBIENTE.get(r, "local")]
    L = [f"### {nome} · {tipo}", "", f"**Ambiente:** {AMBIENTES.get(r, '')}.", "",
         f"**Origem dos números:** {MARCA[origem]} {bm.ROTULO_ORIGEM[origem]}.", ""]
    medido = origem in ("local", "testnet")
    if medido:
        janelas = meta.get("janelas", {})
        jan = "; ".join(f"{t} de {v['inicio_utc'][:16].replace('T', ' ')} a {v['fim_utc'][11:16]} UTC" for t, v in janelas.items())
        L += [f"**Coleta:** {jan or 'janela não registrada'}. RPC: {meta.get('tipo_rpc', '—')}. Cliente: `{meta.get('versao_cliente') or '—'}`. "
              f"Dados brutos: `{dados_rel}/{meta.get('_arquivo', '').replace('metadados_', 'medicoes_').replace('.json', '.csv')}`.", ""]
        if meta.get("pausas_observador"):
            L += [f"**Atenção:** {len(meta['pausas_observador'])} pausa(s) do observador; as linhas afetadas ficam fora das estatísticas de latência.", ""]
    else:
        cmd = COMANDOS.get(r, f"npm run implantar -- --rede {r} && npm run coletar -- --rede {r}")
        L += [f"**Coleta:** pendente. Para preencher esta ficha, dentro de `benchmark/`: `{cmd}` e depois `npm run analisar`.", ""]

    s = d["latencia_t1"]
    L += ["**T1, latência do `acceptOffer` (C3):**", "", "| n | Média | Mediana | p95 | Máximo | Até 30 s |", "|---|---|---|---|---|---|"]
    if s.get("n"):
        L.append(f"| {s['n']} | {_n(s['media'])} s | {_n(s['mediana'])} s | {_n(s['p95'])} s | {_n(s['maximo'])} s | {_n(s['prop_ate_30s'] * 100, 0, '%')} |")
    else:
        L.append("| — | — | — | — | — | — |")
    L.append("")

    c = d.get("custo") or {}
    coluna = "gas limit" if (c.get("coluna_gas") == "gas_limit" or r == "monad") else "gas usado"
    if r == "canton":
        L += ["**T1, custo por função (C4-M1):** a Canton não usa gas; o custo segue o modelo de tráfego pago pelo validador, a definir na INTER-6.", "",
              "| Função | Custo médio (USD) |", "|---|---|", "| `approve` | — |", "| `createOffer` | — |", "| `acceptOffer` | — |", "| `cancelOffer` | — |",
              "| **Ciclo completo** | **—** |", ""]
    else:
        L += ["**T1, gas e custo por função (C4-M1):**", "", f"| Função | Gas médio ({coluna}) | Custo médio (USD) |", "|---|---|---|"]
        proprio = c.get("gas_por_funcao") and not c.get("projetado_com_gas_de")
        for f in ["approve", "createOffer", "acceptOffer", "cancelOffer"]:
            if proprio and f in c["gas_por_funcao"]:
                L.append(f"| `{f}` | {_n(c['gas_por_funcao'][f], 0)} | {_n((c.get('usd_por_funcao') or {}).get(f), 5)} |")
            else:
                L.append(f"| `{f}` | — | — |")
        L.append(f"| **Ciclo completo** | **{_n(c.get('ciclo_gas_medio'), 0) if proprio else '—'}** | **{_n(c.get('ciclo_usd_medio'), 5) if proprio else '—'}** |")
        L.append("")

    t = d["taxa_sucesso_t2"]
    L += ["**T2, carga simultânea (C1):**", "", "| Lote | Taxa de sucesso | Latência mediana sob carga | p95 sob carga |", "|---|---|---|---|"]
    if t.get("n"):
        for lote, taxa in sorted(d["taxa_por_lote"].items()):
            lat = d["latencia_t2_por_lote"].get(lote, {})
            L.append(f"| {lote} | {_n(taxa, 1, '%')} | {_n(lat.get('mediana'))} s | {_n(lat.get('p95'))} s |")
        f = t["falhas"]
        L += [f"| **Total** | **{_n(t['taxa'], 1, '%')}** ({t['confirmadas']} de {t['denominador']}) | | |", "",
              f"Falhas: A {f['A']} · B {f['B']} · C {f['C']} · D {f['D']} · X {f['X']} (só D conta contra a rede).", ""]
    else:
        L += ["| 10 | — | — | — |", "| 25 | — | — | — |", "| 50 | — | — | — |", "| **Total** | — | | |", ""]

    if not medido:
        fb = (projecao or {}).get("fallback_declarado", {})
        prov = []
        if r in fb.get("C3_latencia_s", {}):
            prov.append(f"| C3 latência | {_n(fb['C3_latencia_s'][r]['valor'])} s | {fb['C3_latencia_s'][r]['fonte']} |")
        if c.get("projetado_com_gas_de"):
            prov.append(f"| C4-M1 custo do ciclo | US$ {_n(matriz.brutos['C4M1'].get(r), 5)} | gas medido em {c['projetado_com_gas_de']} (rede local) × preço da mainnet desta rede |")
        if r in fb.get("C1_taxa_sucesso", {}):
            prov.append(f"| C1 taxa de sucesso | {_n(fb['C1_taxa_sucesso'][r]['valor'], 1)}% | {fb['C1_taxa_sucesso'][r]['fonte']} |")
        if prov:
            L += ["**Valores provisórios que a matriz usa até a coleta (nenhum foi medido nesta rede):**", "",
                  "| Critério | Valor | Fonte |", "|---|---|---|", *prov, ""]
        faltam = [x for x, k in [("C3 latência", "C3"), ("C4-M1 custo", "C4M1")] if matriz.brutos[k].get(r) is None]
        if faltam:
            L += [f"Sem valor provisório para {' e '.join(faltam)}: a pontuação desta rede aparece como faixa até a coleta.", ""]
    return L


def gerar(*, redes, nomes, detalhes, matriz, pontos, sens, precos, origens, origem_rede, pesos, projecao, pasta_dados, pasta_imagens, destino: Path, alternativas=None) -> str:
    meta = carregar_metadados(pasta_dados)
    img = os.path.relpath(pasta_imagens, destino.parent)
    dados_rel = os.path.relpath(pasta_dados, destino.parent)
    agora = datetime.now(timezone.utc)
    por_origem = {o: [nomes[r] for r in redes if origem_rede[r] == o] for o in bm.ROTULO_ORIGEM}

    L = [
        "# Resultados do benchmark",
        "",
        f"> Arquivo gerado por `benchmark/analise/analisar.py` em {agora:%d/%m/%Y %H:%M} UTC. Não edite à mão: depois de cada coleta, rode `npm run analisar` dentro de `benchmark/`.",
        "",
        "## De onde vem cada número",
        "",
        "| Etiqueta | Origem | O que significa | Redes hoje |",
        "|---|---|---|---|",
        f"| {MARCA['local']} | Medido em rede local | A equipe rodou o contrato numa rede montada na própria máquina (Docker). Mede o protocolo de verdade, mas sem tráfego de outros usuários nem latência de internet | {', '.join(por_origem['local']) or '—'} |",
        f"| {MARCA['testnet']} | Medido em testnet | A equipe rodou o contrato na testnet pública da rede, com outros usuários e RPC público | {', '.join(por_origem['testnet']) or '—'} |",
        f"| {MARCA['projetado']} | Projeção, sem teste | Nenhum teste nosso: latência da documentação oficial, custo calculado com o gas medido na rede local e 100% de sucesso como hipótese | {', '.join(por_origem['projetado']) or '—'} |",
        f"| {MARCA['pendente']} | A medir | Sem teste e sem valor provisório para algum critério: a pontuação aparece como faixa | {', '.join(por_origem['pendente']) or '—'} |",
        "",
        "Quando uma testnet for coletada, a linha dela passa de projeção para medido em testnet e todos os números abaixo são recalculados.",
        "",
        "## Situação da coleta",
        "",
        "| Rede | Tipo de ambiente | Origem dos números | T1 | T2 | Coletado em |",
        "|---|---|---|---|---|---|",
    ]
    for r in redes:
        d = detalhes[r]
        m = meta.get(r, {})
        quando = next(iter(m.get("janelas", {}).values()), {}).get("inicio_utc", "")[:10]
        t1 = f"{d['latencia_t1']['n']} aceites" if d["latencia_t1"].get("n") else "pendente"
        t2 = f"{d['taxa_sucesso_t2']['n']} aceites" if d["taxa_sucesso_t2"].get("n") else "pendente"
        o = origem_rede[r]
        L.append(f"| {nomes[r]} | {TIPO[bm.AMBIENTE.get(r, 'local')]} | {MARCA[o]} {bm.ROTULO_ORIGEM[o]} | {t1} | {t2} | {quando or '—'} |")

    ordem = sorted(redes, key=lambda x: -(pontos[x]["minimo"] + pontos[x]["maximo"]) / 2)
    L += ["", "## Ranking atual (preliminar enquanto houver projeção)", "", f"![Pontuação por rede]({img}/ranking.png)", "",
          "| Posição | Rede | Origem | C1 | C2 | C3 | C4 | C5 | Pontuação |", "|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(ordem, 1):
        cel = []
        for c in bm.CRITERIOS:
            n = matriz.nota(c, r)
            o = _origem_celula(origens.get({"C1": "C1", "C3": "C3", "C4": "C4M1"}.get(c, ""), {}).get(r))
            cel.append("a medir" if n.valor is None else _n(n.valor) + (f" ({o})" if o else ""))
        p = pontos[r]
        tot = _n(p["minimo"], 1) if p["completo"] else f"{_n(p['minimo'], 1)} a {_n(p['maximo'], 1)}"
        o = origem_rede[r]
        L.append(f"| {i} | {nomes[r]} | {MARCA[o]} {bm.ROTULO_ORIGEM[o]} | " + " | ".join(cel) + f" | **{tot}** |")
    L += [
        "",
        "Notas de 0 a 1 (min-max entre as cinco redes); pesos " + ", ".join(f"{c} {_n(pesos[c] * 100)}%" for c in bm.CRITERIOS) + ". "
        "C2 e C5 vêm de documentação e do código em todas as redes. Pontuação em faixa: critérios ainda sem valor podem ir de 0 a 1.",
    ]
    if matriz.sem_infra:
        L.append("C4 usa só o custo por transação (C4-M1). O custo de infraestrutura (C4-M2) foi levantado em `pesquisa/4-custo-infraestrutura/`, mas não entra na pontuação: a Canton é uma rede privada, de acesso restrito a instituições, e supor um valor para ela seria antiético.")

    mudou = [l["cenario"] for l in sens if l["primeiro_mudou"]]
    L += ["", "## Sensibilidade aos pesos", "", f"![Sensibilidade]({img}/sensibilidade.png)", "",
          f"O primeiro lugar muda em {len(mudou)} de {len(sens)} cenários" + (f": {', '.join(mudou)}." if mudou else ".") +
          " Enquanto houver projeção, a sensibilidade também é preliminar.", ""]

    if alternativas:
        meio = lambda p: (p["minimo"] + p["maximo"]) / 2
        fmt_p = lambda p: _n(p["minimo"], 1) if p["completo"] else f"{_n(p['minimo'], 1)} a {_n(p['maximo'], 1)}"
        base = sorted(redes, key=lambda r: -meio(pontos[r]))
        L += ["## Escolhas de método que podem mudar a conclusão", "",
              "O ranking refeito com cada alternativa (pesos do cenário base):", "",
              "| Escolha | 1º lugar | Pontuação por rede |", "|---|---|---|",
              f"| **Adotada** (roteiro) | {nomes[base[0]]} | " + "; ".join(f"{nomes[r]} {fmt_p(pontos[r])}" for r in base) + " |"]
        for alt in alternativas:
            ordem = sorted(redes, key=lambda r: -meio(alt["pontos"][r]))
            L.append(f"| {alt['descricao']} | {nomes[ordem[0]]} | " + "; ".join(f"{nomes[r]} {fmt_p(alt['pontos'][r])}" for r in ordem) + " |")
        L.append("")
    L += ["## Custo por ciclo a preços da mainnet (C4-M1)", "", f"![Custo por ciclo]({img}/custo_ciclo.png)", "",
          "| Rede | Origem do custo | Gas cobrado por ciclo | Preço de referência | Cotação | Custo do ciclo |", "|---|---|---|---|---|---|"]
    for r in redes:
        c = detalhes[r].get("custo") or {}
        p = precos.get(r) or {}
        oc = origens["C4M1"].get(r)
        rot = (f"{MARCA[bm.AMBIENTE.get(r, 'local')]} {bm.ROTULO_ORIGEM[bm.AMBIENTE.get(r, 'local')]}" if oc == "medido"
               else f"{MARCA['projetado']} projeção (gas medido em {c.get('projetado_com_gas_de', 'outra rede')})" if oc == "projetado"
               else f"{MARCA['pendente']} a medir")
        gas_ciclo = "sem gas" if r == "canton" else _n(c.get("ciclo_gas_medio"), 0)
        L.append(f"| {nomes[r]} | {rot} | {gas_ciclo} | {_n(p['gas_preco_wei'] / 1e9, 3) + ' gwei' if p else '—'} | "
                 f"{'US$ ' + _n(p['cotacao_usd'], 2 if p['cotacao_usd'] >= 1 else 4) if p.get('cotacao_usd') else '—'} | "
                 f"{'US$ ' + _n(matriz.brutos['C4M1'].get(r), 5) if matriz.brutos['C4M1'].get(r) is not None else '—'} |")
    janela = next(iter(precos.values()), {}).get("janela") if precos else None
    if janela:
        L += ["", f"Preços: mediana de {next(iter(precos.values()))['amostras']} amostra(s) entre {janela[0][:16]} e {janela[1][:16]} UTC (eth_feeHistory e CoinGecko)."]

    # Sepolia pós-Glamsterdam: gas da testnet × gas pelas regras atuais da mainnet (medido no Besu).
    cs, cb = detalhes.get("sepolia", {}).get("custo") or {}, detalhes.get("besu", {}).get("custo") or {}
    ps = precos.get("sepolia") or {}
    if cs.get("gas_por_funcao") and not cs.get("projetado_com_gas_de") and cb.get("gas_por_funcao") and ps.get("cotacao_usd"):
        usd = lambda g: g * ps["gas_preco_wei"] / 1e18 * ps["cotacao_usd"]
        L += ["", "### Ethereum: gas da Sepolia × regras atuais da mainnet", "",
              "A Sepolia ativou o Glamsterdam em 06/10/2026, que encarece a criação de estado (contas, posições de "
              "armazenamento e código). A mainnet ainda usa as regras anteriores. O roteiro (seção 3.3) supõe o mesmo gas "
              "na testnet e na mainnet; para a Ethereum essa premissa deixou de valer durante este estudo.", "",
              "| Função | Gas na Sepolia (Glamsterdam) | Gas pelas regras atuais da mainnet (Besu) | Razão |", "|---|---|---|---|"]
        for f in ["approve", "createOffer", "acceptOffer", "cancelOffer"]:
            gs, gb = cs["gas_por_funcao"].get(f), cb["gas_por_funcao"].get(f)
            if gs and gb:
                L.append(f"| `{f}` | {_n(gs, 0)} | {_n(gb, 0)} | {_n(gs / gb, 2)}× |")
        gs, gb = cs.get("ciclo_gas_medio"), cb.get("ciclo_gas_medio")
        if gs and gb:
            L += [f"| **Ciclo completo** | **{_n(gs, 0)}** | **{_n(gb, 0)}** | **{_n(gs / gb, 2)}×** |", "",
                  f"Custo do ciclo a preços da mainnet: US$ {_n(usd(gs), 4)} com o gas da Sepolia (valor usado na matriz, como manda o roteiro) "
                  f"e US$ {_n(usd(gb), 4)} com as regras atuais da mainnet. A Ethereum é a rede mais cara nos dois casos, então "
                  "a nota dela em C4-M1 é 0 nos dois e a ordem do ranking não muda; mudam o valor absoluto citado no artigo e, um pouco, "
                  "as notas de custo das outras redes (ver \"Escolhas de método\")."]
    L += ["", "## Latência e taxa de sucesso medidas", "",
          f"![Latência no T1]({img}/latencia_t1.png)", "", f"![Taxa de sucesso no T2]({img}/sucesso_t2.png)", "",
          "Os dois gráficos só mostram redes medidas; as testnets e a Canton entram neles depois da coleta.", ""]

    locais = [r for r in redes if bm.AMBIENTE.get(r) == "local"]
    testnets = [r for r in redes if bm.AMBIENTE.get(r) == "testnet"]
    L += ["## Fichas por rede", "", "### Redes locais", "",
          "Montadas na máquina da equipe; medem o protocolo sem tráfego de terceiros nem latência de internet.", ""]
    for r in locais:
        L += ["#" + line if line.startswith("### ") else line for line in _ficha(r, nomes[r], detalhes[r], meta.get(r, {}), matriz, origens, origem_rede[r], projecao, dados_rel)]
    L += ["### Testnets públicas", "", "Fichas prontas para os dados da coleta; enquanto mostrarem \"—\", a matriz usa os valores provisórios de cada ficha.", ""]
    for r in testnets:
        L += ["#" + line if line.startswith("### ") else line for line in _ficha(r, nomes[r], detalhes[r], meta.get(r, {}), matriz, origens, origem_rede[r], projecao, dados_rel)]
    return "\n".join(L)
