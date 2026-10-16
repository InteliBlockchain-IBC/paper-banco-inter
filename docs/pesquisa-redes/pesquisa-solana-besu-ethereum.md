
## Protocolo de Concessão de Crédito Interfinanceiro

### Mockchain — Banco Inter

**Frente:** Pesquisa Acadêmica
**Responsável:** Victor Garcia Dos Santos
**Redes pesquisadas:** Solana, Hyperledger Besu e Ethereum Mainnet
**Data:** Setembro de 2026


# 1. Objetivo da pesquisa

Esta pesquisa tem como objetivo analisar três redes blockchain candidatas à utilização como infraestrutura para o **Protocolo de Concessão de Crédito Interfinanceiro**, desenvolvido no contexto do projeto Mockchain do Banco Inter.

As redes atribuídas são:

* **Solana**
* **Hyperledger Besu**
* **Ethereum Mainnet**

O levantamento busca compreender o funcionamento e as características de cada rede antes da etapa de comparação e seleção realizada pelo grupo.

A pesquisa considera aspectos como:

* arquitetura;
* mecanismo de consenso;
* validadores;
* smart contracts;
* ambiente de desenvolvimento;
* desempenho;
* finalização das transações;
* custos;
* privacidade;
* segurança;
* permissionamento;
* governança;
* aplicações financeiras;
* casos institucionais;
* compatibilidade com o PoC desenvolvido pelo grupo.

A **Matriz de Critérios para Benchmark de Redes Blockchain** foi utilizada somente como referência para identificar quais características seriam importantes para o projeto. A pesquisa não reproduz a estrutura de pontuação da matriz e não atribui notas às redes nesta etapa.

Uma observação importante: diferentemente da Solana e da Ethereum Mainnet, o **Hyperledger Besu não é uma rede**, e sim um **cliente (software) Ethereum** que pode ser utilizado tanto para participar da Ethereum pública quanto para construir redes privadas/permissionadas. Nesta pesquisa, "Besu" se refere ao uso do software para montar uma **rede permissionada em consórcio**.

# 2. Contexto do projeto

O projeto propõe um protocolo para representar uma operação de crédito interfinanceiro de curto prazo utilizando smart contracts.

A infraestrutura blockchain deverá permitir representar, entre outras etapas:

```text
Instituição A
      ↓
Solicitação de crédito
      ↓
Negociação
      ↓
Verificação das condições
      ↓
Liquidação
      ↓
Registro da operação
      ↓
Instituição B
```

A utilização de blockchain é estudada principalmente pela possibilidade de automatizar etapas que normalmente dependem de processos manuais ou sistemas separados.

Entre os pontos de interesse estão:

* registro compartilhado;
* execução automática de regras;
* redução de reconciliações;
* controle das partes autorizadas;
* atomicidade de determinadas operações;
* rastreabilidade;
* liquidação coordenada.

O PoC atual utiliza **Solidity, EVM e Foundry**, e é homologado na **Ethereum Sepolia** (testnet da Ethereum), conforme o requisito RNF01. Portanto, a compatibilidade do ambiente de desenvolvimento é uma característica importante para a continuidade da implementação.

É importante distinguir: a Sepolia é o **ambiente acadêmico do PoC**; esta pesquisa avalia redes candidatas à **infraestrutura de produção**.

# 3. Solana

## 3.1 Visão geral

A Solana é uma blockchain pública de camada 1 (L1) projetada para alto throughput e baixa latência, com foco em aplicações que exigem grande volume de transações, como pagamentos, negociação de ativos e stablecoins.

A rede utiliza uma arquitetura própria, que **não é baseada na EVM**. Seus programas (smart contracts) são executados na **Solana Virtual Machine (SVM)**.

A Solana é relevante para o setor financeiro principalmente por:

* volume de stablecoins e pagamentos;
* baixo custo por transação;
* tokenização de ativos;
* presença de instituições financeiras no ecossistema.

# 4. Arquitetura da Solana

## 4.1 Modelo de contas e programas

Na Solana, o código (programas) e os dados (contas) são separados. Os programas são *stateless* e todo o estado fica armazenado em contas.

Cada transação precisa declarar previamente quais contas irá ler e escrever. Isso permite que a rede execute em **paralelo** transações que não disputam as mesmas contas (runtime **Sealevel**).

Essa característica é central para o desempenho da rede, mas também muda a forma de modelar a aplicação: um contrato de crédito precisaria ser redesenhado segundo o modelo de contas, e não segundo o modelo de *storage* da EVM.

## 4.2 Proof of History

A Solana utiliza o **Proof of History (PoH)**, uma sequência de hashes que funciona como um relógio criptográfico, permitindo ordenar eventos sem que todos os nós precisem se comunicar a cada passo.

O PoH **não é o mecanismo de consenso** em si; ele é utilizado em conjunto com o consenso baseado em stake.

## 4.3 Permissionamento

A rede principal da Solana (mainnet-beta) é **pública e permissionless**: qualquer pessoa pode enviar transações, implantar programas e operar um validador.

Existem iniciativas de **ambientes permissionados baseados na tecnologia Solana** (as chamadas *Solana Permissioned Environments* — SPEs), nas quais uma instituição executa sua própria instância da tecnologia com validadores controlados. Esses ambientes, porém, são instâncias separadas e não a Solana Mainnet.

