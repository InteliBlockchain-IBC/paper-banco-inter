# Matriz de critérios e base do paper

**Projeto:** Protocolo de concessão de crédito interfinanceiro (Mockchain)
**Trilha:** Pesquisa Acadêmica
**Atualizado em:** 16/10/2026
**Função deste arquivo:** fonte única das decisões da pesquisa. Quando algo for decidido ou mudar, atualize este arquivo primeiro e depois o paper.

---

## 0. Como usar este arquivo

- Ele resume **o que está decidido** e **o que falta** para terminar o paper.
- Os detalhes de medição (testes, planilhas, falhas) estão em `pesquisa/2-metodo/roteiro-medicao.md`.
- Os números medidos, o ranking atual e a sensibilidade estão em `pesquisa/3-resultados/resultados.md`, gerado pelos scripts de `benchmark/`.
- As pesquisas exploratórias de setembro, que levaram à lista de redes, estão em `pesquisa/1-redes-candidatas/`.
- O texto do artigo está em `paper/template_cotb2027.tex`.
- Cada afirmação técnica aponta uma fonte entre colchetes, como [R3]. Os links estão na seção 15.
- Ao mudar algo: atualizar a data no topo e registrar a mudança na seção 14 (Histórico).

| Marcação | Significado |
|---|---|
| **[DECIDIDO]** | Aprovado pela equipe |
| **[PROPOSTA]** | Sugerido no roteiro de medição, aguardando aprovação (seção 11.2) |
| **[CONFERIR]** | Depende de informação que ainda não chegou (Canton, Monad ou contagem da INTER-15) |
| **[VERIFICAR]** | Precisa de fonte antes da versão final do paper |
| **[A REGISTRAR]** | Decisão tomada, mas o motivo ainda não foi escrito |

---

## 1. Pergunta de pesquisa e tipo de estudo [DECIDIDO]

**Questão de pesquisa (QP), igual à do paper:**

> Qual rede blockchain é mais adequada para executar um protocolo de concessão de crédito interfinanceiro overnight com liquidação por entrega contra pagamento (DvP)?

| Item | Escolha | O que significa |
|---|---|---|
| Tipo de pesquisa | Aplicada | Responde a uma pergunta prática |
| Abordagem | Decisão multicritério (MCDM), com conjunto finito de alternativas (MADM) | Comparar uma lista fechada de opções segundo vários critérios que podem entrar em conflito. Já usada para escolher plataformas blockchain [R1, R2] |
| Pesos | AHP (*Analytic Hierarchy Process*) | Os pesos saem de comparações entre pares de critérios [R3] |
| Agregação | Soma ponderada (WSM, *Weighted Sum Model*) | Pontuação da rede = soma de (peso × nota normalizada) |
| Normalização | Min-max [PROPOSTA] | Converte unidades diferentes (segundos, dólares, %) para notas de 0 a 1 |
| Validação | Razão de consistência, análise de sensibilidade e lista de alternativas fechada antes do cálculo | [R3, R5, R6] |
| Dados | Declarados (documentação oficial e literatura) e medidos (experimentos nas testnets) | Mesma combinação usada por Six et al. [R8] |

---

## 2. O protocolo avaliado (o que o código faz)

Fonte: repositório do time de Web3, commit `3347bf2`, de 12/10/2026 [R31].

### 2.1 Contratos

| Contrato | Padrão | Papel na operação |
|---|---|---|
| `CreditInterbankOffer` | Contrato principal | Ofertas, limites de crédito e liquidação DvP |
| `BRLToken` (BRLt) | ERC-20, 2 casas decimais | Real tokenizado fictício. É a **perna financeira** |
| `CDIPositionToken` (CDIP) | ERC-721 (NFT) | Posição de crédito do ofertante. É a **perna do ativo**. O número do NFT é igual ao número da oferta |

### 2.2 Fluxo

1. O admin (que simula o Banco Central) cadastra as instituições e define o limite de crédito de cada tomador.
2. O ofertante autoriza o contrato a mover seu BRLt (`approve`) [R29].
3. O ofertante cria a oferta, dirigida a um tomador específico (`createOffer`). O contrato recusa se o limite do tomador for menor que o valor.
4. O tomador aceita (`acceptOffer`). Na mesma transação, o contrato consome o limite do tomador, transfere o BRLt do ofertante para o tomador e emite o NFT de posição para o ofertante. Se uma parte falhar, tudo é desfeito.
5. O contrato publica os eventos `OfferAccepted` e `OfferSettled`, que o backend lê.
6. Antes do aceite, o ofertante pode cancelar (`cancelOffer`).

| Requisito do TAP | Onde aparece no código |
|---|---|
| RF01 Oferta | `createOffer` |
| RF02 Validação de limite | `createOffer` e `acceptOffer` |
| RF03 DvP atômico | `acceptOffer` |
| RF06 Cancelamento | `cancelOffer` |
| RNF03 Registro | Evento `OfferSettled` (partes, valor, taxa, horário) mais o hash da transação |

### 2.3 Situação na Sepolia

- Implantado e verificado em 05/10/2026 [R31].
- Primeira operação liquidada em 06/10/2026. Gas usado: `approve` 46.361; `createOffer` 237.009; `acceptOffer` 172.050; ciclo completo 455.420 [R32].

### 2.4 Cuidados de redação no paper

- **Documentos antigos** dizem que o token do CDI é ERC-20. No código, a posição de crédito é um NFT (ERC-721); o ERC-20 é o BRLt.
- **Condição de elegibilidade (seção 3.2 do .tex):** o texto fala em "transferência do token que representa o crédito". No código, a perna do ativo é a **emissão** do NFT para o ofertante, e não uma transferência. A redação deve refletir isso.

---

## 3. Alternativas: as cinco redes [DECIDIDO]

A lista está **fechada**. Incluir ou retirar uma rede depois do cálculo pode inverter a ordem das demais, efeito mostrado por Belton e Gear [R6]. Qualquer mudança na lista exige refazer a análise inteira.

