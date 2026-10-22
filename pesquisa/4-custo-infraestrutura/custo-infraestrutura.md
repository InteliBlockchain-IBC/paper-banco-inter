# Custo de infraestrutura (C4-M2)

Levantamento feito conforme a seção 8.4 do [roteiro de medição](../2-metodo/roteiro-medicao.md). **Estado:** levantamento concluído. Conforme a decisão da equipe, os valores são **descritivos** e não entram na pontuação do ranking (ver seção 5).

## 1. Cenário

Três participantes operando o protocolo, os mesmos dos testes: ofertante, tomador e admin (que simula o Banco Central).

| Rede | Nós considerados |
|---|---|
| Ethereum (Sepolia), Avalanche (Fuji), Monad | 1 nó próprio por participante: 3 no total |

## 2. Requisitos mínimos de hardware (documentação oficial)

| Rede | CPU | Memória | Disco | Fonte |
|---|---|---|---|---|
| Ethereum (Geth) | 4 núcleos | 16 GB | SSD de 2 TB para nó completo com cliente de consenso (valor da mainnet; a Sepolia exige menos) | geth.ethereum.org/docs/getting-started/hardware-requirements |
| Avalanche (validador, estaca baixa) | 4 núcleos / 8 threads | 16 GB | 1 TB NVMe **local**, mínimo de 3.000 IOPS. Armazenamento de bloco em nuvem (EBS) não é recomendado | build.avax.network/docs/nodes/system-requirements |
| Monad | 16 núcleos a 4,5 GHz ou mais | 32 GB | 2 TB para o TrieDB e 500 GB para o sistema, ambos NVMe PCIe Gen4 x4 | docs.monad.xyz/node-ops/hardware-requirements |

## 3. Instâncias e custo mensal

**Provedor:** AWS EC2, região `us-east-1`, Linux, sob demanda. **Consulta:** 19/10/2026, na lista de preços espelhada por instances.vantage.sh. Critério: instância x86_64 mais barata que atende ao requisito, sem as famílias de desempenho variável (`t3`, `t3a`), que não servem para um nó que roda o tempo todo.

`custo mensal = preço por hora × 730 × número de nós`

| Rede | Instância | vCPU / RAM | US$ por hora | Nós | **US$ por mês** |
|---|---|---|---|---|---|
| Ethereum (Sepolia) | `m5a.xlarge` | 4 / 16 GB | 0,172 | 3 | **376,68** |
| Avalanche (Fuji) | `i4i.2xlarge` | 8 / 64 GB, 1.875 GB NVMe local | 0,686 | 3 | **1.502,34** |
| Monad | `m5zn.metal` | 48 / 192 GB, 4,5 GHz | 3,9641 | 3 | **8.681,38** |

## 4. Ressalvas

1. **Monad em nuvem.** A documentação exige servidor físico (*bare metal*) e diz que ambientes de nuvem, como o AWS EC2, não são oficialmente suportados. A `m5zn.metal` é o servidor físico mais barato da AWS com 4,5 GHz, mas não tem NVMe local, então o disco do TrieDB ficaria fora do cálculo. O valor é uma referência, não uma configuração suportada. Se a equipe preferir uma instância virtual com 16 vCPU e 32 GB (`c7i.4xlarge`, US$ 0,714 por hora), o custo cai para **US$ 1.563,66 por mês**.
2. **Armazenamento.** Só o Avalanche tem o disco incluído no preço da instância, porque a documentação exige NVMe local. Nas demais redes o disco (EBS) é cobrado à parte e não entrou na fórmula do roteiro, o que favorece a Ethereum e a Monad na comparação.
3. **Ethereum e Avalanche.** Os requisitos são os das mainnets. Os testes rodaram nas testnets Sepolia e Fuji, que exigem menos.
4. **Um único provedor e uma única data.** O valor depende do provedor, da região e do dia da consulta, como registra a ameaça 10 da matriz.

## 5. Tratamento no ranking (decisão da equipe)

Por decisão da equipe (19/10/2026), o C4-M2 **não entra na pontuação**: os valores acima ficam como informação descritiva e o C4 do ranking continua sendo o custo por transação (C4-M1).

O ranking oficial não muda: Monad 90,1, Avalanche 86,0 e Ethereum 58,5.

Análise de robustez, feita à parte: com o C4-M2 na pontuação (C4 = média de C4-M1 e C4-M2), a ordem depende da instância escolhida para a Monad.

| Monad em | Ranking com o C4-M2 |
|---|---|
| Servidor físico `m5zn.metal` (US$ 8.681,38 por mês, exigência da documentação) | Avalanche 85,7; Monad 82,2; Ethereum 66,4 |
| Instância virtual `c7i.4xlarge` (US$ 1.563,66 por mês) | Monad 82,2; Avalanche 79,2; Ethereum 66,4 |
