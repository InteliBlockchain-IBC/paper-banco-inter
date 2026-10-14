# Matriz de critérios: base para construção

Documento de apoio para a frente de Pesquisa. Não é a matriz final, é o insumo para montá-la.

Fonte principal: Masama, Kannengießer e Sunyaev (2025), *From Concept to Measurement: A Survey of How the Blockchain Trilemma Is Analyzed*, arXiv:2505.03768.

---

## 1. Ressalva sobre o enquadramento pelo trilema

O trilema cobre três subconceitos: grau de descentralização (DoD), escalabilidade e segurança. O paper de referência cataloga 14 construtos e 16 métricas distribuídos entre eles.

Dois parâmetros que o caso de uso exige não pertencem a nenhum desses subconceitos:

- **Custo por operação** (gas por função de contrato). Fu et al., citados no paper, usam taxa média de transação como proxy de segurança, mas isso é um uso indireto. Custo operacional como critério de viabilidade não é construto do trilema.
- **Compatibilidade EVM**. É restrição de portabilidade do código, não propriedade do sistema distribuído.

Recomendação: declarar o trilema como lente teórica principal e explicitar que dois critérios foram adicionados a partir dos requisitos do TAP. Apresentar a matriz como puramente derivada do trilema seria impreciso, e essa imprecisão é visível para quem conhece a literatura.

---

## 2. Onde encontrar cada métrica no paper

Todas as equações estão na Seção IV-A. A Tabela II lista os 14 construtos com definição. A Tabela III mostra quais abordagens de análise usam quais métricas.

| Subconceito | Construtos disponíveis | Equações |
|---|---|---|
| DoD | Aleatoriedade de proposição de bloco, diversidade geográfica, distribuição de poder de hash, concentração de tokens, distribuição de riqueza | 1, 3, 9, 10, 12 |
| Escalabilidade | Disponibilidade, latência de confirmação, throughput | 15, 16, 17, 22, 23 |
| Segurança | Disponibilidade, consistência, custo de ataque, tolerância a falhas, confiabilidade, taxa de blocos órfãos | 27, 30, 31, 32, 35, 36 |

---

## 3. Critérios propostos

Oito critérios. Se precisarem reduzir para sete, o candidato a corte é throughput (justificativa no item 3.7).

### 3.1 Tempo até finalidade

**Construto:** latência de confirmação (escalabilidade).
**Paper:** equações 16 e 17. A eq. 16 mede `BConfTime - BPropTime`. A eq. 17 mede `SecConf × BCI` e é a adequada para redes com finalidade probabilística.
**Definição operacional:** tempo, em segundos, entre a submissão da transação e o ponto em que ela é irreversível segundo o mecanismo de consenso da rede.
**Como medir no projeto:** timestamps de proposição e confirmação extraídos do explorador de cada rede, conforme o procedimento exemplificado no paper com dados do Etherscan. Para a Sepolia, medição direta via script.
**Peso: 5.** O RNF02 exige confirmação visível em até 30 segundos após o aceite. O RF03 exige liquidação atômica, que só faz sentido se a transação for irreversível. Confirmação em bloco não basta: uma reversão desfaz a liquidação.

### 3.2 Taxa de sucesso de transações

**Construto:** disponibilidade (escalabilidade).
**Paper:** equação 15, `ASca = NumOfConfTr / NumOfTr × 100%`.
**Definição operacional:** proporção de transações submetidas que chegam a ser confirmadas, em janela de observação declarada.
**Como medir no projeto:** contagem de submissões versus confirmações nos scripts de coleta. Complementar com dados publicados: o paper de falhas na Solana (arXiv:2504.18055) reporta 6,22% para contas humanas contra 1% a 3% no Ethereum.
**Peso: 4.** Em liquidação atômica, uma transação que falha é uma operação de crédito não concluída. Diferente de uma aplicação de consumo, não há retentativa silenciosa aceitável.

### 3.3 Custo por operação de contrato