| Rede | Acesso no estudo | Compatível com EVM | Ambiente de teste | Finalidade (declarada) | Fontes |
|---|---|---|---|---|---|
| Ethereum | Pública | Sim (rede de origem da EVM); implantada sem alteração na Sepolia em 16/10/2026 | Testnet Sepolia, com o Glamsterdam ativo desde 06/10/2026 [R41] | Cerca de 16 min após a inclusão no bloco [VERIFICAR título e autoria da nota] | [R23, R41] |
| Avalanche (C-Chain) | Pública | Sim; implantada sem alteração na Fuji em 16/10/2026 | Testnet Fuji | Probabilística, menos de 1 s | [R17, R24] |
| Monad | Pública | Sim; implantada sem alteração na testnet em 16/10/2026 | Testnet pública, chain ID 10143 [R35] | Declara 600 ms (2 slots), com bloco mínimo de 300 ms; consulta de 14/10/2026 [R36]. Versões anteriores da documentação diziam 800 ms e 400 ms | [R25, R36] |
| Hyperledger Besu | Privada (permissionada), montada pela equipe | Sim; implantada sem alteração em 14/10/2026 (Besu 26.8.1) | Rede local QBFT com 4 validadores, período de bloco de 2 s, gas grátis [R34] | Imediata | [R26] |
| Canton | Permissionada: DevNet e TestNet exigem patrocínio de um Super Validator [CONFERIR na INTER-17] | Não; contrato reescrito em Daml (5 testes de Daml Script passando) | Sandbox local do SDK oficial (`dpm sandbox`, Canton 3.6.1): participante, sequencer e mediator num só processo [R42]. O LocalNet do `cn-quickstart` [R39] exigiria Nix e conta no Docker Hub | Determinística após a confirmação; no sandbox, 0,37 s até a resposta do commit (medido) | [R28, R39, R42] |

**Redes que saíram da lista:** Solana e Stellar (candidatas iniciais) e Miden (sugerida pelo parceiro). [A REGISTRAR: o motivo de cada descarte. Se o paper citar essas redes, o motivo precisa estar escrito.]

---

## 4. Condição de elegibilidade: liquidação atômica [DECIDIDO]

- **DvP** (entrega contra pagamento): o ativo só é entregue se o pagamento acontecer. Sem esse vínculo existe o **risco de principal**, que é perder o valor inteiro da operação porque uma parte entregou e a outra não [R9].
- Os princípios internacionais para infraestruturas do mercado financeiro exigem que a liquidação de uma obrigação dependa da liquidação da outra (Princípio 12) [R10].
- Em blockchain, isso se faz com **liquidação atômica**: um contrato liga as duas transferências, e uma só acontece se a outra também acontecer [R11].

**Por que não é critério:** todas as redes da lista executam transações de forma atômica (tudo ou nada). Um critério em que todas as redes recebem a mesma nota soma o mesmo valor a todas e não muda o ranking, qualquer que seja o peso. Por isso a atomicidade é uma **exigência para entrar na lista**, e não um critério pontuado. Baninemeh et al. tratam requisitos obrigatórios da mesma forma [R2].

[VERIFICAR: citar, para cada rede, a documentação oficial que confirma a atomicidade das transações.]

---

## 5. Critérios [DECIDIDO]

| Critério | Peso | O que mede | Unidade | Sentido | Origem do dado | Medidas |
|---|---|---|---|---|---|---|
| C1. Resiliência (taxa de sucesso sob carga) | 29,78% | Proporção de transações confirmadas sob carga declarada | % | Benefício | Medido | Única |
| C2. Segurança do contrato | 29,78% | Proteção do contrato e dos dados da operação | Nota composta | Benefício | Declarado e medido | M1 verificação formal (declarado); M2 complexidade do código (medido); M3 confidencialidade (declarado) |
| C3. Latência | 15,78% | Tempo entre o envio da transação e sua inclusão em bloco | Segundos | Custo | Medido | Única |
| C4. Custo | 15,78% | Quanto custa operar o protocolo | Moeda comum, com data da cotação | Custo | Medido e declarado | M1 taxa por transação (medido); M2 custo de infraestrutura (declarado) |
| C5. Compatibilidade EVM | 8,88% | Esforço para levar o contrato em Solidity para a rede | Três níveis | Benefício | Declarado, confirmado na implantação | Única |

**Benefício** = quanto maior, melhor. **Custo** = quanto menor, melhor.

**Base de cada critério:**

| Critério | Fundamentação | Fontes |
|---|---|---|
| C1 | Uma transação que falha é uma operação de crédito não concluída. O desempenho depende das condições de carga, e as métricas do Hyperledger tratam das transações que falham | [R17, R18] |
| C2 | A ISO/IEC 25010 define segurança e inclui confidencialidade e integridade. Verificação formal é demandada em contratos financeiros. Complexidade se associa a vulnerabilidades | [R12, R13, R14, R15, R16] |
| C3 | RNF02 (confirmação visível em até 30 s). Latência = confirmação menos submissão. A latência cresce com envios simultâneos | [R18, R19] |
| C4 | Cada rede cobra de um jeito; o total pago é a base de comparação mais robusta. Sem o custo de infraestrutura, redes sem taxa seriam favorecidas | [R20, R21, R22] |
| C5 | O protocolo é em Solidity. Reescrever em outra linguagem pode mudar a própria implementação avaliada | [R17, R20] |

**Definição de "confirmação" (RNF02) [DECIDIDO]:** inclusão da transação em um bloco. A janela de 30 s cobre a inclusão, a leitura do evento pelo backend e a atualização da tela.

---

## 6. Pesos pelo AHP [DECIDIDO]

### 6.1 Quantidade de critérios

São cinco. Saaty e Özdemir mostram que um grupo comparado aos pares não deve passar de sete elementos, porque em grupos maiores fica difícil achar qual julgamento está errado [R4]. O número de comparações é n(n − 1)/2 = 10 para n = 5.

