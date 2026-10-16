# dados

Dados brutos das coletas, gravados pelos scripts de `../benchmark/`. Não edite à mão: a análise
lê tudo o que está aqui e um valor alterado muda o ranking sem deixar rastro.

| Arquivo | Conteúdo |
|---|---|
| `medicoes_<rede>_<data>.csv` | Uma linha por transação do T1 e do T2, nas colunas da seção 6.1 do roteiro, mais `gas_limit` e `nonce` |
| `preparo_<rede>_<data>.csv` | Transações da preparação do T2 (approve e criação das ofertas), fora da medição |
| `metadados_<rede>_<data>.json` | Metadados da seção 6.2: RPC, máquina, contratos, contas, versão do cliente e janela da coleta |
| `precos_referencia_<data>.json` | Amostras do preço do gas na mainnet e da cotação de cada token (C4-M1) |
| `coleta_<rede>*.log` | Saída do terminal de cada coleta |

`preparo_besu_2026-10-14.tentativa1-suspensao.csv` é a primeira tentativa do T2 no Besu, interrompida
porque a máquina suspendeu; o T2 foi refeito. O arquivo fica como registro e a análise não o lê.