> **A verificar:** o grau de maturidade, suporte oficial e casos em produção das SPEs deve ser confirmado na documentação atual da Solana Foundation antes de qualquer uso como argumento.

# 5. Consenso da Solana

Historicamente, a Solana utiliza o **Tower BFT**, uma variação de PBFT que usa o Proof of History como relógio, combinado com Proof of Stake.

Nesse modelo:

* um líder é escolhido por rodada, conforme o stake;
* o líder produz blocos em *slots* de aproximadamente **400 ms**;
* os validadores votam nos blocos;
* a confirmação "finalizada" (*finalized*/rooted) ocorre após um número de votos sucessivos, levando em torno de **12,8 segundos**.

Em 2025 a comunidade aprovou o **Alpenglow**, novo protocolo de consenso (componentes Votor e Rotor) que substitui o Tower BFT e o PoH na votação, com meta de finalidade na faixa de **100–150 ms**.

> **A verificar:** a data de ativação do Alpenglow na mainnet e os tempos de finalidade efetivamente observados após a ativação.

# 6. Validadores e governança

Qualquer participante com hardware adequado e stake (próprio ou delegado em SOL) pode operar um validador. A rede possui mais de mil validadores, operados por entidades majoritariamente pseudônimas.

Os requisitos de hardware dos validadores são elevados (CPU, memória e banda de rede de alto desempenho), o que é frequentemente citado como fator de pressão sobre a descentralização.

A governança de mudanças de protocolo ocorre por meio de propostas (**SIMDs** — *Solana Improvement Documents*) e votação dos validadores ponderada por stake.

A existência de um segundo cliente independente (**Firedancer**, desenvolvido pela Jump Crypto) é relevante para a resiliência da rede, pois reduz a dependência de uma única implementação.

Para uma aplicação interbancária, **não há como restringir quem valida** a rede principal.

# 7. Smart contracts e desenvolvimento

## 7.1 Ambiente nativo

Os programas Solana são desenvolvidos principalmente em **Rust**, compilados para bytecode **SBF** (*Solana Bytecode Format*, derivado do eBPF), geralmente com o framework **Anchor**.

```text
Rust
   ↓
Anchor / Solana SDK
   ↓
SBF (eBPF)
   ↓
SVM
```

## 7.2 Compatibilidade com Solidity/EVM

A Solana **não é EVM**. Existem soluções de compatibilidade parcial:

* **Solang:** compilador que traduz Solidity para programas Solana — porém o modelo de contas continua sendo o da Solana e o ferramental Foundry não é suportado;
* **Neon EVM:** uma EVM executada como programa dentro da Solana — é uma camada adicional, com suas próprias limitações e riscos.

Nenhuma dessas opções permite reaproveitar diretamente o ambiente **Solidity + Foundry** do PoC com a mesma semântica.

Portanto, a utilização da Solana exigiria reescrita da camada de smart contracts.

# 8. Privacidade

A Solana é uma **blockchain pública**: transações, valores e endereços são visíveis on-chain.

O padrão **Token-2022 (Token Extensions)** inclui a extensão **Confidential Transfers**, que oculta valores de transferência utilizando criptografia homomórfica (ElGamal) e provas de conhecimento zero, com possibilidade de *auditor key* para divulgação controlada.

> **A verificar:** em 2025 o programa de verificação ZK utilizado pelas Confidential Transfers foi temporariamente desativado após a descoberta de uma vulnerabilidade. Deve-se confirmar o status atual antes de considerar o recurso disponível.

Mesmo com esse recurso, as **contrapartes permanecem visíveis**, o que é sensível para o caso de crédito interbancário.

# 9. Atomicidade e DvP

Uma transação Solana pode conter várias instruções, inclusive chamadas a diferentes programas (*Cross-Program Invocation* — CPI). Se qualquer instrução falhar, **toda a transação é revertida**.

Isso permite, em princípio, estruturar uma troca atômica de "entrega contra pagamento" dentro de uma única transação.

Assim como na análise da Stellar, é necessário diferenciar **atomicidade da transação** de **implementação completa de DvP**, que depende dos ativos, contratos e regras envolvidos.

# 10. Desempenho

A Solana é reconhecida por alto throughput e baixa latência:

* slots de aproximadamente 400 ms;
* confirmação otimista em poucos segundos;
* finalização em torno de 12,8 s no modelo Tower BFT (com meta sub-segundo após Alpenglow).

Esses números são **dados apresentados pela própria rede** e por exploradores públicos. A rede também possui histórico de **interrupções (outages)** relevantes, especialmente entre 2021 e 2024, embora a estabilidade tenha melhorado nos anos seguintes.

Para o critério de resiliência sob concorrência, é relevante que a Solana possui histórico de **transações descartadas** em momentos de congestionamento, exigindo *retries* e taxas de prioridade.

# 11. Custos

A Solana possui taxas muito baixas:

* **taxa base** fixa por assinatura (5.000 lamports);
* **taxa de prioridade** opcional, cobrada por unidade de computação, que varia conforme a demanda;
* **rent** (depósito) para manter contas com dados on-chain.

Embora baixo em termos absolutos, o custo **não é totalmente previsível** em momentos de congestionamento, devido às taxas de prioridade.

# 12. Segurança

A segurança da Solana depende de:

* distribuição do stake entre validadores;
* robustez do cliente (hoje com diversidade via Firedancer);
* correção dos programas implantados (o modelo de contas gera classes próprias de vulnerabilidade, como validação incorreta de contas e *signers*).