**Construto:** fora do trilema.
**Paper de apoio:** arXiv:2503.01397 mede gas e latência por função de contrato, que é o recorte correto. Não usar custo de transferência simples como proxy.
**Definição operacional:** custo em USD para executar cada função do ciclo (ofertar, aceitar, liquidar, cancelar), considerando gas consumido e preço do token nativo na data da coleta.
**Como medir no projeto:** `forge test --gas-report` fornece o gas por função. A conversão para USD exige preço do gas e cotação do token, ambos com data registrada.
**Peso: 4.** Determina a viabilidade operacional. Uma rede em que o ciclo completo custa ordens de grandeza a mais inviabiliza o volume de operações de uma mesa.

### 3.4 Custo de ataque

**Construto:** custo de ataque (segurança).
**Paper:** equação 31, `CoA = t × c × Σsi`. O paper traz exemplos calculados para Bitcoin e Ethereum.
**Definição operacional:** custo em USD para acumular recursos suficientes para controlar o consenso da rede, com limiar declarado.
**Como medir no projeto:** dados públicos de stake total ou poder de hash, número de validadores e cotação do token. Cálculo pela equação, com data de coleta.
**Peso: 4.** O valor em risco em uma operação de crédito interbancário é alto. O paper aponta a limitação do construto: ele considera um único vetor de ataque. Declarar qual vetor foi escolhido.

### 3.5 Compatibilidade EVM

**Construto:** fora do trilema.
**Definição operacional:** classificação em três níveis, a serem definidos pela equipe, quanto ao esforço de portar contratos Solidity existentes para a rede.
**Como medir no projeto:** documentação oficial de cada rede e verificação de suporte às ferramentas já usadas no projeto.
**Peso: 3.** O TAP fixa Solidity e Foundry. Uma rede não compatível implica reescrita, o que é custo real de adoção, mas não inviabiliza a operação em si.

### 3.6 Consistência e taxa de blocos órfãos

**Construto:** consistência e taxa de blocos órfãos (segurança).
**Paper:** equação 30 para consistência, equação 36 para `SBR = NumberOfStaleBlocks / NumberOfConfirmedBlocks`.
**Definição operacional:** proporção de blocos propagados que não são finalizados na cadeia principal, em janela declarada.
**Como medir no projeto:** dados de exploradores. Atenção: o paper registra que a métrica se aplica a redes com consistência eventual e não vale para redes com finalidade imediata.
**Peso: 2.** Captura risco de reversão, que é relevante. Peso baixo porque há sobreposição parcial com o critério 3.1 e porque a métrica não se aplica a parte das redes candidatas, o que enfraquece a comparabilidade.

### 3.7 Throughput

**Construto:** throughput (escalabilidade).
**Paper:** equação 22, `TPS = NumOfConfTr / (t1 - t0)`. A eq. 23 é alternativa específica para Ethereum.
**Definição operacional:** transações confirmadas por segundo, em janela declarada.
**Como medir no projeto:** dados de exploradores ou do paper arXiv:2606.22206, que traz séries de TPS para Ethereum, Polygon, Solana e L2s entre 2024 e 2026.
**Peso: 2.** É o critério mais citado na literatura e o menos relevante aqui. O volume de operações de CDI overnight entre um conjunto restrito de instituições é baixo. Manter o critério com peso baixo é mais defensável do que omiti-lo, porque a omissão de uma métrica central da literatura exigiria justificativa mais longa.

### 3.8 Distribuição de poder de consenso

**Construto:** distribuição de poder de hash, via coeficiente de Nakamoto (DoD).
**Paper:** equação 9, `NC = min{k : Σpi ≥ threshold}`.
**Definição operacional:** número mínimo de entidades necessárias para ultrapassar o limiar de controle do consenso.
**Como medir no projeto:** dados públicos de distribuição de stake ou de pools, com data de coleta.
**Peso: 2.** Sem esse critério, o subconceito DoD fica inteiramente ausente e o enquadramento pelo trilema deixa de se sustentar. Peso baixo porque, no contexto bancário, maior descentralização não é automaticamente melhor: redes permissionadas têm DoD baixo por projeto e isso é característica desejada, não defeito. Essa ambiguidade precisa ser registrada na interpretação do critério, senão a pontuação penaliza redes que o caso de uso favorece.

