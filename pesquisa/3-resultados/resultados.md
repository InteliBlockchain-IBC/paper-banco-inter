# Resultados do benchmark

> Arquivo gerado por `benchmark/analise/analisar.py` em 22/10/2026 14:31 UTC. Não edite à mão: depois de cada coleta, rode `npm run analisar` dentro de `benchmark/`.

## De onde vem cada número

| Etiqueta | Origem | O que significa | Redes hoje |
|---|---|---|---|
| `TESTNET` | Medido em testnet | A equipe rodou o contrato na testnet pública da rede, com outros usuários e RPC público | Ethereum Sepolia, Avalanche Fuji, Monad |
| `PROJEÇÃO` | Projeção, sem teste | Nenhum teste nosso: latência da documentação oficial, custo calculado com o gas medido em outra rede e 100% de sucesso como hipótese | — |
| `A MEDIR` | A medir | Sem teste e sem valor provisório para algum critério: a pontuação aparece como faixa | — |

## Situação da coleta

| Rede | Origem dos números | T1 | T2 | Coletado em |
|---|---|---|---|---|
| Ethereum Sepolia | `TESTNET` medido em testnet | 30 aceites | 255 aceites | 2026-10-16 |
| Avalanche Fuji | `TESTNET` medido em testnet | 30 aceites | 255 aceites | 2026-10-16 |
| Monad | `TESTNET` medido em testnet | 30 aceites | 255 aceites | 2026-10-16 |

## Ranking

![Pontuação por rede](graficos/ranking.png)

| Posição | Rede | Origem | C1 | C2 | C3 | C4 | C5 | Pontuação |
|---|---|---|---|---|---|---|---|---|
| 1 | Monad | `TESTNET` medido em testnet | 1,00 | 0,67 | 1,00 | 1,00 | 1,00 | **90,1** |
| 2 | Avalanche Fuji | `TESTNET` medido em testnet | 1,00 | 0,67 | 0,84 | 0,91 | 1,00 | **86,0** |
| 3 | Ethereum Sepolia | `TESTNET` medido em testnet | 1,00 | 0,67 | 0,00 | 0,00 | 1,00 | **58,5** |

Notas de 0 a 1 (min-max entre as 3 redes); pesos C1 29,78%, C2 29,78%, C3 15,78%, C4 15,78%, C5 8,88%. C2 e C5 vêm de documentação e do código em todas as redes. Pontuação em faixa: critérios ainda sem valor podem ir de 0 a 1.
C1, C2, C5 dão a mesma nota a todas as redes e não mudam a ordem: a diferença entre elas vem só dos outros critérios.
C4 usa só o custo por transação (C4-M1). O custo de infraestrutura (C4-M2) foi levantado em `pesquisa/4-custo-infraestrutura/` e, por decisão da equipe, fica como informação descritiva, fora da pontuação.

## Sensibilidade aos pesos

![Sensibilidade](graficos/sensibilidade.png)

O primeiro lugar muda em 0 de 17 cenários.

## Escolhas de método que podem mudar a conclusão

O ranking refeito com cada alternativa (pesos do cenário base):

| Escolha | 1º lugar | Pontuação por rede |
|---|---|---|
| **Adotada** (roteiro) | Monad | Monad 90,1; Avalanche Fuji 86,0; Ethereum Sepolia 58,5 |
| Custo da Ethereum com o gas das regras atuais da mainnet (pré-Glamsterdam, medido na Fuji), em vez do gas medido na Sepolia | Monad | Monad 90,1; Avalanche Fuji 82,2; Ethereum Sepolia 58,5 |

## Custo por ciclo a preços da mainnet (C4-M1)

![Custo por ciclo](graficos/custo_ciclo.png)