Os episódios de indisponibilidade da rede mostram que **liveness** é um ponto a ser considerado, principalmente para uma aplicação com horário crítico de liquidação.

# 13. Aplicações institucionais

A Solana possui presença crescente em aplicações financeiras:

* **stablecoins** (USDC, PYUSD e outras) e pagamentos — incluindo a integração da **Visa** para liquidação em USDC;
* **tokenização de fundos** — o fundo BENJI da Franklin Templeton (disponível na Solana desde 2024) e o fundo **BUIDL** da BlackRock (expandido para Solana em 2025);
* **Société Générale – FORGE**, com a stablecoin EURCV também emitida na Solana.

> **A verificar:** datas e abrangência de cada caso nas fontes oficiais das instituições.

# 14. Síntese da Solana

| Aspecto                | Resultado da pesquisa                                          |
| ---------------------- | -------------------------------------------------------------- |
| Arquitetura            | L1 pública, modelo de contas, execução paralela                |
| Consenso               | Tower BFT + PoH (migração para Alpenglow)                      |
| Validadores            | Abertos, majoritariamente pseudônimos                          |
| Permissionamento       | Não na mainnet (existem ambientes permissionados separados)    |
| EVM                    | Não                                                            |
| Solidity               | Apenas via Solang/Neon, com limitações                         |
| Foundry                | Não suportado                                                  |
| Smart contracts        | Rust / Anchor / SBF                                            |
| Privacidade            | Pública; Confidential Transfers (Token-2022) ocultam valores   |
| DvP                    | Atomicidade de transação com múltiplas instruções              |
| Desempenho             | Slots de ~400 ms; finalização ~12,8 s (meta sub-segundo)       |
| Custos                 | Muito baixos, com taxa de prioridade variável                  |
| Aplicações financeiras | Stablecoins, pagamentos, BENJI, BUIDL, Visa, SG-FORGE          |

# 15. Hyperledger Besu

## 15.1 Visão geral

O **Hyperledger Besu** é um cliente Ethereum de código aberto, escrito em **Java** e licenciado sob **Apache 2.0**, mantido sob a **LF Decentralized Trust** (antiga Hyperledger Foundation, da Linux Foundation).

O Besu pode ser utilizado de duas formas:

* como cliente da **Ethereum Mainnet** pública;
* como base para **redes privadas e permissionadas**, com consenso de autoridade (*Proof of Authority*).

É neste segundo uso que o Besu se torna relevante para o projeto: ele permite construir uma rede de consórcio entre instituições identificadas, mantendo **total compatibilidade com a EVM**.

O Besu foi a tecnologia escolhida pelo **Banco Central do Brasil** para a plataforma-piloto do **Drex**, o que o torna especialmente relevante no contexto brasileiro.

# 16. Arquitetura do Besu

## 16.1 Rede de consórcio

Em uma rede privada Besu, as próprias instituições participantes operam os nós. Cada instituição pode ter:

* nós validadores (participam do consenso);
* nós não validadores (mantêm cópia do ledger e expõem RPC).

A rede possui um **arquivo gênesis** próprio, no qual são definidos parâmetros como tempo de bloco, validadores iniciais, limite de gas e preço de gas.

## 16.2 Permissionamento

O Besu possui recursos de permissionamento em dois níveis:

* **Permissionamento de nós:** lista de nós autorizados a se conectar à rede;
* **Permissionamento de contas:** lista de contas autorizadas a enviar transações.

Esses controles podem ser configurados localmente (arquivos de configuração em cada nó). A documentação também previa **permissionamento on-chain** via smart contracts.

> **A verificar:** o permissionamento on-chain e o recurso de transações privadas (Tessera) foram marcados como **deprecated** em versões recentes do Besu. Deve-se confirmar na documentação atual quais mecanismos seguem suportados.

Controle de quem pode **implantar contratos** pode ser implementado via permissionamento de contas ou por lógica da aplicação.

# 17. Consenso do Besu

Para redes privadas, o Besu oferece protocolos de *Proof of Authority*:

* **QBFT** — protocolo recomendado para redes de consórcio;
* **IBFT 2.0** — protocolo anterior, hoje desencorajado em favor do QBFT;
* **Clique** — protocolo mais simples, descontinuado.

O **QBFT** é um protocolo tolerante a falhas bizantinas (BFT) com as seguintes características:

* validadores conhecidos e identificados;
* tolera até **f** validadores faltosos em **3f + 1**;
* **finalidade imediata**: um bloco aceito não é revertido — não há *forks* nem reorganizações de cadeia;
* tempo de bloco configurável (por exemplo, 1 a 5 segundos).

Para o projeto, a **finalidade determinística** é uma característica diretamente ligada ao critério de *settlement finality* da matriz.

Como limitação, protocolos BFT clássicos exigem troca de mensagens entre todos os validadores, e o desempenho tende a cair à medida que o número de validadores aumenta. Para um consórcio de poucos bancos, isso não é um problema relevante.

# 18. Validadores e governança

Em redes QBFT, os validadores são adicionados e removidos por **votação dos validadores existentes** (via API JSON-RPC) ou por um **contrato inteligente** de gestão de validadores.

Isso permite estruturar uma governança na qual:

* somente instituições autorizadas validam;
* a entrada de um novo banco depende de aprovação do consórcio;
* as regras podem ser documentadas em um acordo entre participantes.