### 6.2 Níveis e regra de conversão

| Nível | Critérios |
|---|---|
| Alto | C1, C2 |
| Médio | C3, C4 |
| Baixo | C5 |

| Comparação | Nota na escala de Saaty |
|---|---|
| Mesmo nível | 1 |
| Alto em relação a médio | 2 |
| Médio em relação a baixo | 2 |
| Alto em relação a baixo | 3 |

A comparação inversa recebe o valor recíproco (por exemplo, médio em relação a alto = 1/2).

### 6.3 Matriz de comparações

Cada célula diz quanto o critério da linha é mais importante que o da coluna.

| | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|
| **C1** | 1 | 1 | 2 | 2 | 3 |
| **C2** | 1 | 1 | 2 | 2 | 3 |
| **C3** | 1/2 | 1/2 | 1 | 1 | 2 |
| **C4** | 1/2 | 1/2 | 1 | 1 | 2 |
| **C5** | 1/3 | 1/3 | 1/2 | 1/2 | 1 |

### 6.4 Resultado

| Critério | Peso |
|---|---|
| C1. Resiliência | 29,78% |
| C2. Segurança | 29,78% |
| C3. Latência | 15,78% |
| C4. Custo | 15,78% |
| C5. Compatibilidade EVM | 8,88% |
| **Total** | **100,00%** |

Os pesos são o autovetor principal da matriz, normalizado para somar 1.

**Consistência:** λmax = 5,0133; CI = (λmax − n)/(n − 1) = 0,0033; RI = 1,12 (para n = 5); CR = CI/RI = 0,0030. Limite aceito: CR ≤ 0,10 [R3]. Valores recalculados em 14/10/2026 e conferidos com o paper.

[VERIFICAR: citar a fonte original do RI = 1,12 e do limite de 0,10.]

**Observações:**

- O CR é baixo em parte porque os julgamentos saíram de uma regra por níveis, e não de comparações feitas uma a uma. Isso vai para Ameaças à Validade.
- Se cada integrante fizer as próprias comparações, as matrizes devem ser combinadas pela média geométrica [R7].

---

## 7. Do dado bruto à pontuação final

### 7.1 Normalização [PROPOSTA]

```
Benefício:  r = (x − mín) ÷ (máx − mín)
Custo:      r = (máx − x) ÷ (máx − mín)
Empate (máx = mín): todas as redes recebem r = 1
```

### 7.2 Escalas dos dados declarados [PROPOSTA, exceto a definição de "sem alteração" em C5, DECIDIDO]

**C5. Compatibilidade EVM**

| Nível | Nota | Significado |
|---|---|---|
| Sem alteração | 1,0 | Mesmo código (mesmo commit) e mesma configuração de compilação (Solidity 0.8.24, otimizador com 200 execuções). Arquivo de configuração de implantação e endereço de RPC novos não contam como alteração [DECIDIDO] |
| Compilador modificado | 0,5 | Exige outra versão ou configuração de compilação, ou mudanças no código |
| Reescrita | 0,0 | Exige reescrever o contrato em outra linguagem |

**C2-M1. Verificação formal**

| Nível | Nota | Significado |
|---|---|---|
| Alto | 1,0 | Ferramenta com documentação oficial ou publicação revisada por pares, e manutenção ativa |
| Médio | 0,5 | Ferramenta experimental, sem manutenção ativa ou limitada a uma função |
| Baixo | 0,0 | Nenhuma ferramenta |

**C2-M3. Confidencialidade**

| Nível | Nota | Significado |
|---|---|---|
| Alto | 1,0 | Cada participante vê só as transações de que faz parte |
| Médio | 0,5 | Rede permissionada, mas todos os participantes veem tudo |
| Baixo | 0,0 | Rede pública: qualquer pessoa vê tudo |

Evidência para a Sepolia: o guia de integração do time de Web3 registra que qualquer pessoa lê os eventos e que esconder as ofertas é feito só na aplicação [R31].

**Notas atribuídas nessas escalas [PROPOSTA, conferir nas INTER-16 e INTER-17]:**

| Medida | Ethereum | Avalanche | Monad | Besu | Canton | Fonte |
|---|---|---|---|---|---|---|
| C2-M1 Verificação formal | 1,0 | 1,0 | 1,0 | 1,0 | 0,5 | Solidity: SMTChecker faz parte do compilador oficial [R37]. Daml: `daml-lf-verify` é experimental, não lançado e só verifica a conservação de um campo [R38] |
| C2-M3 Confidencialidade | 0,0 | 0,0 | 0,0 | 0,5 | 1,0 | Pública nas três primeiras; Besu permissionada com todos vendo tudo; Canton com privacidade por subtransação [R28] |
| C5 Compatibilidade EVM | 1,0 (confirmado em 16/10) | 1,0 (confirmado em 16/10) | 1,0 (confirmado em 16/10) | 1,0 (confirmado em 14/10) | 0,0 | Implantações do experimento [R34] |

### 7.3 Notas dentro de C2 e C4 [PROPOSTA]

```
C2 = (C2-M1 + C2-M2 + C2-M3) ÷ 3
C4 = (C4-M1 + C4-M2) ÷ 2
```

Consequência para o texto: com média simples, cada medida de C2 pesa 9,93% na pontuação final (29,78% ÷ 3), e cada medida de C4 pesa 7,89% (15,78% ÷ 2). Dar pesos internos pelo AHP foi descartado por causa do prazo.

### 7.4 Pontuação final

```
P(Aᵢ) = Σ wⱼ × rᵢⱼ
```

- wⱼ = peso do critério j (seção 6.4)
- rᵢⱼ = nota normalizada da rede i no critério j
- A rede com maior P ocupa o primeiro lugar.

[VERIFICAR: referência revisada por pares para o WSM.]

---