| Rede | Origem do custo | Gas cobrado por ciclo | Preço de referência | Cotação | Custo do ciclo |
|---|---|---|---|---|---|
| Ethereum Sepolia | `TESTNET` medido em testnet | 1.502.836 | 0,081 gwei | US$ 2.422,04 | US$ 0,29611 |
| Avalanche Fuji | `TESTNET` medido em testnet | 429.924 | 6,772 gwei | US$ 9,97 | US$ 0,02903 |
| Monad | `TESTNET` medido em testnet | 602.935 | 103,000 gwei | US$ 0,0229 | US$ 0,00142 |

Preços: mediana de 9 amostra(s) entre 2026-10-16T22:38 e 2026-10-16T23:19 UTC (eth_feeHistory e CoinGecko).

### Ethereum: gas da Sepolia × regras atuais da mainnet

A Sepolia ativou o Glamsterdam em 06/10/2026, que encarece a criação de estado (contas, posições de armazenamento e código). A mainnet ainda usa as regras anteriores. O roteiro (seção 3.3) supõe o mesmo gas na testnet e na mainnet; para a Ethereum essa premissa deixou de valer durante este estudo. Como referência das regras atuais da mainnet usa-se o gas medido na Fuji: a C-Chain executa o mesmo bytecode com as regras de gas anteriores ao Glamsterdam. A C-Chain não devolve gas por limpeza de armazenamento, então a referência pode ficar um pouco acima do gas real da mainnet (aproximação conservadora).

| Função | Gas na Sepolia (Glamsterdam) | Gas pelas regras anteriores (Fuji) | Razão |
|---|---|---|---|
| `approve` | 128.257 | 46.337 | 2,77× |
| `createOffer` | 927.005 | 220.324 | 4,21× |
| `acceptOffer` | 446.758 | 163.120 | 2,74× |
| `cancelOffer` | 133.830 | 51.810 | 2,58× |
| **Ciclo completo** | **1.502.836** | **429.924** | **3,50×** |

Custo do ciclo a preços da mainnet: US$ 0,2961 com o gas da Sepolia (valor usado na matriz, como manda o roteiro) e US$ 0,0847 com as regras anteriores, ainda em vigor na mainnet. A Ethereum é a rede mais cara nos dois casos, então a nota dela em C4-M1 é 0 nos dois e a ordem do ranking não muda; mudam o valor absoluto citado no artigo e, um pouco, as notas de custo das outras redes (ver "Escolhas de método").

## Latência e taxa de sucesso medidas

![Latência no T1](graficos/latencia_t1.png)

![Taxa de sucesso no T2](graficos/sucesso_t2.png)

Os dois gráficos só mostram redes medidas.

## Fichas por rede

Se uma ficha mostrar "—", a rede ainda não foi coletada e a matriz usa os valores provisórios dela.

### Ethereum Sepolia

**Ambiente:** Testnet pública Sepolia (chain ID 11155111).

**Origem dos números:** `TESTNET` medido em testnet.

**Coleta:** T1 de 2026-10-16 22:52 a 23:15 UTC; T2 de 2026-10-16 23:20 a 23:22 UTC. RPC: público gratuito. Cliente: `reth/v2.7.0-3d592ec/x86_64-unknown-linux-gnu`. Dados brutos: `../../dados/medicoes_sepolia_2026-10-16.csv`.

**T1, latência do `acceptOffer` (C3):**

| n | Média | Mediana | p95 | Máximo | Até 30 s |
|---|---|---|---|---|---|
| 30 | 11,35 s | 11,04 s | 11,98 s | 22,02 s | 100% |

**T1, gas e custo por função (C4-M1):**

| Função | Gas médio (gas usado) | Custo médio (USD) |
|---|---|---|
| `approve` | 128.257 | 0,02527 |
| `createOffer` | 927.005 | 0,18265 |
| `acceptOffer` | 446.758 | 0,08803 |
| `cancelOffer` | 133.830 | 0,02637 |
| **Ciclo completo** | **1.502.836** | **0,29611** |

**T2, carga simultânea (C1):**