Por outro lado, a governança **não é fornecida pela tecnologia**: o consórcio precisa definir contratualmente quem opera a rede, como decisões são tomadas e como incidentes são tratados.

# 19. Smart contracts e desenvolvimento

## 19.1 Compatibilidade com EVM

O Besu implementa a **EVM** conforme a especificação da Ethereum. Isso permite utilizar diretamente o ambiente do PoC:

```text
Solidity
   ↓
EVM
   ↓
Foundry
   ↓
Smart Contract
```

Os contratos atuais podem ser implantados em uma rede Besu **sem reescrita**, com adaptação apenas de configuração (RPC, chain ID, contas).

## 19.2 Ferramentas

* Solidity;
* Foundry (forge, cast, anvil);
* bibliotecas como ethers.js, viem e web3.js;
* ferramentas de monitoramento (Prometheus/Grafana, suportados nativamente pelo Besu);
* **Hyperledger Caliper**, citado na matriz como referência para testes de desempenho.

Uma atenção importante: a **versão da EVM (hardfork)** habilitada na rede privada deve ser compatível com a versão do compilador Solidity utilizada (ex.: suporte a opcodes introduzidos no Shanghai/Cancun).

# 20. Privacidade

Por padrão, todos os nós de uma rede Besu veem todas as transações. Porém, como a rede é **privada**, o público externo não tem acesso aos dados.

Historicamente, o Besu oferecia **transações privadas** com o gerenciador **Tessera**, permitindo que apenas as partes envolvidas vissem determinada transação. Esse recurso foi descontinuado nas versões recentes (ver Seção 16.2).

No **piloto do Drex**, a privacidade foi justamente o principal desafio apontado pelo Banco Central: soluções como Anonymous Zether, Starlight, Rayls e outras foram testadas sobre a base Besu, e o Bacen concluiu que as soluções ainda não atendiam plenamente aos requisitos de sigilo bancário.

Para o projeto, as alternativas de privacidade em uma rede Besu são:

* restringir a rede apenas às instituições participantes;
* armazenar dados sensíveis off-chain e registrar apenas hashes on-chain;
* usar soluções adicionais de privacidade (ZK, redes privadas por par de instituições).

# 21. Desempenho

O desempenho de uma rede Besu depende da configuração escolhida:

* tempo de bloco (configurável);
* número de validadores;
* limite de gas por bloco;
* infraestrutura dos nós.

Com QBFT, uma transação é considerada **final assim que incluída em um bloco**, o que permite tempos de finalização na faixa de poucos segundos.

Como a rede é controlada pelo consórcio, **não há competição com tráfego externo**, o que favorece a previsibilidade no horário crítico de fechamento.

Esses resultados precisam ser medidos no ambiente efetivamente montado pelo grupo.

# 22. Custos

Em uma rede Besu privada, o modelo econômico é definido pelo consórcio:

* é possível configurar **preço de gas zero** (*free gas network*);
* o gas continua limitando o consumo computacional de cada transação, mas sem custo monetário;
* não há token nativo com cotação de mercado.

O custo relevante passa a ser **operacional**:

* infraestrutura dos validadores e nós;
* manutenção e atualização do software;
* monitoramento;
* segurança e gestão de chaves;
* governança do consórcio.

# 23. Segurança

A segurança de uma rede Besu permissionada depende principalmente:

* da tolerância BFT (quantidade de validadores honestos);
* da escolha e da independência dos validadores;
* da gestão de chaves dos validadores e das contas;
* da correção dos contratos;
* da disponibilidade da infraestrutura.

Um consórcio pequeno tem **menor descentralização** que uma rede pública, e a segurança se apoia na confiança jurídica e contratual entre os participantes — o que é coerente com o modelo de governança identificada da matriz (Filtro A).

# 24. Aplicações institucionais

O Besu possui presença relevante em aplicações de infraestrutura financeira:

* **Drex (Banco Central do Brasil):** a plataforma-piloto foi construída sobre Hyperledger Besu, com participação de consórcios de bancos brasileiros, incluindo testes de DvP com títulos públicos federais tokenizados;
* **Projetos de bancos centrais e mercados de capitais** em outros países, utilizados como referência em pilotos de CBDC e tokenização;
* uso por empresas e consórcios que precisam de uma rede EVM privada.

> **A verificar:** em 2025 o Bacen anunciou que a primeira fase de lançamento do Drex seria realizada **sem uso de DLT**, priorizando casos de uso como gravames e reconciliação. Isso não invalida os aprendizados técnicos do piloto com Besu, mas deve ser registrado com a fonte oficial.

# 25. Síntese do Hyperledger Besu

| Aspecto                | Resultado da pesquisa                                            |
| ---------------------- | ---------------------------------------------------------------- |
| Tipo                   | Cliente Ethereum (Java, Apache 2.0) para redes públicas/privadas |
| Arquitetura            | Rede privada/permissionada em consórcio                          |
| Consenso               | QBFT (Proof of Authority, BFT)                                   |
| Finalidade             | Imediata/determinística                                          |
| Validadores            | Instituições identificadas, geridas por votação ou contrato      |
| Permissionamento       | Nós e contas                                                      |
| EVM                    | Sim                                                               |
| Solidity               | Sim                                                               |
| Foundry                | Compatível                                                        |
| Privacidade            | Rede restrita ao consórcio; privacidade entre membros é limitada |
| DvP                    | Atomicidade de transação EVM; testado no piloto Drex              |
| Desempenho             | Configurável; sem concorrência externa                           |
| Custos                 | Gas pode ser zero; custo é operacional                           |
| Aplicações financeiras | Piloto Drex, pilotos de CBDC e tokenização                        |