## 8. Coleta de dados (resumo do roteiro de medição)

Detalhes completos em `pesquisa/2-metodo/roteiro-medicao.md` (v2).

| Tema | Decisão | Status | Seção do roteiro |
|---|---|---|---|
| Ciclo medido | `approve` (valor exato) + `createOffer` + `acceptOffer` | [DECIDIDO A] | 2.2 |
| Ponto de partida | Implantação nova e mesma configuração em todas as redes; R$ 1,00 por oferta; validade de 24 h | [DECIDIDO B] | 4.1 |
| Código nas redes EVM | Sem alteração; só arquivo de configuração e RPC novos | [DECIDIDO D] | 4.1 |
| T1 (sem carga) | 30 ciclos e 10 cancelamentos por rede | [PROPOSTA] | 4.2 |
| T2 (carga) | Lotes de 10, 25 e 50 aceites simultâneos, 3 rodadas (255 aceites) | [PROPOSTA] | 4.3 |
| Falhas | Classificadas pelo nome do erro; só falhas da rede (categoria D) contam | [PROPOSTA] | 5 |
| Latência | Do envio real (depois da estimativa de gas) até o recibo; mediana do T1 entra na matriz | [PROPOSTA] | 3.2, 7 |
| Custo por transação (EVM) | Gas medido na testnet × preço do gas na mainnet × cotação do token | [PROPOSTA] | 3.3 |
| Custo na Monad | A Monad cobra o gas limit, e não o gas usado [R35]. O custo da Monad usa o limite enviado (estimativa × 1,2, igual em todas as redes) | [PROPOSTA] | 3.3 |
| Complexidade | Complexidade ciclomática do código da equipe em `src/`, sem OpenZeppelin; contam `if`, laços, ternário, `&&` e `\|\|`; não contam modificadores | Regra [DECIDIDO C]; métrica [PROPOSTA] | 3.4 |
| Contagem Solidity | 49 (24 funções e 25 pontos de decisão), igual à contagem manual; conferida por script em 14/10 [R34] | Conferida; falta o aceite da INTER-15 | 3.4 |
| Contagem Daml | 24 (9 funções e 15 pontos de decisão) na versão provisória do benchmark; contam `if`, `assert`, `assertMsg`, `ensure`, guardas, alternativas de `case`, `&&` e `\|\|` [R34] | [PROPOSTA]; refazer sobre o código da INTER-13 | 3.4 |
| Infraestrutura | Três participantes (duas instituições e o admin); 1 nó por participante nas redes públicas; 4 validadores no Besu | Participantes [DECIDIDO E]; nós [PROPOSTA] | 8.4 |

### 8.1 Dados coletados e origem de cada número

Scripts em `benchmark/`, dados brutos em `dados/` e gráficos em `pesquisa/3-resultados/graficos/` [R34]. Resultados completos e sempre atualizados em `pesquisa/3-resultados/resultados.md`.

Todo número do paper precisa dizer de onde veio. São quatro origens:

| Etiqueta | Origem | O que significa |
|---|---|---|
| `LOCAL` | Medido em rede local | A equipe rodou o contrato numa rede montada na própria máquina (Docker): Besu e, depois, o LocalNet da Canton. Mede o protocolo, mas sem tráfego de terceiros nem latência de internet |
| `TESTNET` | Medido em testnet | A equipe rodou o contrato na testnet pública: Sepolia, Fuji e Monad |
| `PROJEÇÃO` | Projeção, sem teste | Valor da documentação oficial, custo calculado com o gas medido na rede local, ou hipótese (100% de sucesso), usado no lugar da medição |
| `A MEDIR` | A medir | Sem teste e sem valor provisório; a pontuação aparece como faixa |

| Rede | Ambiente | Origem | T1: mediana do `acceptOffer` | T1: p95 e máximo | T1: até 30 s | T2: taxa de sucesso | Gas médio do ciclo | Custo do ciclo | Coletado em |
|---|---|---|---|---|---|---|---|---|---|
| Canton | Rede local (sandbox) | `LOCAL` | 0,37 s | 0,37 s e 0,38 s | 100% | 100% (255 de 255) | sem gas | Zero (sandbox sem taxa) | 16/10/2026 |
| Hyperledger Besu | Rede local (QBFT, 4 validadores) | `LOCAL` | 1,96 s | 2,06 s e 2,07 s | 100% | 100% (255 de 255) | 422.312 | Zero (gas grátis) | 14/10/2026 |
| Monad | Testnet pública | `TESTNET` | 0,99 s | 1,56 s e 1,74 s | 100% | 100% (255 de 255) | 602.935 (gas limit) | US$ 0,0014 | 16/10/2026 |
| Avalanche Fuji | Testnet pública | `TESTNET` | 2,64 s | 3,03 s e 3,13 s | 100% | 100% (255 de 255) | 429.924 | US$ 0,029 | 16/10/2026 |
| Ethereum Sepolia | Testnet pública | `TESTNET` | 11,04 s | 11,98 s e 22,02 s | 100% | 100% (255 de 255) | 1.502.836 | US$ 0,296 | 16/10/2026 |

Nenhuma rede teve falha de nenhuma categoria (A a D) no T1 nem no T2: 1.825 transações medidas, todas confirmadas. As testnets foram coletadas em paralelo entre 22:40 e 23:22 UTC de 16/10/2026, com RPC público gratuito; preços de referência são a mediana de 9 amostras nessa janela (Ethereum 0,081 gwei a US$ 2.422,04; Avalanche 6,77 gwei a US$ 9,97; Monad 103 gwei a US$ 0,0229).

**Resultado da matriz (pesos do cenário base):** Canton 86,2; Hyperledger Besu 82,8; Monad 79,2; Avalanche 75,2; Ethereum 48,6. O primeiro lugar muda em 4 dos 17 cenários de sensibilidade (pesos iguais; C2 −50%; C5 +50%; sem C2), sempre para o Besu ou para a Monad. Com C1 empatado em 100% em todas as redes, o critério de maior peso não diferencia ninguém neste estudo.

