"""Consolida os dados medidos (INTER-18), calcula notas, ranking e sensibilidade (INTER-21) e gera gráficos.

Uso (o mesmo que `npm run analisar`):
  python3 analise/analisar.py --projecao config/projecao.json --projetar-custo-com besu
      dados medidos onde existem; nas redes ainda não medidas, valores declarados ou projetados
  python3 analise/analisar.py --relatorio /tmp/so-medido.md
      só o que foi medido (o restante fica como faixa pendente)

Saídas em pesquisa/3-resultados/: resultados.md, resumo.json e graficos/*.png. Dados lidos de dados/.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI))

import benchmark as bm  # noqa: E402
import complexidade  # noqa: E402
import graficos  # noqa: E402
import relatorio  # noqa: E402


def _fmt(v, casas=2, sufixo=""):
    if v is None:
        return "pendente"
    return f"{v:,.{casas}f}{sufixo}".replace(",", "X").replace(".", ",").replace("X", ".")


def coletar_brutos(df, precos, redes_cfg, declarados, projecao, projetar_com, repo_web3):
    redes = declarados["redes"]
    brutos = {k: {} for k in ["C1", "C3", "C4M1", "C4M2", "C2M2"]}
    origens = {k: {} for k in brutos}
    detalhes = {}
    fb = (projecao or {}).get("fallback_declarado", declarados.get("fallback_declarado", {}))

    m_sol = complexidade.analisar(repo_web3 / "src")["total"]["m_total"]
    pasta_daml = RAIZ / "redes-locais" / "canton"
    m_daml = complexidade.analisar(pasta_daml)["total"]["m_total"] if pasta_daml.exists() else None

    for r in redes:
        cfg = redes_cfg.get(r, {})
        d = {}
        tem = not df.empty and (df.rede == r).any()
        dr = df[df.rede == r] if tem else df

        # C3: mediana da latência do acceptOffer no T1
        lat = bm.latencias_aceite_t1(df, r) if tem else []
        d["latencia_t1"] = bm.estatisticas(lat) if len(lat) else {"n": 0}
        d["latencia_t2_por_lote"] = bm.latencia_sob_carga(df, r) if tem else {}
        if len(lat):
            brutos["C3"][r], origens["C3"][r] = d["latencia_t1"]["mediana"], "medido"
        elif r in fb.get("C3_latencia_s", {}):
            brutos["C3"][r], origens["C3"][r] = fb["C3_latencia_s"][r]["valor"], "declarado"

        # C1: taxa agregada do T2
        ts = bm.taxa_sucesso(dr) if tem else {"n": 0}
        d["taxa_sucesso_t2"] = ts
        d["taxa_por_lote"] = bm.taxa_por_lote(df, r) if tem else {}
        if ts.get("n"):
            brutos["C1"][r], origens["C1"][r] = ts["taxa"], "medido"
        elif r in fb.get("C1_taxa_sucesso", {}):
            brutos["C1"][r], origens["C1"][r] = fb["C1_taxa_sucesso"][r]["valor"], "hipótese"

        # C4-M1: média do ciclo completo em USD
        cobranca = cfg.get("cobrancaGas", "conferir")
        c = bm.custos(df, r, cobranca, precos.get(r)) if tem and cobranca != "conferir" else {}
        if c.get("ciclo_usd_medio") is not None:
            brutos["C4M1"][r], origens["C4M1"][r] = c["ciclo_usd_medio"], "medido"
        elif projetar_com and r in precos and cobranca in ("gasUsed", "gasLimit"):
            ref = bm.custos(df, projetar_com, "gasLimit" if cobranca == "gasLimit" else "gasUsed", {"gas_preco_wei": precos[r]["gas_preco_wei"], "cotacao_usd": precos[r]["cotacao_usd"]})
            if ref.get("ciclo_usd_medio") is not None:
                c = {**ref, "projetado_com_gas_de": projetar_com}
                brutos["C4M1"][r], origens["C4M1"][r] = ref["ciclo_usd_medio"], "projetado"
        elif r in fb.get("C4_M1_ciclo_usd", {}):
            brutos["C4M1"][r], origens["C4M1"][r] = fb["C4_M1_ciclo_usd"][r]["valor"], "declarado"
        d["custo"] = c

        # C4-M2 e C2-M2
        infra = declarados["C4_M2_infra_usd_mes"].get(r)
        if isinstance(infra, (int, float)):
            brutos["C4M2"][r], origens["C4M2"][r] = infra, "declarado"
        versao = declarados["versao_codigo"][r]
        m = m_sol if versao == "solidity" else m_daml
        if m is not None:
            brutos["C2M2"][r], origens["C2M2"][r] = m, "medido"
        d["complexidade"] = {"versao": versao, "m_total": m}
        detalhes[r] = d
    return brutos, origens, detalhes


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dados", default=str(RAIZ.parent / "dados"))
    ap.add_argument("--saida", default=str(RAIZ.parent / "pesquisa" / "3-resultados"))
    ap.add_argument("--relatorio", default=str(RAIZ.parent / "pesquisa" / "3-resultados" / "resultados.md"), help="documento de resultados gerado")
    ap.add_argument("--declarados", default=str(RAIZ / "config" / "declarados.json"))
    ap.add_argument("--redes", default=str(RAIZ / "config" / "redes.json"))
    ap.add_argument("--projecao", help="JSON com valores declarados para células não medidas")
    ap.add_argument("--projetar-custo-com", help="rede cujo gas medido projeta o custo das redes sem T1")
    ap.add_argument("--repo-web3", default=str(bm.repo_web3()))
    a = ap.parse_args(argv)

    declarados = json.loads(Path(a.declarados).read_text())
    redes_cfg = json.loads(Path(a.redes).read_text())
    projecao = json.loads(Path(a.projecao).read_text()) if a.projecao else None
    df = bm.carregar_medicoes(Path(a.dados))
    precos = bm.carregar_precos(Path(a.dados))
    redes, nomes, pesos = declarados["redes"], declarados["nomes"], declarados["pesos"]

    brutos, origens, detalhes = coletar_brutos(df, precos, redes_cfg, declarados, projecao, a.projetar_custo_com, Path(a.repo_web3))
    matriz = bm.montar_matriz(redes, brutos, origens, declarados)
    pontos = bm.pontuar(matriz, pesos)
    sens = bm.sensibilidade(matriz, pesos)

    saida = Path(a.saida)
    saida.mkdir(parents=True, exist_ok=True)
    lider = sens[0]["ordem"][0]
    pasta_graficos = saida / "graficos"
    pasta_graficos.mkdir(parents=True, exist_ok=True)
    graficos.latencia_t1({r: bm.latencias_aceite_t1(df, r) for r in redes} if not df.empty else {}, nomes, lider, pasta_graficos / "latencia_t1.png")
    graficos.custo_ciclo(brutos["C4M1"], origens["C4M1"], nomes, pasta_graficos / "custo_ciclo.png")
    graficos.sucesso_por_lote({r: detalhes[r]["taxa_por_lote"] for r in redes}, nomes, pasta_graficos / "sucesso_t2.png")
    graficos.ranking(pontos, nomes, pesos, pasta_graficos / "ranking.png")
    graficos.sensibilidade(sens, nomes, pasta_graficos / "sensibilidade.png")

    resumo = {
        "gerado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pesos": pesos,
        "precos_referencia": precos,
        "brutos": brutos,
        "origens": origens,
        "notas": {c: {r: {"valor": matriz.nota(c, r).valor, "origem": matriz.nota(c, r).origem} for r in redes} for c in bm.CRITERIOS},
        "medidas": {k: {r: {"valor": v.valor, "origem": v.origem} for r, v in cel.items()} for k, cel in matriz.medidas.items()},
        "pontuacao": pontos,
        "sensibilidade": [{k: v for k, v in l.items() if k != "pesos"} for l in sens],
        "detalhes": detalhes,
    }
    (saida / "resumo.json").write_text(json.dumps(resumo, indent=2, ensure_ascii=False, default=float))
    destino = Path(a.relatorio)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(relatorio.gerar(
        redes=redes, nomes=nomes, detalhes=detalhes, matriz=matriz, pontos=pontos, sens=sens, precos=precos,
        origens=origens, pesos=pesos, projecao=projecao, pasta_dados=Path(a.dados), pasta_imagens=pasta_graficos, destino=destino,
    ))
    lider = sens[0]["ordem"]
    print(f"Ranking: " + " > ".join(f"{nomes[r]} {(pontos[r]['minimo'] + pontos[r]['maximo']) / 2:.1f}" for r in lider))
    print(f"Relatório: {destino}\nGráficos: {pasta_graficos}\nresumo.json: {saida}")


if __name__ == "__main__":
    main()