# 26. Ethereum Mainnet

## 26.1 Visão geral

A Ethereum é a principal blockchain pública de smart contracts e a origem da **EVM**, ambiente utilizado pelo PoC.

É a rede com maior ecossistema de desenvolvimento, maior volume de ativos tokenizados e maior histórico de auditorias e ferramentas de segurança.

A **Sepolia**, onde o PoC é homologado, é uma testnet da própria Ethereum. Portanto, a Ethereum Mainnet é o ambiente mais **semelhante ao atual** do ponto de vista técnico.

# 27. Arquitetura e consenso da Ethereum

## 27.1 Proof of Stake

Desde o **Merge** (setembro de 2022), a Ethereum utiliza **Proof of Stake**. O protocolo de consenso é o **Gasper**, que combina:

* **LMD-GHOST** — regra de escolha da cadeia;
* **Casper FFG** — mecanismo de finalização.

A rede é organizada em:

* **slots** de 12 segundos (um bloco por slot);
* **épocas** de 32 slots (6,4 minutos).

Um bloco é considerado **finalizado** após aproximadamente **duas épocas**, ou seja, cerca de **12,8 a 15 minutos**.

Antes disso, o bloco pode, em teoria, ser reorganizado — embora reorganizações profundas sejam raras.

## 27.2 Separação em camadas

A arquitetura atual separa:

* **camada de execução** (clientes como Geth, Nethermind, **Besu**, Erigon, Reth);
* **camada de consenso** (clientes como Prysm, Lighthouse, Teku, Nimbus, Lodestar).

A diversidade de clientes é um fator relevante de resiliência da rede.

## 27.3 Atualizações recentes

* **Dencun (2024):** introduziu *blobs* (EIP-4844), reduzindo custos das redes de camada 2;
* **Pectra (maio de 2025):** incluiu melhorias em contas (EIP-7702) e no staking;
* **Fusaka (dezembro de 2025):** introduziu PeerDAS, ampliando a capacidade de dados.

> **A verificar:** propostas de redução do tempo de finalização (*single slot finality* e similares) seguem em pesquisa e não devem ser consideradas disponíveis.

# 28. Validadores e governança

Qualquer participante com **32 ETH** pode operar um validador. A rede possui cerca de um milhão de validadores ativos, operados por indivíduos, *exchanges*, provedores de staking e protocolos de *liquid staking*.

Os validadores são **pseudônimos**: não há identificação obrigatória dos operadores.

A governança do protocolo ocorre de forma off-chain, por meio de **EIPs** (*Ethereum Improvement Proposals*), discussões públicas entre desenvolvedores dos clientes e adoção das atualizações pelos operadores de nós.

Para uma aplicação interbancária:

* **não é possível escolher ou restringir os validadores**;
* **não é possível restringir quem envia transações** no nível da rede (apenas no nível do contrato, por meio de *allowlists* em Solidity).

# 29. Smart contracts e desenvolvimento

A Ethereum é o ambiente nativo do stack utilizado pelo PoC:

```text
Solidity
   ↓
EVM
   ↓
Foundry
   ↓
Ethereum
```

Os contratos atuais podem ser implantados na Mainnet **sem nenhuma adaptação** de código — a transição Sepolia → Mainnet exige apenas mudança de RPC, chain ID e contas.

O ecossistema oferece a maior variedade de ferramentas:

* Foundry, Hardhat;
* bibliotecas auditadas (OpenZeppelin);
* padrões de tokens (ERC-20, ERC-721, ERC-1155, ERC-3643 para tokens permissionados);
* ferramentas de análise estática e verificação formal.

# 30. Privacidade

A Ethereum é uma **blockchain pública e transparente**: todas as transações, valores, contrapartes e o estado dos contratos são visíveis a qualquer pessoa, inclusive no **mempool**, antes da inclusão no bloco.

Isso gera riscos adicionais para uma aplicação financeira:

* exposição de volumes, taxas e limites de crédito;
* **MEV** (*Maximal Extractable Value*) e *front-running*;
* identificação de padrões de operação das instituições.

As alternativas de privacidade são implementadas **na camada de aplicação** ou em outras camadas:

* dados sensíveis off-chain, com apenas hashes on-chain;
* provas de conhecimento zero;
* redes de camada 2 privadas ou permissionadas ancoradas na Ethereum.

Para o critério de privacidade da matriz, a Ethereum Mainnet corresponde ao cenário de **transparência integral** por padrão.

# 31. Atomicidade e DvP

Uma transação EVM é **atômica**: se qualquer parte da execução falhar, todo o estado é revertido. Um mesmo contrato pode transferir o token de crédito e o ativo de liquidação na mesma chamada.

Essa é a mesma propriedade disponível em qualquer rede EVM (incluindo Besu), e é a base da implementação do PoC.

A diferença na Mainnet é que a atomicidade de execução não elimina o risco de **reorganização antes da finalização** (ver Seção 27.1).

# 32. Desempenho

* tempo de bloco: 12 segundos;
* inclusão: geralmente em um a poucos blocos, dependendo da taxa paga;
* finalização econômica: cerca de 12,8 a 15 minutos.

