# Matriz de Critérios para Benchmark de Redes Blockchain (Versão 3.0 Homologada)
**Projeto:** Protocolo de Concessão de Crédito Interfinanceiro (Mockchain — Banco Inter)  
**Trilha:** Pesquisa Acadêmica  
**Data:** 20/09/2026  
**Status:** Versão 3.0 (Consolidada e Homologada por Meta-Auditoria Técnica e Financeira)

---

## 1. Estrutura Metodológica de Seleção (Modelo em Duas Etapas)

A seleção da infraestrutura blockchain para o Banco Inter utiliza uma abordagem em **duas etapas** fundamentada na literatura de Tomada de Decisão Multicritério (MCDM):

1. **Etapa 1 — Filtros Eliminatórios de Entrada (*Gating Criteria / Hard Constraints*):** Critérios mandatórios de elegibilidade técnica e regulatória. Redes que não cumprem estes requisitos são descartadas preliminarmente antes da ponderação.
2. **Etapa 2 — Matriz Ponderada de Decisão (*AHP / Soft Constraints*):** 5 critérios estritamente ortogonais (independentes), totalizando 100% dos pesos, avaliados nas redes aprovadas na Etapa 1.

> [!NOTE] **Distinção de Escopo: Ambiente da PoC (Sepolia) vs. Rede-Alvo de Produção**  
> A utilização da rede *Ethereum Sepolia* atende estritamente ao requisito **RNF01** (*Doc 1, p. 4*) como ambiente acadêmico de homologação da Prova de Conceito (PoC). O presente benchmark avalia, pontua e recomenda a infraestrutura corporativa definitiva para operação real do Banco Inter (ex.: rede permissionada em consórcio compatível com o Drex / Hyperledger Besu ou Rollup Institucional auditado).