| Lote | Taxa de sucesso | Latência mediana sob carga | p95 sob carga |
|---|---|---|---|
| 10 | 100,0% | 9,39 s | 9,91 s |
| 25 | 100,0% | 8,85 s | 10,14 s |
| 50 | 100,0% | 7,65 s | 10,12 s |
| **Total** | **100,0%** (255 de 255) | | |

Falhas: A 0 · B 0 · C 0 · D 0 · X 0 (só D conta contra a rede).

### Avalanche Fuji

**Ambiente:** Testnet pública Fuji, C-Chain (chain ID 43113).

**Origem dos números:** `TESTNET` medido em testnet.

**Coleta:** T1 de 2026-10-16 22:41 a 22:49 UTC; T2 de 2026-10-16 22:50 a 22:52 UTC. RPC: público gratuito. Cliente: `avalanchego/1.15.1 [database=v1.4.5, rpcchainvm=46, commit=fdb2c1b9b02ef357b5867d5ababb6acc83837a01, go=1.26.8]`. Dados brutos: `../../dados/medicoes_fuji_2026-10-16.csv`.

**Atenção:** 1 pausa(s) do observador; as linhas afetadas ficam fora das estatísticas de latência.

**T1, latência do `acceptOffer` (C3):**

| n | Média | Mediana | p95 | Máximo | Até 30 s |
|---|---|---|---|---|---|
| 30 | 2,60 s | 2,64 s | 3,03 s | 3,13 s | 100% |

**T1, gas e custo por função (C4-M1):**

| Função | Gas médio (gas usado) | Custo médio (USD) |
|---|---|---|
| `approve` | 46.337 | 0,00313 |
| `createOffer` | 220.324 | 0,01487 |
| `acceptOffer` | 163.120 | 0,01101 |
| `cancelOffer` | 51.810 | 0,00350 |
| **Ciclo completo** | **429.924** | **0,02903** |

**T2, carga simultânea (C1):**

| Lote | Taxa de sucesso | Latência mediana sob carga | p95 sob carga |
|---|---|---|---|
| 10 | 100,0% | 2,47 s | 3,29 s |
| 25 | 100,0% | 2,40 s | 3,38 s |
| 50 | 100,0% | 3,49 s | 4,08 s |
| **Total** | **100,0%** (255 de 255) | | |

Falhas: A 0 · B 0 · C 0 · D 0 · X 0 (só D conta contra a rede).

### Monad

**Ambiente:** Testnet pública Monad (chain ID 10143).

**Origem dos números:** `TESTNET` medido em testnet.

**Coleta:** T1 de 2026-10-16 22:40 a 22:43 UTC; T2 de 2026-10-16 22:44 a 22:44 UTC. RPC: público gratuito. Cliente: `Monad/0.16.3`. Dados brutos: `../../dados/medicoes_monad_2026-10-16.csv`.

**T1, latência do `acceptOffer` (C3):**

| n | Média | Mediana | p95 | Máximo | Até 30 s |
|---|---|---|---|---|---|
| 30 | 0,99 s | 0,99 s | 1,56 s | 1,74 s | 100% |

**T1, gas e custo por função (C4-M1):**

| Função | Gas médio (gas limit) | Custo médio (USD) |
|---|---|---|
| `approve` | 63.497 | 0,00015 |
| `createOffer` | 257.152 | 0,00061 |
| `acceptOffer` | 282.441 | 0,00067 |
| `cancelOffer` | 63.519 | 0,00015 |
| **Ciclo completo** | **602.935** | **0,00142** |

**T2, carga simultânea (C1):**

| Lote | Taxa de sucesso | Latência mediana sob carga | p95 sob carga |
|---|---|---|---|
| 10 | 100,0% | 0,80 s | 0,80 s |
| 25 | 100,0% | 1,04 s | 1,60 s |
| 50 | 100,0% | 1,10 s | 1,33 s |
| **Total** | **100,0%** (255 de 255) | | |

Falhas: A 0 · B 0 · C 0 · D 0 · X 0 (só D conta contra a rede).