**Achados que entram no artigo:**

- **Sepolia pós-Glamsterdam.** A Sepolia ativou o Glamsterdam em 06/10/2026 [R41], um dia depois da implantação do time, e a criação de estado ficou mais cara. O ciclo gastou 1.502.836 de gas na Sepolia contra 422.312 pelas regras atuais da mainnet (medidas no Besu), 3,56 vezes mais. A premissa da seção 3.3 do roteiro (mesmo gas na testnet e na mainnet) não vale para a Ethereum neste estudo. A matriz usa o gas da Sepolia, como manda o roteiro; com o gas das regras atuais o custo cai para US$ 0,083 por ciclo, a Ethereum continua a mais cara e a ordem não muda.
- **Custo da Canton.** O sandbox não cobra por transação, e a matriz trata isso como o Besu com gas grátis (custo zero). A Canton é uma rede privada, de acesso restrito a instituições, então o custo real dela não é acessível e supor um valor seria antiético. **[DECIDIDO pela equipe]** Não estimar: Canton e Besu aparecem com asterisco por terem rodado em rede local, e o C4-M2 (levantado em `pesquisa/4-custo-infraestrutura/`) fica como informação descritiva, fora da pontuação. A alternativa com o custo "a definir" (faixa de 70,4 a 86,2, com o Besu em primeiro) continua registrada em `resultados.md` como análise de robustez.

O gas médio do ciclo no Besu (422.312) é menor que o da demonstração na Sepolia em 06/10 (455.420) porque a primeira oferta grava posições vazias do armazenamento [R30]; a média de 30 ciclos já reflete o estado comum.

---

## 9. Análise de sensibilidade [PROPOSTA]

Testa se o ranking se mantém quando os pesos mudam [R5].

| Cenário | O que muda | Quantidade |
|---|---|---|
| S1 | Pesos iguais (20% cada) | 1 |
| S2 | Cada peso +50% e −50%, um de cada vez, com renormalização | 10 |
| S3 | Retirar um critério de cada vez, com renormalização | 5 |
| | **Total** | **16** |

Reportar a posição de cada rede em cada cenário e se o primeiro lugar muda.

---

## 10. Ameaças à validade e limitações (insumo para a seção 5.2 do paper)

| # | Ameaça | Onde aparece |
|---|---|---|
| 1 | Os julgamentos do AHP vieram de uma regra por níveis; o CR baixo não indica julgamentos independentes | Seção 6.4 |
| 2 | Testnet não é mainnet: o tráfego é menor, e o preço do gas foi trocado pelo da mainnet sob a premissa de que o gas usado é igual | Roteiro 3.3 |
| 3 | A rede Besu é local e não compartilhada; as testnets públicas têm outros usuários. As condições de carga diferem | Roteiro 4.3 |
| 4 | A carga máxima é de 50 transações simultâneas; o resultado não mede a capacidade máxima da rede | Roteiro 4.3 |
| 5 | A latência mede só a inclusão no bloco. A janela do RNF02 também inclui backend e tela, e inclusão não é o mesmo que finalidade | Seção 5; roteiro 3.2 |
| 6 | C2-M2 tem só duas versões do código (Solidity e Daml), em linguagens diferentes; a soma cresce com o número de funções; a normalização vira "tudo ou nada" | Roteiro 3.4 e 8.1 |
| 7 | As medidas internas de C2 e C4 usam média simples, sem pesos próprios | Seção 7.3 |
| 8 | As escalas qualitativas (C5, C2-M1, C2-M3) foram definidas pela equipe | Seção 7.2 |
| 9 | A normalização min-max depende do conjunto de redes; por isso a lista foi fechada | Seção 3 |
| 10 | O custo de infraestrutura depende do cenário escolhido, de um único provedor de nuvem e da data da consulta | Roteiro 8.4 |
| 11 | Dados declarados pelas próprias redes (por exemplo, os números da Monad) não foram verificados por terceiros. Gramoli et al. apontam que esses números costumam não ser reproduzíveis | Seção 3; [R17] |
| 12 | Se Canton ou Monad ficarem sem ambiente de teste, parte dos dados será declarada, e não medida | Roteiro 10 |
| 13 | O estudo avalia um único protocolo; os resultados valem para este caso de uso | Geral |
| 14 | A latência do Besu reflete o período de bloco escolhido pela equipe (2 s); outro período mudaria C3 | Seção 8.1 |
| 15 | Na Monad o custo depende do gas limit que o cliente envia, e não só do trabalho executado | Seção 8 |
| 16 | A Canton roda numa só máquina, sem rede entre participantes; a latência medida (0,37 s) é um piso | Seção 3 |
| 17 | A versão Daml muda o desenho em dois pontos por causa da privacidade: o limite do tomador só é checado no aceite, e a posição é um contrato assinado pelas duas partes. Aceites simultâneos do mesmo tomador disputam o mesmo contrato de limite | Seção 8 |
| 18 | A Sepolia mudou de regras de gas durante o estudo (Glamsterdam, 06/10/2026); o gas medido nela não representa a mainnet atual | Seção 8.1 |
| 19 | A Canton foi medida no sandbox do SDK (um participante, sequencer e mediator no mesmo processo), não no LocalNet com vários validadores nem na rede real | Seções 3 e 8.1 |
| 20 | Todas as redes tiveram 100% de sucesso com até 50 aceites simultâneos; C1 não diferenciou as redes, e uma carga maior seria necessária para separá-las | Seção 8.1 |
| 21 | As três testnets foram coletadas em paralelo na mesma máquina, com RPC público; o Besu foi coletado dois dias antes | Seção 8.1 |

---

## 11. Decisões

### 11.1 Decididas

