# benchmark-redes

Coleta e análise dos dados medidos do paper. Implementa o roteiro de medição
([`../docs/roteiro-medicao.md`](../docs/roteiro-medicao.md)) e a matriz de critérios
([`../docs/matriz-de-criterios.md`](../docs/matriz-de-criterios.md)). O resultado sai em
[`../docs/resultados.md`](../docs/resultados.md).

| Tarefa | O que faz | Onde |
|---|---|---|
| INTER-10 | Coleta T1 e T2 nas redes EVM | `src/coletar-evm.mjs` |
| INTER-14 | Coleta na Canton | `src/coletar-canton.mjs`, `canton/daml/` |
| INTER-15 | Complexidade ciclomática | `analise/complexidade.py` |
| INTER-18 | Consolidação dos dados | `analise/analisar.py` |
| INTER-21 | Notas, ranking e sensibilidade | `analise/benchmark.py` |

## Estrutura

```
config/        redes.json (RPC, chain ID, faucets), declarados.json (notas e pesos), projecao.json
src/           coletores (Node + viem), carteiras, implantação, preços de referência
besu/          rede Besu QBFT local com 4 validadores (Docker)
canton/daml/   versão Daml do contrato, com testes em Daml Script
analise/       estatísticas, notas, ranking, sensibilidade, gráficos e relatório
dados/         CSVs e metadados de cada coleta (um arquivo por rede e dia)
resultados/    gráficos PNG e resumo.json da última análise
test/          testes dos coletores (Node)
```

## Preparação

Precisa de Node 20+, Python 3.10+ com pandas e matplotlib, Foundry (`forge`) e Docker. O
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
| Besu | 13371 | não precisa (gas grátis) |

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

# redes EVM públicas: sepolia, fuji, monad
npm run implantar -- --rede sepolia
systemd-inhibit --what=sleep:idle npm run coletar -- --rede sepolia

# Besu local
./besu/gerar-rede.sh --limpar
npm run implantar -- --rede besu
systemd-inhibit --what=sleep:idle npm run coletar -- --rede besu
```

Cada coleta grava em `dados/`: `medicoes_<rede>_<data>.csv` (seção 6.1 do roteiro, mais
`gas_limit` e `nonce`), `preparo_<rede>_<data>.csv` (preparação do T2, fora da medição) e
`metadados_<rede>_<data>.json` (seção 6.2).

### Canton

```bash
# 1. LocalNet (pré-requisitos: Nix, direnv, docker login)
git clone https://github.com/digital-asset/cn-quickstart.git && cd cn-quickstart && direnv allow
cd quickstart && make setup && make build && make start
#    para zerar o ledger antes de cada rodada: make clean-docker && make start

# 2. Modelo Daml (dentro de benchmark-redes/canton/daml)
dpm build && dpm test

# 3. Enviar o DAR ao participante
curl -X POST -H "Authorization: Bearer $CANTON_TOKEN" -H 'content-type: application/octet-stream' \
  --data-binary @.daml/dist/credit-interbank-1.0.0.dar "$CANTON_API/v2/packages"

# 4. Coletar (variáveis CANTON_* no .env)
npm run coletar:canton
```

O coletor cria sozinho o estado inicial, com as mesmas contas e valores das redes EVM. Os caminhos da
JSON Ledger API v2 estão marcados como [CONFERIR] em `src/coletar-canton.mjs`; compare com o
Swagger do LocalNet (`make open-swagger-ui`) antes da rodada.

## Análise

```bash
npm run analisar
```

Lê tudo o que está em `dados/`, usa valores medidos onde existem e, nas redes ainda não medidas,
os valores de `config/projecao.json` (marcados como declarados, projetados ou hipótese). Regera
`../docs/resultados.md`, `resultados/resumo.json` e os gráficos. Rode depois de cada coleta.

## Testes

```bash
npm test                         # 18 testes; os 3 de integração pedem um Anvil com o contrato
python3 -m pytest analise/tests  # 9 testes
```

Para os de integração:

```bash
anvil --port 8546 --block-time 1 --accounts 15 &
MNEMONIC="test test test test test test test test test test test junk" npm run implantar -- --rede anvil
MNEMONIC="test test test test test test test test test test test junk" npm test
```