Considerando o requisito RNF02 (confirmação em até 30 segundos), a Mainnet pode atender a **confirmação visível**, mas **não atende à finalidade determinística** nesse intervalo.

A capacidade de processamento da camada 1 é limitada, e a escalabilidade da Ethereum é direcionada principalmente às **redes de camada 2** (rollups).

# 33. Custos

A Ethereum utiliza o modelo **EIP-1559**:

* **base fee** — ajustada automaticamente conforme a demanda e queimada;
* **priority fee** — gorjeta ao validador.

Após o Dencun e o aumento do limite de gas, as taxas da camada 1 ficaram significativamente menores do que em anos anteriores. Ainda assim, o custo:

* é pago em ETH, ativo com cotação volátil;
* **varia conforme a demanda** da rede;
* pode ter picos em momentos de congestionamento.

Para operações de atacado, o valor absoluto tende a ser pouco relevante, mas a **imprevisibilidade** é um ponto negativo segundo a matriz.

# 34. Segurança

A Ethereum é considerada a plataforma de smart contracts com maior segurança econômica, dado o volume de ETH em stake e a diversidade de clientes e operadores.

Para o projeto, os principais riscos não estão no consenso, mas em:

* vulnerabilidades nos contratos (em ambiente totalmente aberto a atacantes);
* MEV e *front-running*;
* gestão de chaves das instituições;
* ausência de mecanismo de reversão em caso de erro operacional.

# 35. Aplicações institucionais

A Ethereum concentra a maior parte dos ativos do mundo real tokenizados em blockchains públicas:

* **BlackRock BUIDL** — fundo tokenizado lançado na Ethereum em 2024;
* **Franklin Templeton BENJI** — disponível na Ethereum desde 2025;
* emissões de títulos tokenizados por bancos e organismos multilaterais (por exemplo, títulos digitais do Banco Europeu de Investimento);
* **Société Générale – FORGE**, com stablecoins e títulos emitidos na Ethereum;
* **Enterprise Ethereum Alliance (EEA)**, que reúne empresas no desenvolvimento de padrões corporativos.

Esses casos mostram viabilidade em produtos regulados, geralmente com **controles de acesso no nível do token** (ex.: ERC-3643, *allowlists*), e não no nível da rede.

# 36. Síntese da Ethereum Mainnet

| Aspecto                | Resultado da pesquisa                                          |
| ---------------------- | -------------------------------------------------------------- |
| Arquitetura            | L1 pública; execução + consenso separados                      |
| Consenso               | Proof of Stake (Gasper: LMD-GHOST + Casper FFG)                |
| Validadores            | Abertos (32 ETH), pseudônimos, ~1 milhão                       |
| Permissionamento       | Não no nível da rede; apenas no nível do contrato              |
| EVM                    | Sim (ambiente de referência)                                   |
| Solidity               | Sim                                                            |
| Foundry                | Compatível (ambiente nativo)                                   |
| Privacidade            | Transparência integral por padrão                              |
| DvP                    | Atomicidade de transação EVM                                   |
| Desempenho             | Blocos de 12 s; finalização ~13–15 min                         |
| Custos                 | EIP-1559, variáveis e pagos em ETH                             |
| Aplicações financeiras | BUIDL, BENJI, títulos tokenizados, SG-FORGE, EEA              |

# 37. Relação com o projeto do Banco Inter

## 37.1 Solana

A Solana apresenta características atrativas para pagamentos de alto volume e baixo custo, com casos institucionais relevantes.

Entretanto, existe uma diferença tecnológica relevante:

```text
Solidity + EVM + Foundry
```

versus

```text
Rust + SBF + Anchor (SVM)
```

Além disso, a mainnet é pública, com validadores pseudônimos e sem permissionamento no nível da rede.

## 37.2 Hyperledger Besu

O Besu apresenta **compatibilidade direta** com o PoC e é a única das três opções que permite:

* rede permissionada entre instituições identificadas;
* controle de validadores e de contas;
* finalidade imediata (QBFT);
* gas configurável (inclusive zero);
* alinhamento com a infraestrutura utilizada no piloto do Drex.

Uma eventual implementação no Besu poderia aproveitar praticamente toda a estrutura tecnológica já criada.

## 37.3 Ethereum Mainnet

A Ethereum é o ambiente **tecnicamente mais próximo** do PoC (a Sepolia é sua testnet), com compatibilidade total.

Porém, para uso como infraestrutura de produção interbancária, apresenta limitações importantes:

* validadores pseudônimos e sem controle de participação;
* transparência integral de dados;
* finalização em torno de 13 a 15 minutos;
* custos variáveis.

# 38. Comparação técnica das redes

A comparação abaixo não atribui pontuação. Seu objetivo é consolidar as informações encontradas durante a pesquisa.