### Fundamentação Científica da Quantidade de Critérios (5 Critérios na Matriz)
* **Capacidade Cognitiva:** [Miller, G. A. (1956)](https://doi.org/10.1037/h0043158) demonstra que a mente humana processa com consistência no máximo $7 \pm 2$ variáveis simultâneas.
* **Consistência Matemática do AHP:** [Saaty, T. L. (2008)](https://doi.org/10.1504/IJSSCI.2008.017590) prova que o número de julgamentos par a par necessários é:
  $$\text{Comparações} = \frac{n(n-1)}{2}$$
  Para $n = 5$ critérios, realizam-se exatamente **10 comparações**. Isso garante a manutenção da Razão de Consistência ($CR < 0{,}10$).

---

## 2. Etapa 1: Filtros Eliminatórios de Entrada (*Gating Criteria*)

As redes candidatas devem atender a ambos os requisitos para ingressar na lista fechada de 3 a 5 redes da Semana 1 (*Doc 2, p. 2*):

### Filtro A: Governança Identificada e Auditável (Anti-Anonimato Irrestrito)
* **Condição de Corte:** A rede deve possuir validadores identificáveis, consórcio auditável ou governança institucional compatível com normas de Prevenção à Lavagem de Dinheiro (PLD/AML).
* **Fontes Oficiais:** [CPMI-IOSCO (2012) — Princípio 2 (Governança)](https://www.bis.org/cpmi/publ/d101a.pdf); [Banco Central do Brasil — Diretrizes do Piloto Drex](https://www.bcb.gov.br/estabilidadefinanceira/drex).
* **Racional de Negócio:** Nenhuma tesouraria bancária regulada pelo Banco Central pode liquidar operações de crédito interbancário em redes cujo consenso dependa de validadores 100% anônimos ou imunes a jurisdição legal executável.

### Filtro B: Compatibilidade com a Stack do Projeto (EVM Equivalent / Compatible)
* **Condição de Corte:** Suporte nativo à execução de bytecode da Ethereum Virtual Machine (EVM) e ao ferramental Foundry/Solidity.
* **Fontes Oficiais:** Requisito de Projeto: *Doc 1, p. 4* (*"Stack Tecnológica: Smart Contracts: Solidity, Foundry"*); [ISO/IEC 25010 (Portabilidade e Modularidade)](https://www.iso.org/standard/78176.html).
* **Racional de Engenharia:** O projeto possui um ciclo estrito de 5 semanas (*Doc 1, p. 5*). Tratar a compatibilidade EVM como filtro prévio (e não como critério de nota na matriz) elimina o viés de pontuação circular e assegura que os contratos inteligentes desenvolvidos pela trilha Web3 não precisem ser reescritos em linguagens incompatíveis (como Rust, Move ou Wasm).

---

## 3. Etapa 2: Matriz Ponderada com Pesos e Justificativas

A tabela abaixo sintetiza a distribuição de pesos calibrada para o perfil de tesouraria de atacado bancário:

| ID | Critério Ortogonal | Peso | Justificativa do Peso (Racional de Tesouraria) |
| :---: | :--- | :---: | :--- |
| **C1** | **Suporte Nativo a DvP (Delivery vs. Payment)** | **25%** | **Cerne Funcional do Projeto:** É a dor prioritária da tesouraria (*RF03* e *Doc 1, p. 2-3*). A eliminação do risco de contraparte exige atomicidade estrita em transação única. |
| **C2** | **Isolamento de Privacidade Institucional** | **25%** | **Viabilidade Regulatória Obrigatória:** Sem garantia de sigilo de dados bancários (taxas, volumes e limites de crédito), a solução não pode operar em ambiente produtivo financeiro. |
| **C3** | **Latência e Determinismo de Finalidade** | **20%** | **Eficiência Operacional no Fechamento de Caixa:** O *RNF02* exige confirmação em $\le 30$ segundos. Finalidade determinística é essencial para evitar o risco de reversão (*reorg*). |
| **C4** | **Previsibilidade e Custo de Taxas (*Gas*)** | **15%** | **Previsibilidade Orçamentária:** Em operações de atacado (tíquetes de dezenas a centenas de milhões de reais), o peso foca na previsibilidade orçamentária e blindagem contra picos voláteis de mempools abertos. |
| **C5** | **Resiliência e Taxa de Sucesso sob Concorrência** | **15%** | **Estabilidade na Mesa de Operações:** A rede deve sustentar rajadas concorrentes de ordens no fechamento diário sem falhas de estado ou reversões anômalas (*Doc 2, p. 5*). |
| **Total** | | **100%** | **Soma dos pesos ponderados.** |

---

### Detalhamento dos Critérios

#### Critério 1: Suporte Nativo a DvP (Delivery versus Payment) — **Peso: 25%**
* **Fontes Primárias com Links Diretos:**
  * [CPMI-IOSCO (2012) PFMI — Princípio 12 (*Exchange-of-value settlement systems*, p. 77-80)](https://www.bis.org/cpmi/publ/d101a.pdf)
  * Requisito de Projeto: *RF03 — Liquidação atômica (DvP)* (*Doc 1, p. 4*)
* **Justificativa do Critério e Peso:**
  O documento do projeto declara que a concessão de crédito sofre com atrasos que geram risco de contraparte (*Doc 1, p. 2*). O Princípio 12 do BIS exige a liquidação atômica vinculada. Sendo o objetivo central do sistema (*"transferência do token representando o crédito e a liquidação do ativo ocorrem simultaneamente"*, *RF03*), este critério recebe o peso máximo de 25%.
* **Como será medido:**
  * **Nota 5:** Suporte nativo a composabilidade atômica síncrona (reversão integral no mesmo bloco).
  * **Nota 3:** Atomicidade dependente de orquestração externa em duas fases (*Two-Phase Commit* / travas de custódia).
  * **Nota 1:** Comunicação estritamente assíncrona que não garante reversão atômica em transação única.

---

#### Critério 2: Isolamento de Privacidade Institucional e Conformidade Regulatória — **Peso: 25%**
* **Fontes Primárias com Links Diretos:**
  * [Brasil — Lei Complementar nº 105/2001 (Sigilo das Operações Financeiras)](https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp105.htm)
  * [Banco Central do Brasil — Diretrizes e Relatórios do Piloto Drex](https://www.bcb.gov.br/estabilidadefinanceira/drex)
  * Requisito de Projeto: *Doc 1, p. 3* (*"privacidade de dados institucionais"*) e *Doc 2, p. 2* (*"Aula: privacidade"*)
* **Justificativa do Critério e Peso:**
  No mercado interbancário, a exposição pública de limites de crédito e volumes operados viola o Art. 1º da LC 105/2001 e expõe estratégias da tesouraria do Banco Inter a bancos concorrentes. A experiência do Bacen no Drex confirma que privacidade é o pré-requisito regulatório número um. Recebe peso de 25%.
* **Como será medido:**
  * **Nota 5:** Suporte nativo a transações confidenciais, canais privados de consórcio ou Provas de Conhecimento Zero (ZKPs).
  * **Nota 3:** Pseudonimato público mitigado exclusivamente por off-chain hashing na camada Web2 (dados sensíveis no PostgreSQL e apenas hashes/assinaturas on-chain).
  * **Nota 1:** Transparência integral e aberta de valores e contrapartes em mempool e ledger públicos.

---

#### Critério 3: Latência e Determinismo de Finalidade Arquitetural (*Settlement Finality*) — **Peso: 20%**
* **Fontes Primárias com Links Diretos:**
  * [CPMI-IOSCO (2012) PFMI — Princípio 8 (*Settlement Finality*, p. 64-67)](https://www.bis.org/cpmi/publ/d101a.pdf)
  * [CPMI (2017) DLT Analytical Framework — BIS Paper No. 157 (p. 12-14)](https://www.bis.org/cpmi/publ/d157.pdf)
  * Requisito de Projeto: *RNF02 — Desempenho* (*Doc 1, p. 4*)
* **Justificativa do Critério e Peso:**
  O *RNF02* impõe confirmação visível na interface em até 30 segundos. Para a tesouraria, a finalidade deve ser determinística para afastar o risco de reorganização de cadeia (*reorg*). Recebe peso de 20%.
* **Como será medido:**
  * **Nota 5:** Finalidade determinística imediata ($\le 3$ segundos, ex.: consenso BFT com 1 bloco).
  * **Nota 3:** Finalidade determinística entre $4$ e $30$ segundos (em conformidade com o *RNF02*).
  * **Nota 1:** Finalidade probabilística exigindo $> 30$ segundos para segurança estatística contra *reorgs*.

---

#### Critério 4: Previsibilidade e Eficiência Econômica de Taxas (*Gas Economy*) — **Peso: 15%**
* **Fontes Primárias com Links Diretos:**
  * [Farshidi, S., Jansen, S., España, S., & Verkleij, J. (2020) — IEEE TEM (DOI: 10.1109/TEM.2019.2956897)](https://doi.org/10.1109/TEM.2019.2956897)
  * Requisito de Projeto: *Doc 2, p. 2* (*"Bibliografia inicial: documentação, whitepaper e custo"*) e *Doc 2, p. 5* (*"Custo de gas por função"*)
* **Justificativa do Critério e Peso:**
  Em operações de atacado interbancário (onde os lotes transacionados giram em torno de R$ 10 mi a R$ 500 mi), o valor absoluto de frações de centavos de dólar é secundário. O risco crítico avaliado por este critério é a **volatilidade e imprevisibilidade de taxas** decorrentes de picos de congestionamento em mempools abertos, favorecendo redes de consórcio (*gas-free* ou custo fixo). Recebe peso de 15%.
* **Como será medido:**
  * **Nota 5:** Modelo *gas-free* institucional ou com custo previsível e subsidiável em rede privada/consórcio.
  * **Nota 3:** Custo por transação baixo ($< \$0{,}05$), porém sujeito à variabilidade de demanda da L1 (típico de Layer 2 rollups).
  * **Nota 1:** Taxas elevadas e altamente voláteis sujeitas a leilão dinâmico em mempool aberto ($> \$1{,}00$ por chamada).

---

#### Critério 5: Resiliência Operacional e Taxa de Sucesso sob Concorrência — **Peso: 15%**
* **Fontes Primárias com Links Diretos:**
  * [Hyperledger Caliper — Blockchain Performance Metrics (Linux Foundation)](https://hyperledger-caliper.github.io/caliper/)
  * [Casino, F., Dasaklis, T. K., & Patsakis, C. (2019) — Telematics and Informatics (DOI: 10.1016/j.tele.2018.11.006)](https://doi.org/10.1016/j.tele.2018.11.006)
  * Requisito de Projeto: *Doc 2, p. 5* (*"Dados do teste empírico: latência e taxa de sucesso"*)
* **Justificativa do Critério e Peso:**
  A mesa de operações precisa de garantias de que ordens simultâneas não sofrerão reversões anômalas ou falhas de nonce no fechamento diário do caixa. Recebe peso de 15%, avaliando empiricamente a robustez sob estresse concorrente na Semana 4.
* **Como será medido:**
  * **Nota 5:** Taxa de sucesso $\ge 99{,}9\%$ sob testes concorrentes sem conflitos de estado.
  * **Nota 3:** Taxa de sucesso entre $95{,}0\%$ e $99{,}8\%$ (falhas transitórias sanadas via retentativas assíncronas).
  * **Nota 1:** Taxa de sucesso $< 95{,}0\%$ sob carga concorrente.

---

## 4. Análise de Sensibilidade: "O Efeito de Outros Pesos"

O *Doc 2 (p. 4)* exige o relatório *"Recomendação de rede: Uma página com a escolha e o efeito de outros pesos"*. Para cumprir este requisito, a matriz modela **quatro cenários de simulação**:

| Cenário de Simulação | DvP (C1) | Privacidade (C2) | Finalidade (C3) | Custo (C4) | Resiliência (C5) | Hipótese de Impacto na Escolha da Rede |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **1. Cenário Base (Institucional)** | **25%** | **25%** | **20%** | **15%** | **15%** | Equilibra conformidade regulatória e desempenho operacional nominal. |
| **2. Regulatório Rigoroso (Drex)** | 20% | **40%** | 15% | 10% | 15% | Prioriza sigilo bancário; favorece consórcio privado permissionado (Besu). |
| **3. Otimização Econômica (Throughput)**| 20% | 15% | 20% | **30%** | 15% | Prioriza custo marginal e velocidade; favorece L2 Rollups (Arbitrum, Base). |
| **4. Estresse de Fechamento (Peak SPB/STR)**| 20% | 15% | **35%** | **5%** | **25%** | **Horário Crítico (18h30):** Custo torna-se irrelevante frente ao risco de multa de redesconto do Bacen; exige finalidade instantânea e tolerância zero a falhas. |

---

## 5. Critérios que NÃO Devem Ser Incluídos (com Justificativa e Links)

1. **Descentralização Extrema / Contagem Irrestrita de Nós Anônimos:**
   * *Justificativa:* Conflita com a governança financeira mandatória para câmaras institucionais.
   * *Link Oficial:* [CPMI-IOSCO PFMI Princípio 2 (Governança)](https://www.bis.org/cpmi/publ/d101a.pdf).
2. **Capitalização de Mercado e Volume Especulativo do Criptoativo de Varejo:**
   * *Justificativa:* O projeto veda movimentação de ativos reais (*Doc 1, p. 5*). Cotação de tokens de varejo não reflete eficiência técnica de conciliação bancária.
   * *Link Oficial:* [Farshidi et al. (2020) — IEEE TEM](https://doi.org/10.1109/TEM.2019.2956897).
3. **Diversidade de Linguagens de Programação Não-EVM:**
   * *Justificativa:* A stack está contratualmente fixada em Solidity/Foundry (*Doc 1, p. 4*). Avaliar outras linguagens distorceria a matriz e violaria o prazo de 5 semanas.
   * *Link Oficial:* [ISO/IEC 25010 (Portabilidade)](https://www.iso.org/standard/78176.html).

---

## 6. Critérios que PODERIAM Ser Incluídos (Roadmap de Produção)

1. **Suporte a Verificação Formal (*Formal Verification*):**
   * *Racional:* Prova matemática de invariantes de código. Essencial para tesouraria bancária em produção, mas postergado para a Fase 2 em virtude do ciclo de 5 semanas da PoC.
   * *Link Oficial:* [Casino et al. (2019) — Telematics and Informatics](https://doi.org/10.1016/j.tele.2018.11.006).
2. **Interoperabilidade Nativa Cross-Chain:**
   * *Racional:* Comunicação com a rede do Drex (Bacen). Postergado porque o *Doc 1 (p. 5)* veda liquidação externa nesta PoC.
   * *Link Oficial:* [CPMI (2017) DLT Analytical Framework (p. 18)](https://www.bis.org/cpmi/publ/d157.pdf).
3. **Eficiência Energética e Pegada Ecológica (ESG):**
   * *Racional:* Todas as candidatas elegíveis (PoS, L2s e consórcios BFT) já operam com consumo elétrico insignificante, conferindo variância zero na avaliação comparativa.
   * *Links Oficiais:* [Platt et al. (2021) — Energy Footprint of DLT](https://doi.org/10.1109/ACCESS.2021.3129849); [Erol et al. (2023) — Techn. Forecast. Soc. Change (DOI: 10.1016/j.techfore.2022.122132)](https://doi.org/10.1016/j.techfore.2022.122132).