| Decisão | Data |
|---|---|
| Método MCDM (MADM), com AHP para os pesos e soma ponderada para a agregação | Até 14/10 |
| Cinco critérios, com níveis e pesos da seção 6 | Até 14/10 |
| Atomicidade como condição de elegibilidade, e não como critério | Até 14/10 |
| Confidencialidade como medida dentro de C2; infraestrutura como medida dentro de C4 | Até 14/10 |
| "Confirmação" do RNF02 = inclusão em bloco | Até 14/10 |
| Dinheiro representado por token; nenhum dinheiro real | Até 14/10 |
| Testes nas testnets das outras redes, inclusive a não EVM | Até 14/10 |
| Lista fechada: Ethereum, Avalanche, Monad, Besu e Canton | Até 14/10 |
| A. Um `approve` por ciclo, no valor exato; no T2, um único `approve` na preparação | 14/10 |
| B. Mesmo ponto de partida em todas as redes | 14/10 |
| C. Complexidade conta só o código exato da equipe | 14/10 |
| D. Definição de "sem alteração" em C5 | 14/10 |
| E. O admin entra no cenário de infraestrutura | 14/10 |

### 11.2 Aguardando aprovação (seção 13.2 do roteiro)

1. Tamanho do T1 e do T2
2. Custo das redes EVM com preço da mainnet
3. Classificação de falhas
4. Valores que entram na matriz (mediana, média do ciclo, taxa agregada)
5. Complexidade ciclomática como métrica de C2-M2
6. Escalas de C2-M1, C2-M3 e níveis 0,5 e 0,0 de C5
7. Média simples dentro de C2 e C4
8. Um nó por participante nas redes públicas
9. Cenários de sensibilidade

---

## 12. Estrutura do paper e responsáveis

Template do COTB 2027, trilha de artigo completo.

| Seção | Conteúdo | Tarefa (Linear) | No .tex em 14/10 |
|---|---|---|---|
| Título, abstract e keywords (em inglês) e título em português | Itens obrigatórios | INTER-23 (A7) | Vazio |
| 1. Introdução | Contexto, problema, QP, objetivo | INTER-19 (A5) | Vazio |
| 2. Fundamentação Teórica | DvP, liquidação atômica, MCDM, AHP | INTER-19 (A5) | Vazio |
| 2.1 Trabalhos Relacionados | Estudos de seleção de blockchain e benchmarks | INTER-27 (B9) | Vazio |
| 3.1 Definição do Problema e Método | QP, MCDM, normalização, WSM, sensibilidade | INTER-20 (A6) | Escrito, com pendências |
| 3.2 Modelo de Decisão | Alternativas, elegibilidade, critérios, pesos | INTER-20 (A6) e INTER-22 (B7, tabela de alternativas) | Escrito, com pendências |
| 3.3 Coleta de Dados | Dados declarados e medidos, experimentos | INTER-22 (B7) | Escrito, com pendências |
| 4. Resultados | Matriz de desempenho, ranking, sensibilidade | INTER-21 (B6) e INTER-22 (B7) | Depende dos dados |
| 5.1 Interpretação dos Resultados | | INTER-22 (B7) | Depende dos dados |
| 5.2 Ameaças à Validade e Limitações | Seção 10 deste arquivo | INTER-23 (A7) | Insumo pronto |
| 6. Conclusões e Trabalhos Futuros | | INTER-23 (A7) | Vazio |
| Agradecimentos e Declaração de Uso de IA | Obrigatórios | INTER-23 (A7) | Vazio |
| Revisão final | | INTER-25 (A8) e INTER-26 (B8) | Prevista para 16/10 |
| Resumo executivo (fora do paper) | | INTER-24 (C6) | Previsto para 16/10 |

### 12.1 Pendências marcadas no .tex

| Pendência | Seção do .tex | Como resolver |
|---|---|---|
| Confirmar o método de normalização | 3.1 | Aprovação do item 11.2; texto na seção 7.1 deste arquivo |
| Referência revisada por pares para o WSM | 3.1 | Buscar e citar |
| Cenários de sensibilidade | 3.1 | Aprovação do item 9; seção 9 deste arquivo |
| Tabela de alternativas | 3.2 | Seção 3 deste arquivo, depois de fechar os [CONFERIR] da Canton |
| Documentação de atomicidade de cada rede | 3.2 | Buscar e citar |
| Redação da elegibilidade ("transferência" do token de crédito) | 3.2 | Trocar para emissão do NFT (seção 2.4) |
| Parâmetros de C1 | 3.2 | Roteiro 4.3 |
| Escalas de M1 e M3, métrica de M2 e combinação de C2 | 3.2 | Seções 7.2 e 7.3; roteiro 3.4 |
| Repetições e estatísticas de C3 | 3.2 | Roteiro 4.2 e 7 |
| Exemplo do Hyperledger Fabric em C4 | 3.2 | Fabric não está na lista. Trocar pelo Besu sem cobrança de gas, que é a configuração usada no experimento [R40] |
| Combinação de M1 e M2 em C4 | 3.2 | Seção 7.3 |
| Nota de cada nível de C5 | 3.2 | Seção 7.2 |
| Fonte do RI e do limite de 0,10 | 3.2 | Buscar e citar |
| Parâmetros dos experimentos e cenário de infraestrutura | 3.3 | Roteiro 4 e 8.4 |
| Título e autoria da nota sobre finalidade do Ethereum | Referências | Conferir a fonte |
| Referências de exemplo do template (Haykin, Kalman e "exemplo_*") | Referências | Apagar antes de enviar; o template exige que toda referência listada seja citada |

---

## 13. Regras do template (COTB 2027)