| Característica                | Solana                                   | Hyperledger Besu                      | Ethereum Mainnet                        |
| ----------------------------- | ---------------------------------------- | ------------------------------------- | --------------------------------------- |
| Tipo de infraestrutura        | L1 pública                               | Rede privada/consórcio                | L1 pública                              |
| Consenso                      | Tower BFT + PoH (→ Alpenglow)            | QBFT (PoA/BFT)                        | PoS (Gasper)                            |
| Validadores                   | Abertos, pseudônimos                     | Instituições identificadas            | Abertos, pseudônimos                    |
| Smart contracts               | Programas SVM                            | EVM                                   | EVM                                     |
| Linguagem principal           | Rust                                     | Solidity                              | Solidity                                |
| Máquina de execução           | SVM (SBF)                                | EVM                                   | EVM                                     |
| Compatibilidade com PoC atual | Baixa                                    | Alta                                  | Alta                                    |
| Foundry                       | Não suportado                            | Compatível                            | Compatível                              |
| Permissionamento              | Não na mainnet                           | Nativo (nós e contas)                 | Apenas no contrato                      |
| Privacidade                   | Pública; valores ocultáveis (Token-2022) | Restrita ao consórcio                 | Transparência integral                  |
| DvP                           | Atomicidade multi-instrução              | Atomicidade EVM; testado no Drex      | Atomicidade EVM                         |
| Finalização                   | ~12,8 s (meta sub-segundo)               | Imediata (poucos segundos)            | ~13–15 minutos                          |
| Taxas                         | Muito baixas, prioridade variável        | Configuráveis (pode ser zero)         | EIP-1559, variáveis                     |
| Tokenização                   | Sim (BENJI, BUIDL)                       | Pilotos (Drex, CBDCs)                 | Maior volume (BUIDL, BENJI etc.)        |
| Casos institucionais          | Visa, Franklin, BlackRock, SG-FORGE      | Banco Central do Brasil (Drex)        | BlackRock, Franklin, BEI, SG-FORGE      |
| Adaptação necessária ao PoC   | Maior (reescrita)                        | Mínima (configuração)                 | Mínima (configuração)                   |

# 39. Registro de descarte

## 39.1 Solana

**Status:** descartada para a próxima etapa do PoC atual.

### Motivo do descarte

O projeto estabeleceu como requisito técnico de elegibilidade (Filtro B da matriz) a compatibilidade com o ambiente **EVM/Solidity/Foundry**.

A Solana utiliza a **SVM**, com desenvolvimento em **Rust** e modelo de contas próprio, não sendo uma rede EVM. As alternativas de compatibilidade (Solang, Neon EVM) não preservam o ambiente Foundry nem a semântica dos contratos atuais.

Assim, para utilizar a Solana seria necessário:

* reescrever os smart contracts;
* remodelar o estado segundo o modelo de contas;
* substituir o ambiente Foundry;
* adaptar os testes;
* adaptar a integração do backend.

Adicionalmente, a mainnet não atende ao Filtro A (governança identificada), pois os validadores são abertos e pseudônimos.

### Justificativa

O descarte ocorre por **incompatibilidade com o stack técnico definido para o PoC**, e não por ausência de capacidade para aplicações financeiras. A pesquisa encontrou casos concretos de stablecoins, pagamentos e fundos tokenizados na rede.

> **A Solana é tecnicamente relevante para o setor financeiro, mas foi descartada neste benchmark específico por incompatibilidade com o stack EVM/Solidity/Foundry definido para o PoC.**

## 39.2 Ethereum Mainnet

**Status:** descartada como infraestrutura de produção; mantida como referência técnica (ambiente do PoC via Sepolia).

### Motivo do descarte

A Ethereum Mainnet atende ao Filtro B (é o ambiente nativo da EVM), mas **não atende ao Filtro A** da matriz:

* os validadores são abertos e pseudônimos;
* não existe governança institucional identificada sobre a rede;
* não é possível restringir participantes no nível da rede.

Além disso, apresenta pontos negativos nos critérios de privacidade (transparência integral) e finalidade (cerca de 13 a 15 minutos, acima dos 30 segundos do RNF02).

### Justificativa

O descarte ocorre por **incompatibilidade com o modelo de governança e privacidade exigido para operação interbancária**, e não por limitação técnica de smart contracts. A Ethereum continua sendo a referência técnica do projeto, pois o PoC é homologado na Sepolia e o código é integralmente portável.

> **A Ethereum Mainnet é o ambiente de referência do stack do projeto, mas foi descartada como rede de produção por não atender ao filtro de governança identificada e por limitações de privacidade e finalidade.**

# 40. Registro de continuidade

## 40.1 Hyperledger Besu

**Status:** mantido para as próximas etapas do benchmark.

### Motivos para continuidade

O Besu apresenta compatibilidade com:

* Solidity;
* EVM;
* Foundry;
* smart contracts já desenvolvidos pelo projeto.

Além disso, possui mecanismos de:

* permissionamento de nós e contas;
* validadores identificados (QBFT);
* finalidade imediata;
* configuração de gas (inclusive gas zero);
* operação em consórcio.

Também é a base tecnológica utilizada no piloto do Drex, o que reforça sua aderência ao contexto regulatório brasileiro.

O principal ponto de atenção é a **privacidade entre os próprios membros do consórcio**, que deverá ser tratada na arquitetura da solução.

Dessa forma, o Hyperledger Besu permanece como candidato para os testes práticos do benchmark.

# 41. O que ainda precisa ser validado

A pesquisa documental não é suficiente para concluir como as redes se comportariam no cenário específico do projeto.

Por isso, para a rede que permanecer no benchmark, deverão ser realizados testes experimentais.

## 41.1 Desempenho

Medir:

* tempo de confirmação;
* tempo de finalização;
* média;
* mediana;
* máximo;
* variação;
* efeito do tempo de bloco configurado e do número de validadores.

## 41.2 Concorrência

Executar diferentes volumes de operações simultâneas:

```text
10 transações
100 transações
500 transações
1.000 transações
```

Registrar:

* taxa de sucesso;
* falhas;
* retries;
* conflitos de nonce;
* tempo de processamento.

