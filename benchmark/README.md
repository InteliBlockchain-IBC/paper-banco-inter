# benchmark

Código que coleta e analisa os dados medidos do paper. Implementa o roteiro de medição
([`../pesquisa/2-metodo/roteiro-medicao.md`](../pesquisa/2-metodo/roteiro-medicao.md)) e a matriz de critérios
([`../pesquisa/2-metodo/matriz-de-criterios.md`](../pesquisa/2-metodo/matriz-de-criterios.md)).
Os dados brutos vão para [`../dados/`](../dados/) e o resultado sai em
[`../pesquisa/3-resultados/`](../pesquisa/3-resultados/resultados.md).

O estudo compara três testnets públicas: Ethereum Sepolia, Avalanche Fuji e Monad.

| Tarefa | O que faz | Onde |
|---|---|---|
| INTER-10 | Coleta T1 e T2 nas testnets | `coleta/coletar-evm.mjs` |
| INTER-15 | Complexidade ciclomática | `analise/complexidade.py` |
| INTER-18 | Consolidação dos dados | `analise/analisar.py` |
| INTER-21 | Notas, ranking e sensibilidade | `analise/benchmark.py` |

## Estrutura

```
benchmark/
├── config/              redes.json (RPC, chain ID, faucets), declarados.json (notas e pesos), projecao.json
├── coleta/              coletores (Node + viem), carteiras, implantação, preços de referência
├── analise/             estatísticas, notas, ranking, sensibilidade, gráficos e relatório (Python)
└── testes/              testes dos coletores (Node); os da análise ficam em analise/tests/
```

## Preparação

Precisa de Node 20+, Python 3.10+ com pandas e matplotlib e Foundry (`forge`). O
repositório do contrato (`projeto-inter-web3`) fica ao lado deste repositório; se estiver em
outro lugar, ajuste `WEB3_REPO` no `.env`.

```bash
npm install
cp .env.example .env      # e preencha PRIVATE_KEY
```

## Carteira e faucets

Coloque em `PRIVATE_KEY` a chave da carteira de teste que recebeu os faucets. Ela vira o admin e
financia as outras 12 contas, que o script deriva da própria chave.

| Rede | Chain ID | Faucet |
|---|---|---|
| Sepolia | 11155111 | [Google Cloud](https://cloud.google.com/application/web3/faucet/ethereum/sepolia), [Alchemy](https://www.alchemy.com/faucets/ethereum-sepolia), [PoW](https://sepolia-faucet.pk910.de) |
| Fuji | 43113 | [Builder Hub](https://build.avax.network/console/primary-network/faucet), [Core](https://core.app/tools/testnet-faucet/?subnet=c&token=c) |
| Monad | 10143 | [faucet.monad.xyz](https://faucet.monad.xyz) |

```bash
npm run carteiras -- enderecos --rede fuji     # as 13 contas
npm run carteiras -- orcamento --rede fuji     # quanto o plano consome pelo gas atual (margem 2x)
npm run carteiras -- distribuir --rede fuji    # o admin envia o que falta a cada conta
```

O plano completo consome cerca de 127 milhões de gas por rede. Se o faucet não cobrir, use
`--reduzida` em todos os comandos daquela rede (seção 11 do roteiro). A Monad cobra o gas limit,
então costuma ser a mais cara em tokens de teste.

## Coleta

Mesma ordem em todas as redes. Bloqueie a suspensão da máquina durante a coleta: uma suspensão
no meio invalida as latências.

```bash
# preços de referência da mainnet ao longo da janela de coleta (em paralelo)
systemd-inhibit --what=sleep:idle npm run precos -- --amostras 12 --intervalo 300 &

# testnets: sepolia, fuji, monad (as três no mesmo dia, na mesma janela de preços)
npm run implantar -- --rede sepolia
systemd-inhibit --what=sleep:idle npm run coletar -- --rede sepolia
```

Cada coleta grava em `../dados/`: `medicoes_<rede>_<data>.csv` (seção 6.1 do roteiro, mais
`gas_limit` e `nonce`), `preparo_<rede>_<data>.csv` (preparação do T2, fora da medição) e
`metadados_<rede>_<data>.json` (seção 6.2).

## Análise

```bash
npm run analisar
```

Lê tudo o que está em `../dados/`, usa valores medidos onde existem e, se alguma rede ainda não foi
medida, os valores de `config/projecao.json` (marcados como declarados ou hipótese). Regera
`../pesquisa/3-resultados/` (resultados.md, resumo.json e graficos/). Rode depois de cada coleta.

Gráficos e relatório marcam a origem de cada rede: `TESTNET` (medido em testnet: Sepolia, Fuji e
Monad), `PROJEÇÃO` (sem teste: documentação oficial e
hipóteses de `config/projecao.json`) e `A MEDIR` (faixa de pontuação). Nos gráficos, barra sólida =
medido; clara e hachurada = projeção; contorno tracejado = a medir. Quando uma testnet é coletada,
os valores medidos substituem a projeção automaticamente, sem mexer na configuração.

## Testes

```bash
npm test                         # 13 testes; os 3 de integração pedem um Anvil com o contrato
python3 -m pytest analise/tests  # 9 testes
```

Para os de integração:

```bash
anvil --port 8546 --block-time 1 --accounts 15 &
MNEMONIC="test test test test test test test test test test test junk" npm run implantar -- --rede anvil
MNEMONIC="test test test test test test test test test test test junk" npm test
```