- **Tamanho:** artigo completo com no máximo 6 páginas, **incluindo as referências**.
- **Idioma:** título, abstract (até cerca de 250 palavras) e keywords em inglês são obrigatórios. Como o texto é em português, o título também aparece em português.
- **Citações:** formato numérico da ACM, com `\cite{}`. Toda referência listada precisa ser citada, e toda citação precisa estar na lista.
- **Duas versões:** a de avaliação é anônima (sem autores, sem agradecimentos identificáveis, sem autocitações que revelem a autoria); a final é completa.
- **Declaração de Uso de IA:** obrigatória nas duas versões.
- **Envio:** só em PDF gerado pelo template.
- **Regras da equipe:** não alterar a formatação nem a estrutura do template; não identificar o banco parceiro no texto.
- **Datas do projeto:** entrega em 17/10/2026; demo day em 21/10/2026.

---

## 14. Histórico deste arquivo

| Data | Mudança |
|---|---|
| 14/10/2026 | Criado. Consolida o rascunho de metodologia, os pesos com cinco critérios, o roteiro de medição v2, a leitura do código do time de Web3 e as decisões A a E. Substitui `contexto-trilha-pesquisa.md` (setembro), `pesos-criterios.md` (seis critérios) e `resumo-equipe-matriz.md` |
| 14/10/2026 | Incorpora o benchmark (`benchmark-redes/`): finalidade da Monad atualizada pela documentação atual (600 ms, bloco de 300 ms); Monad cobra o gas limit; ambiente proposto para a Canton (LocalNet); notas propostas de C2-M1, C2-M3 e C5 com fontes; contagem Solidity conferida por script (49) e contagem Daml provisória (24); dados medidos do Besu (seção 8.1); ameaças 14 a 17; fonte para o exemplo de rede sem cobrança de gas |
| 16/10/2026 | Benchmark movido para este repositório (`benchmark-redes/`); pesquisas de setembro movidas para `docs/pesquisa-redes/`; resultados passam a ser gerados em `docs/resultados.md` |
| 16/10/2026 | Repositório reorganizado por função: `pesquisa/` (1-redes-candidatas, 2-metodo com este arquivo e o roteiro, 3-resultados), `entregas/` (resumo executivo), `dados/` (coletas brutas) e `benchmark/` (código) |
| 16/10/2026 | Seção 8.1 passa a marcar a origem de cada número (rede local, testnet, projeção ou a medir), com linhas reservadas para as testnets e a Canton |
| 16/10/2026 | Coleta completa nas cinco redes: testnets Sepolia, Fuji e Monad e Canton em sandbox local; seção 8.1 com todos os números, resultado da matriz, achado do Glamsterdam na Sepolia e decisão pendente sobre o custo da Canton; C5 confirmado nas testnets; ameaças 18 a 21 |

---

## Glossário

| Termo | Explicação |
|---|---|
| MCDM / MADM | Decisão multicritério. MADM é o caso em que as alternativas formam uma lista finita, conhecida antes da análise |
| AHP | Método que calcula pesos comparando critérios dois a dois |
| CR (razão de consistência) | Mede o quanto os julgamentos do AHP se contradizem; até 0,10 é aceito |
| WSM (soma ponderada) | Pontuação = soma de peso × nota de cada critério |
| Normalização min-max | Converte valores de unidades diferentes para uma escala de 0 a 1 |
| Critério de benefício / de custo | Benefício: maior é melhor. Custo: menor é melhor |
| Condição de elegibilidade | Exigência para a rede entrar na lista; não vira nota |
| DvP | Entrega contra pagamento: o ativo só é entregue se o pagamento acontecer |
| Risco de principal | Perder o valor inteiro porque uma parte entregou e a outra não |
| Atomicidade | Tudo ou nada: a transação acontece inteira ou não acontece |
| Inversão de ranking | Incluir ou retirar uma alternativa muda a ordem das outras |
| Análise de sensibilidade | Testar se o ranking muda quando os pesos mudam |
| Dado declarado / medido | Declarado vem de documentação ou literatura; medido vem dos testes da equipe |
| Finalidade | Momento a partir do qual a transação não pode mais ser desfeita |
| EVM | Máquina virtual que executa contratos nas redes do tipo Ethereum |
| Daml | Linguagem de contratos usada na Canton |
| NFT (ERC-721) | Token único, que não é intercambiável com outro |

---

## 15. Referências

**Método**

- [R1] Farshidi, S. et al. (2020). Decision Support for Blockchain Platform Selection: Three Industry Case Studies. *IEEE Transactions on Engineering Management*, 67(4). https://doi.org/10.1109/TEM.2019.2956897
- [R2] Baninemeh, E.; Farshidi, S.; Jansen, S. (2023). A Decision Model for Decentralized Autonomous Organization Platform Selection. *Blockchain: Research and Applications*, 4. https://arxiv.org/abs/2107.14093
- [R3] Saaty, T. L. (2001). Deriving the AHP 1-9 Scale from First Principles. ISAHP 2001. https://www.isahp-org.creativedecisions.net/uploads/125-p.pdf
- [R4] Saaty, T. L.; Özdemir, M. S. (2003). Why the Magic Number Seven Plus or Minus Two. *Mathematical and Computer Modelling*, 38. https://doi.org/10.1016/S0895-7177(03)90083-5
- [R5] Triantaphyllou, E.; Sánchez, A. (1997). A Sensitivity Analysis Approach for Some Deterministic Multi-Criteria Decision-Making Methods. *Decision Sciences*, 28(1). https://doi.org/10.1111/j.1540-5915.1997.tb01306.x
- [R6] Belton, V.; Gear, T. (1983). On a Short-coming of Saaty's Method of Analytic Hierarchies. *Omega*, 11(3), 228-230. https://ideas.repec.org/a/eee/jomega/v11y1983i3p228-230.html
- [R7] Forman, E.; Peniwati, K. (1998). Aggregating Individual Judgments and Priorities with the AHP. *European Journal of Operational Research*, 108. https://www.isahp.org/uploads/383-aggregating.pdf
- [R8] Six, N.; Herbaut, N.; Salinesi, C. (2020). Which Blockchain to Choose? arXiv:2004.06080. https://arxiv.org/abs/2004.06080

**DvP e liquidação**