## 41.3 Liquidação

Testar a execução de operações envolvendo duas partes:

```text
Banco A
   ↓
Solicitação
   ↓
Contrato
   ↓
Banco B
   ↓
Liquidação
```

Também deve ser testado o comportamento quando uma das condições da operação não é atendida.

## 41.4 Custos

Como a rede Besu pode operar com gas zero, medir:

* consumo de gas por função (mesmo sem custo monetário);
* recursos de infraestrutura por nó (CPU, memória, disco);
* custo estimado de operação do consórcio.

## 41.5 Privacidade e permissionamento

Validar:

* bloqueio de contas não autorizadas;
* bloqueio de nós não autorizados;
* inclusão e remoção de validadores;
* quais dados ficam visíveis para cada participante.

# 42. Conclusão da pesquisa

A pesquisa analisou as redes **Solana, Hyperledger Besu e Ethereum Mainnet** de forma independente, considerando sua arquitetura, consenso, smart contracts, desempenho, custos, privacidade, governança e aplicações financeiras.

A **Solana** apresentou alto desempenho, baixo custo e casos institucionais relevantes, mas utiliza um stack incompatível com o PoC (Rust/SVM) e validadores abertos. Foi registrada como **descartada**.

A **Ethereum Mainnet** é o ambiente de referência do stack do projeto e possui o maior ecossistema de tokenização, mas não atende ao filtro de governança identificada e apresenta transparência integral e finalização lenta para o cenário interbancário. Foi registrada como **descartada como rede de produção**, mantendo-se como referência técnica.

O **Hyperledger Besu** combina compatibilidade total com EVM/Solidity/Foundry, permissionamento, validadores identificados e finalidade imediata, além de ter sido a base do piloto do Drex. Permanece como **candidato para a etapa prática**.

Assim, o resultado da pesquisa é:

```text
┌──────────────────────────────────────────────┐
│              PESSOA [ ]                      │
├──────────────────────────────────────────────┤
│ Solana                                       │
│ → Pesquisada                                 │
│ → Forte atuação em pagamentos/stablecoins    │
│ → Rust/SVM                                   │
│ → Descartada por incompatibilidade com PoC  │
├──────────────────────────────────────────────┤
│ Hyperledger Besu                             │
│ → Pesquisado                                 │
│ → Compatível com EVM/Solidity/Foundry        │
│ → Permissionado, QBFT, base do piloto Drex   │
│ → Mantido para benchmark                     │
├──────────────────────────────────────────────┤
│ Ethereum Mainnet                             │
│ → Pesquisada                                 │
│ → Compatível com EVM/Solidity/Foundry        │
│ → Pública, validadores pseudônimos           │
│ → Descartada como produção (Filtro A)        │
└──────────────────────────────────────────────┘
```

# 43. Referências

## Solana

**Solana Foundation.** Solana Documentation — Core Concepts (Accounts, Programs, Transactions).
https://solana.com/docs

**Solana Foundation.** Transaction Fees.
https://solana.com/docs/core/fees

**Solana Foundation.** Token Extensions — Confidential Transfer.
https://solana.com/docs/tokens/extensions

**Anza.** Alpenglow: A New Consensus for Solana.
https://www.anza.xyz/blog/alpenglow-a-new-consensus-for-solana

**Solang.** Solidity compiler for Solana.
https://solang.readthedocs.io/

**Yakovenko, A.** *Solana: A new architecture for a high performance blockchain* (whitepaper). 2017.
https://solana.com/solana-whitepaper.pdf

---

## Hyperledger Besu

**LF Decentralized Trust.** Hyperledger Besu Documentation.
https://besu.hyperledger.org/

**Hyperledger Besu.** QBFT consensus protocol.
https://besu.hyperledger.org/private-networks/how-to/configure/consensus/qbft

**Hyperledger Besu.** Permissioning.
https://besu.hyperledger.org/private-networks/concepts/permissioning

**Hyperledger Besu.** Free gas networks.
https://besu.hyperledger.org/private-networks/how-to/configure/free-gas

**Banco Central do Brasil.** Drex — Real Digital.
https://www.bcb.gov.br/estabilidadefinanceira/drex

**Saltini, R.; Hyland-Wood, D.** *IBFT 2.0: A Safe and Live Variation of the IBFT Blockchain Consensus Protocol for Eventually Synchronous Networks*. 2019.
https://arxiv.org/abs/1909.10194

**Hyperledger Caliper.** Blockchain Performance Benchmark Framework.
https://hyperledger-caliper.github.io/caliper/

---

## Ethereum

**Ethereum Foundation.** Proof-of-Stake.
https://ethereum.org/en/developers/docs/consensus-mechanisms/pos/

**Ethereum Foundation.** Gasper.
https://ethereum.org/en/developers/docs/consensus-mechanisms/pos/gasper/

**Ethereum Foundation.** Gas and Fees (EIP-1559).
https://ethereum.org/en/developers/docs/gas/

**Ethereum Foundation.** Ethereum Roadmap.
https://ethereum.org/en/roadmap/

**Buterin, V. et al.** *Combining GHOST and Casper*. 2020.
https://arxiv.org/abs/2003.03052

**Enterprise Ethereum Alliance.**
https://entethalliance.org/

**ERC-3643.** Token for Regulated EXchanges (T-REX).
https://eips.ethereum.org/EIPS/eip-3643