---

## 4. Pesos consolidados

| # | Critério | Peso bruto | Peso normalizado |
|---|---|---|---|
| 1 | Tempo até finalidade | 5 | 0,192 |
| 2 | Taxa de sucesso de transações | 4 | 0,154 |
| 3 | Custo por operação de contrato | 4 | 0,154 |
| 4 | Custo de ataque | 4 | 0,154 |
| 5 | Compatibilidade EVM | 3 | 0,115 |
| 6 | Consistência e blocos órfãos | 2 | 0,077 |
| 7 | Throughput | 2 | 0,077 |
| 8 | Distribuição de poder de consenso | 2 | 0,077 |
| | **Total** | **26** | **1,000** |

Normalização: peso bruto dividido pela soma dos pesos brutos.

Agregação sugerida: `Pontuação(rede) = Σ (nota_normalizada_no_critério × peso_normalizado)`. As notas precisam ser normalizadas antes, porque as escalas são incompatíveis entre si (segundos, dólares, percentuais, contagens). Definir a função de normalização e declará-la na metodologia.

Os pesos acima são uma proposta de partida. A atribuição final deve passar pela discussão da equipe, e o processo dessa discussão é parte da metodologia.

---

## 5. Construtos avaliados e descartados

Registrar os descartes é entrega da semana 1 e compõe o rigor metodológico.

| Construto | Motivo do descarte |
|---|---|
| Diversidade geográfica (eq. 3) | O paper aponta que não há definição clara de "localização" e que os nós podem ocultar posição via VPN. Dado não confiável para redes públicas. |
| Concentração de tokens (eq. 10) e distribuição de riqueza (eq. 12) | Capturam aspecto econômico de DoD, já parcialmente coberto pelo critério 3.8. Incluir os três seria redundância dentro do mesmo subconceito. |
| Aleatoriedade de proposição de bloco (eq. 1) | Requer dados de proposição por nó, de coleta custosa, e o paper registra que a métrica ignora quais blocos são de fato finalizados. |
| Tolerância a falhas (eq. 32) | Exige medição sob falha induzida de nós validadores, fora do alcance do projeto. |
| Confiabilidade (eq. 35) e disponibilidade de segurança (eq. 27) | Dependem de MTBF e MTTR, que exigem histórico de falhas por rede. O paper registra que a literatura não enfatiza esses construtos em análises de blockchain. |

---

## 6. Limitação a declarar na metodologia

O RNF01 restringe a execução à testnet Sepolia. Isso tem duas consequências para a pesquisa:

A medição empírica direta fica limitada ao ambiente do projeto. Dados de outras redes vêm de fontes secundárias ou de testnets, não de mainnet.

Números de testnet não refletem condições reais de congestionamento, porque a testnet tem tráfego menor e custo subsidiado. Qualquer dado coletado nesse ambiente precisa ser identificado como tal na tabela comparativa, separado dos dados de mainnet obtidos de fontes secundárias.

---

## 7. Referências

Masama, M. A.; Kannengießer, N.; Sunyaev, A. *From Concept to Measurement: A Survey of How the Blockchain Trilemma Is Analyzed*. arXiv:2505.03768, 2025.

*Transaction Costs and Speed in the Ethereum Ecosystem: Scalability of the Mainnet and Layer 2s*. arXiv:2606.22206, 2026.

*An Empirical Smart Contracts Latency Analysis on Ethereum Blockchain for Trustworthy Inter-Provider Agreements*. arXiv:2503.01397, 2025.

*Why Does My Transaction Fail? A First Look at Failed Transactions on the Solana Blockchain*. arXiv:2504.18055, 2025.

Quattrocchi, G.; Scaramuzza, F.; Tamburri, D. A. *The blockchain trilemma: an evaluation framework*. IEEE Software, v. 41, n. 6, p. 101-110, 2024.

Gräbe, F.; Kannengießer, N.; Lins, S.; Sunyaev, A. *Do not be fooled: Toward a holistic comparison of distributed ledger technology designs*. HICSS 53, 2020.