- [R9] CPSS/BIS (1992). Delivery versus Payment in Securities Settlement Systems. https://www.bis.org/cpmi/publ/d06.pdf
- [R10] CPSS-IOSCO (2012). Principles for Financial Market Infrastructures. https://bis.org/pfmi/help/principleid.htm
- [R11] BIS Quarterly Review, março de 2020, glossário. https://www.bis.org/publ/qtrpdf/r_qt2003c.pdf

**Segurança**

- [R12] ISO/IEC 25010, resumo das características de qualidade. https://iso25000.com/index.php/en/iso-25000-standards/iso-25010?start=6
- [R13] Bhargavan, K. et al. (2016). Formal Verification of Smart Contracts. PLAS '16. https://doi.org/10.1145/2993600.2993611
- [R14] Tolmach, P. et al. (2021). A Survey of Smart Contract Formal Specification and Verification. *ACM Computing Surveys*, 54(7). https://arxiv.org/abs/2008.02712
- [R15] Shin, Y. et al. (2011). Evaluating Complexity, Code Churn, and Developer Activity Metrics as Indicators of Software Vulnerabilities. *IEEE TSE*, 37(6). https://ieeexplore.ieee.org/document/5560680
- [R16] McCabe, T. J. (1976). A Complexity Measure. *IEEE TSE*, 2(4), 308-320. https://doi.org/10.1109/TSE.1976.233837

**Desempenho e custo**

- [R17] Gramoli, V. et al. (2023). Diablo: A Benchmark Suite for Blockchains. EuroSys '23. https://gramoli.github.io/pubs/Eurosys23-Diablo.pdf
- [R18] Hyperledger PSWG (2018). Blockchain Performance Metrics. https://www.lfdecentralizedtrust.org/learn/publications/blockchain-performance-metrics
- [R19] Javed, F. et al. (2025). An Empirical Smart Contracts Latency Analysis on Ethereum Blockchain. arXiv:2503.01397. https://arxiv.org/abs/2503.01397
- [R20] Lazăr, C.; Secrieru, G.; Onica, E. (2025). Where Should I Deploy My Contracts? arXiv:2504.10535. https://arxiv.org/abs/2504.10535
- [R21] Ethereum Foundation. Gas and Fees. https://ethereum.org/developers/docs/gas
- [R22] Ethereum Foundation. Run a Node. https://ethereum.org/developers/docs/nodes-and-clients/run-a-node

**Redes**

- [R23] Finalidade no Ethereum: nota de pesquisa https://notes.ethereum.org/@yannvon/S1wIxIDqbe [VERIFICAR título e autoria] e Gasper https://ethereum.org/developers/docs/consensus-mechanisms/pos/gasper/
- [R24] Avalanche. Avalanche Consensus. https://docs.avax.network/docs/primary-network/avalanche-consensus
- [R25] Monad. Documentação oficial. https://docs.monad.xyz
- [R26] Hyperledger Besu. Proof of Authority Consensus. https://besu.hyperledger.org/private-networks/concepts/poa
- [R27] Hyperledger Besu. Notas da versão 23.10.2. https://github.com/hyperledger/besu/releases/tag/23.10.2
- [R28] Canton Network. Comunicado de lançamento (2023). https://www.canton.network/canton-network-press-release
- [R29] EIP-20: Token Standard. https://eips.ethereum.org/EIPS/eip-20
- [R30] EIP-2200: Structured Definitions for Net Gas Metering. https://eips.ethereum.org/EIPS/eip-2200

**Projeto**

- [R31] Repositório do time de Web3, `projeto-inter-web3`, commit `3347bf2` (12/10/2026). https://github.com/anacampos-crypto/projeto-inter-web3
- [R32] Transações da demonstração na Sepolia (06/10/2026): `approve` https://sepolia.etherscan.io/tx/0xac5f8c4b2678129920ef2c91fb677d6c4d3324dc62dc9d63afe23934ecfeb3aa ; `createOffer` https://sepolia.etherscan.io/tx/0x1fcfa5db23515922b644a39fa15cec2dc7203a5d01dddbda212025f6a911467d ; `acceptOffer` https://sepolia.etherscan.io/tx/0xe503d1c3f1dddf19cb0de517e291be9b8be34539c0963243414899782658084f
- [R33] TAP e cronograma de entregas, no repositório geral do projeto. https://github.com/InteliBlockchain-IBC/projeto-banco-inter
- [R34] Scripts e dados do benchmark (coletor EVM, rede Besu, modelo Daml, análise), pastas `benchmark/` e `dados/` deste repositório, 14/10/2026.

**Fontes acrescentadas em 14/10/2026**

- [R35] Monad. Gas Pricing e Testnets. https://docs.monad.xyz/developer-essentials/gas-pricing ; https://docs.monad.xyz/developer-essentials/testnets
- [R36] Monad. MonadBFT. https://docs.monad.xyz/monad-arch/consensus/monad-bft
- [R37] Solidity 0.8.24. SMTChecker and Formal Verification. https://docs.soliditylang.org/en/v0.8.24/smtchecker.html
- [R38] Daml Forum. Formal Verification (ferramenta `daml-lf-verify`). https://discuss.daml.com/t/formal-verification/665
- [R39] Digital Asset. `cn-quickstart` (LocalNet da Canton). https://github.com/digital-asset/cn-quickstart
- [R40] Hyperledger Besu. Free gas networks. https://besu.hyperledger.org/private-networks/how-to/configure/free-gas
- [R41] Glamsterdam ativado na Sepolia em 06/10/2026, com reprecificação da criação de estado. https://cryptobriefing.com/ethereum-sepolia-forks-gloas-200m-gas/ ; https://defiprotocolbycode.substack.com/p/glamsterdam-gas-repricing-what-builders-should-check [VERIFICAR nas notas oficiais do fork]
- [R42] Digital Asset. Daml SDK 3.6 (`dpm sandbox`, Canton 3.6.1). https://get.digitalasset.com/install/install.sh
