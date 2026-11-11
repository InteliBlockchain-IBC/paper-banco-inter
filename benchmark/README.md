# benchmark: como os experimentos foram feitos e como repeti-los

Este diretório tem o código que mede o contrato de crédito interfinanceiro overnight nas três
testnets do estudo (Ethereum Sepolia, Avalanche Fuji e Monad Testnet) e transforma as medições em
notas, ranking e análise de sensibilidade.

- **Especificação** do que medir e por quê: [`../pesquisa/2-metodo/roteiro-medicao.md`](../pesquisa/2-metodo/roteiro-medicao.md)
  (testes, falhas, formato dos dados) e [`../pesquisa/2-metodo/matriz-de-criterios.md`](../pesquisa/2-metodo/matriz-de-criterios.md)
  (critérios, pesos, escalas).
- **Este arquivo**: o que foi executado de fato, com quais parâmetros, e o passo a passo para repetir.
- **Saídas**: dados brutos em [`../dados/`](../dados/) e resultados em
  [`../pesquisa/3-resultados/resultados.md`](../pesquisa/3-resultados/resultados.md).

Sumário: [1. Objeto medido](#1-objeto-medido) · [2. Testes](#2-testes) ·
[3. Definições de medida](#3-definições-de-medida) · [4. A coleta de 16/10/2026](#4-a-coleta-de-16102026) ·
[5. Como repetir](#5-como-repetir) · [6. Testes automatizados](#6-testes-automatizados) ·
[7. Estrutura do código](#7-estrutura-do-código)

---

## 1. Objeto medido

**Contrato.** Repositório `projeto-inter-web3`, commit `3347bf2`: `CreditInterbankOffer` (ofertas e
aceite), `BRLToken` (real tokenizado fictício, ERC-20, 2 casas decimais) e `CDIPositionToken`
(posição de crédito, ERC-721). Solidity 0.8.24, otimizador com 200 execuções, OpenZeppelin 5.4.0.
O mesmo código foi implantado nas três redes, sem nenhuma alteração.

**Redes.**

| Rede | Testnet | Chain ID | RPC usado (público, gratuito) | Cliente informado pelo RPC | Consulta de blocos | Gas cobrado |
|---|---|---|---|---|---|---|
| Ethereum | Sepolia | 11155111 | `ethereum-sepolia-rpc.publicnode.com` | reth 2.7.0 | a cada 500 ms | gas usado |
| Avalanche (C-Chain) | Fuji | 43113 | `api.avax-test.network` | avalanchego 1.15.1 | a cada 150 ms | gas usado |
| Monad | Monad Testnet | 10143 | `testnet-rpc.monad.xyz` | Monad 0.16.3 | a cada 150 ms | gas limit |

O intervalo de consulta acompanha o tempo de bloco de cada rede (12 s na Sepolia, abaixo de 1 s nas
outras duas) e limita a resolução da latência medida. A configuração de cada rede fica em
[`config/redes.json`](config/redes.json).

**Ciclo de crédito.** Três transações, sempre nesta ordem:

1. `approve` (BRLToken): o ofertante autoriza o contrato a mover o valor exato da oferta.
2. `createOffer`: o ofertante registra a oferta, dirigida a um tomador.
3. `acceptOffer`: o tomador aceita. Numa única transação, o contrato consome o limite de crédito do
   tomador, transfere o BRLt do ofertante ao tomador e emite ao ofertante o NFT da posição. Se
   qualquer etapa falhar, nada acontece (liquidação atômica).

O cancelamento usa `createOffer` seguido de `cancelOffer`.

**Oferta usada em todas as transações:** R$ 1,00 (`amount = 100`), 100% do CDI
(`rateCDI = 10000`), prazo de 1 dia (`term = 1`) e validade de 24 h (`validityWindow = 86400`).

**Contas.** São 13 contas, todas derivadas da chave da carteira de teste: admin (implanta e
financia as demais), ofertante, tomador do T1 e 10 tomadores do T2. A implantação registra as 12
contas que operam como instituições, com limite de crédito de R$ 5 milhões e saldo de R$ 10
milhões cada.

## 2. Testes

Cada rede passa pelos mesmos dois testes, nesta ordem.

### T1: sequencial, sem carga (fornece C3 e C4-M1)

- 30 ciclos completos (`approve`, `createOffer`, `acceptOffer`) e depois 10 cancelamentos
  (`createOffer`, `cancelOffer`).
- Uma transação por vez: a próxima só é enviada depois que a anterior entra em bloco.
- Total: 30 × 3 + 10 × 2 = **110 transações por rede**.
- Valor que entra na matriz: **C3** é a mediana da latência dos 30 `acceptOffer`. **C4-M1** é o
  custo médio do ciclo (`approve` + `createOffer` + `acceptOffer`) a preços da mainnet (seção 3).

### T2: carga simultânea (fornece C1)

- **Preparação, fora da medição:** um único `approve` com o valor total e 255 `createOffer`, cada
  uma dirigida a um dos 10 tomadores em rodízio, enviadas em blocos de 16. O limite de 16 é o
  padrão de transações pendentes por conta no Geth. Essas transações vão para
  `preparo_<rede>_<data>.csv` e não entram em nenhuma nota.
- **Medição:** lotes de 10, 25 e 50 `acceptOffer`, cada tamanho repetido em 3 rodadas, num total
  de **255 transações por rede**. Em cada lote, todas as transações são assinadas antes e
  enviadas juntas. Há uma pausa de 2 s entre rodadas, para o mempool esvaziar.
- Valor que entra na matriz: **C1** é a taxa de sucesso, contando só as falhas da rede (seção 3).
  A latência do T2 é registrada, mas não entra na matriz.

Por rede são 365 transações medidas; nas três redes, 1.095.

## 3. Definições de medida

**Latência.** É o intervalo entre o envio e a inclusão em bloco:

- O início é o instante imediatamente anterior ao `eth_sendRawTransaction`. A estimativa de gas, a
  consulta de taxas e a assinatura acontecem antes desse instante, fora do tempo medido.
- O fim é o momento em que o observador de blocos do coletor, que consulta o último bloco no
  intervalo da tabela da seção 1, encontra o bloco que contém a transação.
- A medida representa a **inclusão, não a finalidade** do consenso. O modelo de finalidade de cada
  rede é registrado à parte (roteiro, seção 3.5).

**Tempo limite.** Uma transação sem inclusão em 300 s conta como falha da rede.

**Gas limit.** Em todas as redes e funções, o gas limit é a estimativa de gas × 1,2. No T2, a
estimativa é feita uma vez por tipo de transação e vale para o lote inteiro.

**Falhas.** Cada falha é classificada pelo nome do erro retornado, e não pelo momento em que ele
aparece ([`coleta/lib/falhas.mjs`](coleta/lib/falhas.mjs); roteiro, seção 5):

| Categoria | Origem | Conta em C1? |
|---|---|---|
| A | Contrato ou token (revert com erro do código) | Não |
| B | Cliente de teste (nonce, saldo, gas insuficiente) | Não |
| C | Provedor de RPC (limite de requisições, conexão) | Não |
| D | Rede: hash aceito, sem inclusão no tempo limite | **Sim** |
| X | Não reconhecida | Revisão manual antes da análise |

**Custo (C4-M1).** Como os tokens de testnet não têm valor, o custo do ciclo em dólar é calculado
assim:

- custo = gas do ciclo × preço do gas na mainnet × cotação do token nativo.
- O gas é o gas usado na Sepolia e na Fuji. Na Monad é o gas limit, porque a Monad cobra sobre o
  limite enviado, e não sobre o gas usado.
- O preço do gas vem de `eth_feeHistory` na mainnet: base fee mais a gorjeta mediana, nos últimos
  20 blocos.
- A cotação vem da CoinGecko.
- O amostrador ([`coleta/precos-referencia.mjs`](coleta/precos-referencia.mjs)) roda em paralelo à
  coleta, com uma amostra a cada 5 min. A análise usa a mediana das amostras dentro da janela da
  coleta, com 5 min de folga antes do início.

**Pausas do observador.** Se o laço do observador fica parado mais que max(10 s, 20 × intervalo),
por exemplo com a máquina suspensa ou o processo travado, a pausa é registrada nos metadados. As
linhas afetadas ficam fora das estatísticas de latência.

## 4. A coleta de 16/10/2026

Os números do estudo vêm desta coleta.

**Ambiente:**

- Uma única máquina: notebook Linux, kernel 6.17, 12 CPUs.
- RPC público gratuito nas três redes.
- Os três coletores rodaram em paralelo, um terminal por rede, com a suspensão do sistema
  bloqueada.
- O amostrador de preços rodou ao mesmo tempo. Ele gravou 20 amostras, das quais 9 caem na janela
  da coleta.

| Rede | T1 (UTC) | T2 (UTC) | Transações | Falhas | Pausas do observador |
|---|---|---|---|---|---|
| Monad | 22:40:21 – 22:43:13 | 22:44:10 – 22:44:44 | 365 | 0 | nenhuma |
| Fuji | 22:41:56 – 22:49:03 | 22:50:47 – 22:52:45 | 365 | 0 | 1 (22:51:28 – 22:52:34) |
| Sepolia | 22:52:26 – 23:15:26 | 23:20:26 – 23:22:16 | 365 | 0 | nenhuma |

A janela completa vai de 22:40 a 23:22 UTC. Os horários exatos estão em
`../dados/metadados_<rede>_2026-10-16.json`, no campo `janelas`.

**Preços de referência** (mediana das 9 amostras):

| Rede | Preço do gas | Cotação |
|---|---|---|
| Ethereum | 0,081 gwei | US$ 2.422,04 |
| Avalanche | 6,77 gwei | US$ 9,97 |
| Monad | 103 gwei | US$ 0,0229 |

**Ocorrências registradas:**

- **Pausa do observador na Fuji.** Coincide com o lote de 50 da primeira rodada do T2, que levou
  64,6 s; três aceites desse lote aparecem com cerca de 64 s. As 50 transações foram incluídas, e
  C1 não muda. As linhas ficam fora das estatísticas de latência. Ainda falta confirmar se o atraso
  foi da rede ou só da medição.
- **Glamsterdam na Sepolia.** A atualização entrou na Sepolia em 06/10/2026 e encarece a criação de
  estado; a mainnet da Ethereum ainda segue as regras anteriores. Por isso, o ciclo consome 3,50
  vezes o gas medido na Fuji, que executa o mesmo bytecode com as regras antigas. A análise mostra
  o custo da Ethereum também com o gas da Fuji. A implantação na Sepolia precisou de
  `--gas-estimate-multiplier 1000`, porque a simulação local do `forge` ainda usa as regras antigas.
  Isso afeta só a implantação, não as transações medidas.
- **Monad.** O recibo informa gas usado igual ao gas limit, coerente com a cobrança sobre o limite.

**De onde sai cada número do artigo.** Tudo é gerado por `npm run analisar`:

| Número | Arquivo | Onde |
|---|---|---|
| Latência mediana, p95 e máximo do T1 (C3) | `pesquisa/3-resultados/resultados.md` | seção de cada rede; `resumo.json` → `detalhes.<rede>.latencia_t1` |
| Taxa de sucesso e medianas por lote do T2 (C1) | idem | idem → `taxa_sucesso_t2`, `taxa_por_lote` e `latencia_t2_por_lote` |
| Gas e custo do ciclo (C4-M1) | idem | idem → `custo` |
| Notas normalizadas, pontuação e ranking | idem | tabela do ranking; `resumo.json` → `notas` e `pontuacao` |
| 17 cenários de sensibilidade | idem | seção de sensibilidade; `resumo.json` → `sensibilidade` |
| Preços de referência | `resumo.json` | `precos_referencia` |
| Complexidade ciclomática (C2-M2, M = 49) | `resumo.json` | `detalhes.<rede>.complexidade`, calculada sobre `src/` do contrato |
| Gráficos | `pesquisa/3-resultados/graficos/` | `latencia_t1.png`, `custo_ciclo.png`, `sucesso_t2.png`, `ranking.png`, `sensibilidade.png` |

As notas declaradas (C2-M1, C2-M3 e C5) e os pesos ficam em
[`config/declarados.json`](config/declarados.json), cada um com sua fonte.

## 5. Como repetir

O experimento pode ser repetido do zero; cada coleta gera arquivos novos, com a data no nome. Os
comandos abaixo rodam dentro de `benchmark/`.

### 5.1 Pré-requisitos

- Node 20 ou superior.
- Python 3.10 ou superior, com `pandas`, `matplotlib` e `pytest`.
- Foundry (`forge`).
- O repositório do contrato, `projeto-inter-web3`, ao lado deste repositório. Para repetir
  exatamente, use o commit `3347bf2`. Se o repositório estiver em outro lugar, ajuste `WEB3_REPO`
  no `.env`.

```bash
npm install
cp .env.example .env
```

### 5.2 Carteira

1. Coloque em `PRIVATE_KEY` a chave de uma carteira **só de teste**, sem fundos reais.
2. Peça tokens nos faucets para essa carteira. Ela vira o admin e financia as outras 12 contas.

| Rede | Faucets |
|---|---|
| Sepolia | [Google Cloud](https://cloud.google.com/application/web3/faucet/ethereum/sepolia), [Alchemy](https://www.alchemy.com/faucets/ethereum-sepolia), [PoW](https://sepolia-faucet.pk910.de) |
| Fuji | [Builder Hub](https://build.avax.network/console/primary-network/faucet), [Core](https://core.app/tools/testnet-faucet/?subnet=c&token=c) |
| Monad | [faucet.monad.xyz](https://faucet.monad.xyz) |

Depois, para cada rede:

```bash
npm run carteiras -- enderecos  --rede fuji   # lista as 13 contas
npm run carteiras -- orcamento  --rede fuji   # quanto o plano consome pelo gas atual (margem de 2x)
npm run carteiras -- distribuir --rede fuji   # o admin envia a cada conta o que falta
```

O plano completo consome cerca de 127 milhões de gas por rede. A Monad cobra o gas limit e por
isso é a que mais gasta em tokens de teste. Se o faucet não cobrir, use `--reduzida` em todos os
comandos daquela rede: 20 ciclos sem cancelamentos e lotes de 10 e 50 em 2 rodadas (roteiro,
seção 11). Registre a escolha, porque ela muda o plano daquela rede.

**Não altere** `MULTIPLICADOR_GAS=1.2`, `TEMPO_LIMITE_S=300` e `N_TOMADORES_T2=10` no `.env`. Eles
precisam ser iguais em todas as redes.

### 5.3 Implantação (uma vez por rede)

```bash
npm run implantar -- --rede sepolia
npm run implantar -- --rede fuji
npm run implantar -- --rede monad
```

Para cada rede, o script:

1. Gera `script/config/bench-<rede>.json` no repositório do contrato, com as 12 instituições e os
   mesmos valores em todas as redes.
2. Roda `forge script script/Deploy.s.sol --broadcast`, sem alterar o contrato.
3. Copia os endereços para `../dados/implantacoes/<rede>.json`. O registro do `forge` vai para
   `../dados/implantacoes/broadcast/`.

O nome `bench-` evita sobrescrever a implantação oficial do time.

### 5.4 Coleta

Rode tudo no mesmo dia e na mesma janela, para que as redes compartilhem os preços de referência.
Bloqueie a suspensão da máquina: uma suspensão no meio da coleta invalida as latências.

```bash
# terminal 1: amostrador de preços, em paralelo a toda a coleta (uma amostra a cada 5 min)
systemd-inhibit --what=sleep:idle npm run precos -- --amostras 36 --intervalo 300

# terminais 2, 3 e 4: um coletor por rede, em paralelo
systemd-inhibit --what=sleep:idle npm run coletar -- --rede monad   | tee ../dados/coleta_monad.log
systemd-inhibit --what=sleep:idle npm run coletar -- --rede fuji    | tee ../dados/coleta_fuji.log
systemd-inhibit --what=sleep:idle npm run coletar -- --rede sepolia | tee ../dados/coleta_sepolia.log
```

O coletor roda o T1 e depois o T2. Opções:

| Opção | Efeito |
|---|---|
| `--teste T1` ou `--teste T2` | Roda só um dos testes |
| `--reduzida` | Usa o plano reduzido |
| `--data AAAA-MM-DD` | Grava num arquivo de data já existente |

Para cada rede, a coleta grava em `../dados/`:

| Arquivo | Conteúdo |
|---|---|
| `medicoes_<rede>_<data>.csv` | Uma linha por transação medida (roteiro, seção 6.1, mais `gas_limit` e `nonce`) |
| `preparo_<rede>_<data>.csv` | A preparação do T2 |
| `metadados_<rede>_<data>.json` | RPC, cliente, máquina, contratos, contas, parâmetros, janelas, pausas e erros de consulta |

O amostrador grava em `precos_referencia_<data>.json`.

**Antes de aceitar uma coleta, confira:**

- Nenhuma falha de categoria X (coluna `categoria_falha`).
- `pausas_observador` vazio nos metadados. Se houver pausa, ela precisa ficar documentada.
- `erros_consulta_blocos` baixo nos metadados.
- As três redes coletadas dentro da janela das amostras de preço.

### 5.5 Análise

```bash
npm run analisar
```

O comando:

1. Lê tudo o que está em `../dados/`.
2. Calcula as estatísticas, a complexidade do contrato (lida de `src/` do repositório do contrato),
   as notas min-max, a pontuação ponderada e os 16 cenários de sensibilidade além do base.
3. Regera `../pesquisa/3-resultados/` (`resultados.md`, `resumo.json` e `graficos/`).

Se houver mais de uma coleta, a análise usa o arquivo de preços mais recente.

O arquivo [`config/projecao.json`](config/projecao.json) só é usado quando uma rede ainda não tem
dados medidos. Com as três testnets coletadas, ele não afeta nenhum número.

## 6. Testes automatizados

```bash
npm test                         # 13 testes dos coletores; os 3 de integração pedem um Anvil
python3 -m pytest analise/tests  # 9 testes da análise (normalização, pontuação, sensibilidade)
```

Para rodar os testes de integração contra um Anvil local, com o contrato implantado:

```bash
anvil --port 8546 --block-time 1 --accounts 15 &
MNEMONIC="test test test test test test test test test test test junk" npm run implantar -- --rede anvil
MNEMONIC="test test test test test test test test test test test junk" npm test
```

## 7. Estrutura do código

```
benchmark/
├── config/
│   ├── redes.json            RPC, chain ID, intervalo de consulta, cobrança de gas, faucets
│   ├── declarados.json       pesos e notas declaradas (C2-M1, C2-M3, C5), com fonte
│   └── projecao.json         valores usados só se uma rede não tiver medição
├── coleta/                   Node + viem
│   ├── carteiras.mjs         contas, orçamento e distribuição de saldo
│   ├── implantar.mjs         implantação do contrato com forge
│   ├── coletar-evm.mjs       T1 e T2
│   ├── precos-referencia.mjs amostras de preço de gas e cotação
│   └── lib/                  envio e observação de blocos, classificação de falhas, utilidades
├── analise/                  Python
│   ├── analisar.py           ponto de entrada: consolida dados e regera os resultados
│   ├── benchmark.py          estatísticas, normalização, pontuação e sensibilidade
│   ├── complexidade.py       complexidade ciclomática do contrato (C2-M2)
│   ├── graficos.py, relatorio.py
│   └── tests/
└── testes/                   testes dos coletores
```
