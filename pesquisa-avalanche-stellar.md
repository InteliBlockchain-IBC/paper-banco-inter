
## Protocolo de Concessão de Crédito Interfinanceiro

### Mockchain — Banco Inter

**Frente:** Pesquisa Acadêmica
**Responsável:** Beatriz Sofia Freitas Sena
**Redes pesquisadas:** Avalanche e Stellar
**Data:** Setembro de 2026


# 1. Objetivo da pesquisa

Esta pesquisa tem como objetivo analisar duas redes blockchain candidatas à utilização como infraestrutura para o **Protocolo de Concessão de Crédito Interfinanceiro**, desenvolvido no contexto do projeto Mockchain do Banco Inter.

As redes atribuídas são:

* **Avalanche**
* **Stellar**

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

O PoC atual utiliza **Solidity, EVM e Foundry**, portanto a compatibilidade do ambiente de desenvolvimento é uma característica importante para a continuidade da implementação.

# 3. Avalanche

## 3.1 Visão geral

A Avalanche é uma plataforma blockchain que permite a criação de redes próprias dentro de seu ecossistema.

Sua arquitetura atual permite trabalhar tanto com a infraestrutura pública da Avalanche quanto com **Avalanche L1s**, redes com conjunto próprio de validadores e regras específicas.

As L1s podem ser configuradas para diferentes modelos de participação, incluindo redes permissionadas e redes com participação aberta. A documentação da Avalanche destaca que uma L1 pode possuir seu próprio ambiente de execução, conjunto de validadores e regras de operação.

Essa característica torna a Avalanche relevante para aplicações institucionais nas quais a organização pode precisar controlar:

* quem participa da rede;
* quem pode validar;
* quem pode enviar transações;
* quem pode implantar contratos;
* como a rede é administrada.

# 4. Arquitetura da Avalanche

## 4.1 Avalanche L1

As Avalanche L1s são blockchains com conjunto próprio de validadores.

A arquitetura atual diferencia as L1s da antiga estrutura de Subnets, permitindo que uma L1 tenha gerenciamento independente do seu conjunto de validadores. A documentação técnica informa que os validadores de uma L1 formam um conjunto independente da Primary Network.

Isso permite criar uma infraestrutura mais específica para determinado caso de uso.

Para uma aplicação interbancária, essa arquitetura poderia ser utilizada para construir uma rede com participação restrita a instituições autorizadas.

## 4.2 Permissionamento

A Avalanche possui recursos de permissionamento incorporados à infraestrutura das L1s.

A documentação oficial apresenta três dimensões que podem ser controladas:

* **Contract Deployer AllowList:** controla quem pode implantar contratos;
* **Transaction AllowList:** controla quem pode enviar transações;
* **Validator Permissioning:** controla quem pode participar como validador.

Esses controles são implementados por mecanismos da própria rede, e não apenas por regras externas da aplicação.

A Transaction AllowList, por exemplo, permite definir quais endereços estão autorizados a enviar transações e pode ser utilizada em redes com requisitos de KYC/AML.


# 5. Consenso da Avalanche

A Avalanche utiliza uma família de protocolos conhecida como **Snow consensus**.

O mecanismo possui uma abordagem diferente de modelos tradicionais como Proof of Work e Proof of Stake.

Em termos simplificados, os participantes consultam subconjuntos de outros participantes da rede e utilizam essas respostas para convergir para uma decisão.

Pesquisas acadêmicas descrevem o Snow consensus como uma família de protocolos descentralizados e sem líder, baseada em amostragem aleatória de participantes.

A literatura também destaca que o comportamento do protocolo depende da interação entre:

* parâmetros de segurança;
* aleatoriedade;
* comportamento adversarial;
* latência;
* condições de rede.

Por isso, características como segurança e finalização não devem ser avaliadas somente a partir de uma descrição simplificada do protocolo.

# 6. Validadores e governança

Nas Avalanche L1s, o conjunto de validadores pode ser administrado especificamente para aquela rede.

A documentação da Avalanche apresenta o **Validator Manager**, utilizado para controlar operações relacionadas aos validadores.

Entre as operações estão:

* adicionar validador;
* remover validador;
* alterar peso de um validador;
* desabilitar um validador.

O processo é integrado à infraestrutura da Avalanche por meio da P-Chain e de mensagens entre as cadeias.

Para uma rede institucional, isso permite definir uma estrutura na qual somente entidades previamente autorizadas participem da validação.

# 7. Smart contracts e desenvolvimento

## 7.1 Compatibilidade com EVM

Um dos principais pontos da Avalanche para este projeto é a compatibilidade com a **Ethereum Virtual Machine (EVM)**.

Isso permite utilizar tecnologias já presentes no PoC:

```text
Solidity
   ↓
EVM
   ↓
Foundry
   ↓
Smart Contract
```

A documentação da Avalanche apresenta configuração de L1s compatíveis com EVM e desenvolvimento utilizando Solidity.

Isso reduz a necessidade de reescrever os contratos atuais caso a Avalanche seja utilizada na próxima etapa do projeto.

## 7.2 Ferramentas

O ecossistema EVM permite utilizar ferramentas conhecidas pelo grupo, como:

* Solidity;
* Foundry;
* bibliotecas compatíveis com Ethereum;
* ferramentas de testes para contratos EVM;
* RPCs compatíveis com aplicações EVM.

Esse fator possui impacto direto no esforço necessário para adaptar o PoC.

# 8. Comunicação entre Avalanche L1s

A Avalanche possui o **Avalanche Warp Messaging (AWM)**, mecanismo destinado à comunicação entre diferentes L1s.

O AWM utiliza assinaturas BLS agregadas e informações relacionadas aos conjuntos de validadores para permitir que uma cadeia verifique mensagens originadas em outra.

Essa característica pode ser relevante em arquiteturas nas quais diferentes instituições ou aplicações utilizem L1s distintas.

No entanto, para o PoC atual, essa funcionalidade não é necessariamente necessária. O projeto primeiro precisa validar o funcionamento do protocolo dentro da rede escolhida.

# 9. Privacidade e controle de acesso

A Avalanche possui mecanismos específicos para criação de redes permissionadas.

A documentação diferencia:

### Rede permissionada privada

* leitura restrita;
* escrita restrita;
* validadores autorizados;
* participantes controlados.

### Rede permissionada pública

* leitura pública;
* escrita controlada;
* validadores autorizados.

### Rede permissionless

* participação aberta;
* validação aberta conforme as regras da rede.

Para uma aplicação interbancária, uma rede permissionada pode ser interessante porque as instituições participantes podem ser previamente identificadas.

# 10. DvP e aplicações financeiras

A arquitetura da Avalanche também possui materiais voltados para aplicações financeiras e estruturas de liquidação.

A documentação de privacidade e infraestrutura institucional da Avalanche apresenta cenários relacionados a:

* Delivery versus Payment;
* repo;
* securities lending;
* liquidação entre instituições;
* ativos financeiros.

A possibilidade de combinar uma rede permissionada, contratos EVM e controle de participantes permite construir aplicações nas quais regras de liquidação sejam executadas diretamente pelo protocolo.

Para o projeto, isso possui relação com a possibilidade de representar:

```text
Crédito
   +
Garantia/ativo
   +
Condições da operação
        ↓
Smart Contract
        ↓
Liquidação
```

Entretanto, a existência de recursos de infraestrutura não comprova que o contrato específico do projeto será atomicamente seguro. Essa propriedade deverá ser testada no PoC.

# 11. Desempenho

A Avalanche destaca baixa latência como uma de suas características.

A documentação da plataforma apresenta tempos de finalidade muito baixos para determinados ambientes Avalanche, incluindo a C-Chain e L1s configuradas para aplicações específicas.

Esses números são **dados apresentados pela própria Avalanche** e devem ser diferenciados de medições independentes.

Para o projeto, o mais importante será medir o comportamento da rede no ambiente efetivamente utilizado.

Os testes deverão considerar:

* tempo de submissão;
* tempo de inclusão;
* tempo de confirmação;
* tempo de finalização;
* comportamento sob concorrência.

# 12. Custos

As Avalanche L1s permitem configurar elementos relacionados ao modelo econômico da rede.

Entre eles estão:

* token utilizado para taxas;
* parâmetros de gas;
* taxas de transação;
* mecanismos relacionados ao gerenciamento de taxas.

Isso permite que uma organização modele uma rede com características econômicas diferentes de uma blockchain pública de uso geral.

Para o projeto, ainda será necessário medir o custo real da infraestrutura escolhida.

Além do custo de execução das transações, devem ser considerados:

* infraestrutura dos validadores;
* manutenção dos nós;
* armazenamento;
* RPC;
* monitoramento;
* operação da rede.

---

# 13. Segurança

A segurança da Avalanche depende tanto do protocolo de consenso quanto da configuração específica da rede.

Em uma L1 permissionada, por exemplo, a segurança também está relacionada:

* à escolha dos validadores;
* ao controle das chaves;
* ao gerenciamento de permissões;
* à governança;
* à disponibilidade dos nós.

A documentação do Validator Manager demonstra que operações de inclusão, remoção e alteração de validadores possuem mecanismos específicos de controle.

A literatura acadêmica sobre Avalanche também demonstra que segurança e liveness devem ser analisados considerando os parâmetros do consenso, não apenas o tempo de confirmação observado.

# 14. Aplicações institucionais

A Avalanche possui iniciativas relacionadas a:

* tokenização;
* ativos financeiros;
* stablecoins;
* infraestrutura institucional;
* redes permissionadas;
* aplicações de mercado financeiro.

A própria arquitetura de L1s foi desenvolvida para permitir redes específicas com regras próprias.

Portanto, existe uma relação conceitual entre a infraestrutura Avalanche e aplicações que precisam de maior controle sobre os participantes.

> **Atualização de verificação:** o fundo tokenizado BENJI, da Franklin Templeton (ver Seção 27), passou a estar disponível também na Avalanche a partir de 2024, além da Stellar (rede original), Polygon, Arbitrum, Aptos, Base, Solana e Ethereum. Isso reforça, com um exemplo concreto e verificável, a presença da Avalanche em aplicações financeiras institucionais tokenizadas — reduzindo o número de casos como diferencial exclusivo da Stellar nesta comparação específica.

# 15. Síntese da Avalanche

| Aspecto                | Resultado da pesquisa                                         |
| ----------------------- | --------------------------------------------------------------|
| Arquitetura            | L1s soberanas e infraestrutura Avalanche                      |
| Consenso               | Família Snow/Snowman                                          |
| Validadores            | Podem ser gerenciados por L1                                  |
| Permissionamento       | Disponível                                                    |
| EVM                    | Sim                                                            |
| Solidity               | Sim                                                            |
| Foundry                | Compatível com o ambiente EVM                                 |
| Smart contracts        | EVM                                                            |
| Privacidade            | Pode ser implementada em arquiteturas permissionadas/privadas |
| DvP                    | Há casos e documentação relacionados                          |
| Desempenho             | Baixa latência reportada pela rede                             |
| Custos                 | Configuráveis em L1                                            |
| Aplicações financeiras | Tokenização, liquidação e infraestrutura institucional (inclui BENJI, desde 2024) |

# 16. Stellar

## 16.1 Visão geral

A Stellar é uma blockchain pública voltada principalmente para aplicações relacionadas a:

* pagamentos;
* transferência de valor;
* ativos digitais;
* tokenização;
* serviços financeiros.

A rede utiliza o **Stellar Consensus Protocol (SCP)**.

A Stellar apresenta a rede como uma infraestrutura aberta para pagamentos e ativos financeiros, com utilização também em aplicações institucionais.


# 17. Arquitetura e consenso da Stellar

## 17.1 Stellar Consensus Protocol

O Stellar utiliza o **Stellar Consensus Protocol (SCP)**, baseado em **Federated Byzantine Agreement (FBA)**.

Nesse modelo, os nós definem quais outros nós consideram confiáveis.

A partir dessas relações são construídos:

* quorum sets;
* quorum slices;
* quorums.

Dessa forma, a rede não utiliza Proof of Work ou Proof of Stake para definir consenso.

A documentação explica que cada nó decide quais outros participantes deseja considerar confiáveis.


# 18. Segurança do consenso Stellar

O SCP possui uma base acadêmica relevante.

García-Pérez e Schett realizaram uma análise formal do protocolo (*Deconstructing Stellar Consensus*, 2019) e apresentaram uma prova de correção do SCP sob as condições consideradas no trabalho.

Ao mesmo tempo, outros estudos apontam que as propriedades de segurança e disponibilidade da Stellar dependem da estrutura dos quorum slices.

Kim, Kwon e Kim (*Is Stellar As Secure As You Think?*, 2019) analisaram a topologia dos validadores da rede e levantaram questões sobre centralização e dependência de determinados nós.

Isso mostra que a análise da Stellar deve considerar não apenas o algoritmo, mas também a configuração efetiva da rede.


# 19. Smart contracts na Stellar

A plataforma de smart contracts da Stellar é chamada, na documentação técnica e para desenvolvedores, de **Soroban**; em materiais de produto voltados a público mais amplo, a mesma plataforma também é referida como **Stellar Smart Contracts**. Os dois nomes descrevem a mesma tecnologia.

Soroban foi lançado em mainnet em fevereiro de 2024 (Protocolo 20) e utiliza:

* Rust;
* WebAssembly;
* Soroban SDK;
* Soroban CLI;
* RPC;
* ambiente de desenvolvimento próprio.

A documentação oficial informa que os contratos são desenvolvidos em Rust e executados em WebAssembly.

A arquitetura pode ser representada por:

```text
Rust
   ↓
Soroban SDK
   ↓
WebAssembly
   ↓
Stellar
```

Essa é uma diferença importante em relação ao PoC atual.

O projeto utiliza:

```text
Solidity
   ↓
EVM
   ↓
Foundry
```

Portanto, a utilização da Stellar exigiria adaptação da camada de smart contracts.


# 20. Ferramentas de desenvolvimento

O ecossistema Stellar oferece ferramentas específicas para desenvolvimento com smart contracts.

Entre elas:

* Rust;
* Soroban CLI;
* RPC;
* sandbox local;
* SDK;
* ferramentas de teste;
* integração com aplicações web.

A documentação oficial apresenta o fluxo de desenvolvimento desde a criação de um contrato até sua implantação em testnet.

Apesar da existência de ferramentas próprias, elas não são equivalentes ao ambiente Solidity + Foundry utilizado no PoC.


# 21. Atomicidade das operações

A Stellar permite combinar operações dentro de uma mesma transação.

Isso possibilita executar mudanças de estado de forma coordenada.

Para uma aplicação financeira, essa característica pode ser utilizada para estruturar operações nas quais diferentes ações precisam ser concluídas conjuntamente.

Entretanto, é necessário diferenciar:

**atomicidade de uma transação**

de

**implementação completa de um mecanismo de DvP**.

A segunda depende da arquitetura dos ativos, regras e contratos envolvidos.

Por isso, o uso da Stellar para o projeto precisaria ser validado por um PoC específico.


# 22. Privacidade

A Stellar é uma **blockchain pública**.

A documentação oficial afirma que as transações são registradas on-chain e podem ser visualizadas publicamente.

Porém, a rede vem desenvolvendo mecanismos de privacidade configurável.

A abordagem atual é descrita pela Stellar como:

> Open by default. Private when needed.

A estratégia inclui:

* Privacy Pools;
* Confidential Tokens;
* Stellar Private Payments;
* view keys;
* mecanismos de divulgação controlada;
* verificação de provas de conhecimento zero (zero-knowledge).

Essas ferramentas buscam permitir privacidade em aplicações que precisam preservar determinados dados financeiros sem abandonar completamente a infraestrutura pública.


# 23. Privacidade para aplicações institucionais

A Stellar apresenta aplicações de privacidade para cenários como:

* pagamentos empresariais;
* treasury management;
* liquidação institucional;
* ativos financeiros tokenizados.

**Verificado:** a atualização **X-Ray** (Protocolo 25) foi votada em testnet em 7 de janeiro de 2026 e entrou em mainnet em 22 de janeiro de 2026. Ela introduz suporte nativo à curva elíptica BN254 e às funções de hash Poseidon/Poseidon2 — primitivas criptográficas voltadas a provas de conhecimento zero (ZK) — ampliando a infraestrutura disponível para construção de soluções de privacidade configurável na rede. A informação original do documento (data de janeiro de 2026) está correta.

Para o projeto do Banco Inter, isso é relevante porque informações como:

* valor da operação;
* taxa negociada;
* limite de crédito;
* identidade das contrapartes;
* condições da operação

podem ser consideradas sensíveis.

Entretanto, a abordagem Stellar é diferente de simplesmente utilizar uma blockchain privada. A rede permanece pública e a privacidade é implementada de forma configurável no nível da aplicação.

# 24. Desempenho e finalização

A Stellar informa que seu processo de consenso geralmente leva aproximadamente **5 segundos**.

Em um caso institucional publicado pela própria Stellar, a Franklin Templeton informa finalização de aproximadamente **5 a 7 segundos** para operações relacionadas ao fundo BENJI.

Esses valores são úteis como referência, mas o benchmark do projeto ainda deve medir o comportamento real da aplicação.

Os testes podem observar:

* tempo médio;
* tempo máximo;
* variação;
* comportamento sob concorrência;
* taxa de falhas.

# 25. Custos

A Stellar utiliza um modelo de taxas que diferencia transações tradicionais e transações de smart contracts.

Para Soroban existem:

* **inclusion fee**;
* **resource fee**.

A resource fee considera recursos utilizados pela execução do contrato, como:

* instruções;
* leitura;
* escrita;
* armazenamento;
* tamanho da transação;
* outros recursos computacionais.

A documentação também informa que determinadas taxas podem variar conforme o consumo de recursos e parâmetros da rede.

Esse modelo precisa ser considerado ao estimar o custo de uma aplicação de crédito interfinanceiro.


# 26. Tokenização e aplicações financeiras

A Stellar possui forte atuação em tokenização.

A rede apresenta casos relacionados a:

* fundos;
* títulos;
* ativos financeiros;
* stablecoins;
* pagamentos;
* ativos do mundo real.

A página oficial de casos institucionais reúne exemplos de empresas utilizando Stellar para tokenização e serviços financeiros.


# 27. Caso Franklin Templeton

Um dos casos mais relevantes é o **Franklin OnChain U.S. Government Money Fund**, representado pelo token BENJI.

**Verificado:** segundo o estudo de caso publicado pela Stellar e confirmado por release da própria Franklin Templeton (abril de 2026, marcando 5 anos do fundo), o fundo foi lançado em **abril de 2021** e utilizou a Stellar como o primeiro sistema de registro em blockchain pública para um fundo mútuo registrado nos EUA, processando transações e registrando a propriedade das cotas.

O caso possui mecanismos de controle importantes para um produto regulado, incluindo:

* autorização de investidores;
* controle sobre transferências;
* congelamento de contas;
* clawback.

A Stellar informa que a liquidação das operações ocorre em aproximadamente 5 a 7 segundos.

**Nota adicional de verificação:** desde o lançamento, o BENJI deixou de ser exclusivo da Stellar — passou a estar disponível também em outras redes (Polygon, desde 2023; Arbitrum, Aptos, Avalanche e Base, desde 2024; Solana, desde 2024; Ethereum, desde 2025), com a Stellar permanecendo como a cadeia original e a que concentra a maior parte dos detentores. Essa expansão multi-chain não estava no documento original e é relevante para contextualizar o caso: ele demonstra viabilidade de blockchain pública para um produto financeiro regulado, mas não é mais um diferencial exclusivo da Stellar frente à Avalanche.

Esse caso é relevante porque demonstra uma utilização concreta de blockchain pública em uma aplicação financeira regulada.


# 28. Outros casos institucionais

A Stellar apresenta outros casos de uso envolvendo instituições e empresas.

Entre os exemplos documentados estão:

* WisdomTree;
* Franklin Templeton;
* ABN AMRO;
* MoneyGram;
* Nonco.

Os casos estão relacionados a diferentes aplicações, incluindo:

* tokenização;
* pagamentos;
* ativos digitais;
* liquidação;
* colateral.

Esses casos demonstram que a Stellar possui experiência prática em aplicações financeiras, embora cada implementação tenha arquitetura e requisitos próprios.


# 29. Governança e validadores

Na Stellar, qualquer participante pode operar um nó, mas cada nó define quais outros nós deseja considerar confiáveis.

A documentação explica que não existe uma autoridade central que determine quais votos todos os participantes precisam aceitar.

Essa estrutura diferencia a Stellar de uma rede privada tradicional.

Para um consórcio de bancos, seria necessário avaliar se a estrutura de confiança do SCP atende ao modelo de governança desejado.


# 30. Síntese da Stellar

| Aspecto                   | Resultado da pesquisa                                     |
| -------------------------- | ------------------------------------------------------------|
| Arquitetura               | Blockchain pública                                         |
| Consenso                  | Stellar Consensus Protocol                                 |
| Modelo                    | Federated Byzantine Agreement                               |
| Validadores               | Nós que participam do consenso por relações de confiança   |
| Smart contracts           | Soroban (também chamado "Stellar Smart Contracts")         |
| Linguagem                 | Rust                                                        |
| Execução                  | WebAssembly                                                 |
| EVM                       | Não                                                          |
| Solidity                  | Não é o ambiente nativo                                     |
| Foundry                   | Não é o ambiente nativo                                     |
| Privacidade               | Pública por padrão, com privacidade configurável (X-Ray, jan/2026) |
| Atomicidade               | Operações podem ser agrupadas em transações                 |
| Desempenho                | Cerca de 5 segundos, segundo documentação                   |
| Custos                    | Inclusion fee + resource fee para smart contracts            |
| Tokenização               | Forte presença                                               |
| Pagamentos                | Forte foco histórico                                         |
| Aplicações institucionais | Diversos casos documentados (Franklin Templeton/BENJI, WisdomTree, ABN AMRO, MoneyGram, Nonco) |


# 31. Relação com o projeto do Banco Inter

## 31.1 Avalanche

A Avalanche apresenta uma compatibilidade direta com a arquitetura atual do projeto.

O PoC utiliza:

```text
Solidity
+
EVM
+
Foundry
```

A Avalanche oferece suporte a esse ambiente.

Além disso, as L1s permitem:

* permissionamento;
* controle de validadores;
* controle de transações;
* controle de deploy;
* configuração da infraestrutura.

A documentação oficial apresenta inclusive mecanismos específicos para permitir ou bloquear transações por endereço.

Isso significa que uma eventual implementação na Avalanche poderia aproveitar grande parte da estrutura tecnológica já criada.


## 31.2 Stellar

A Stellar possui características relevantes para o problema financeiro, especialmente:

* pagamentos;
* tokenização;
* baixa latência;
* atomicidade;
* casos institucionais;
* mecanismos de privacidade.

Entretanto, existe uma diferença tecnológica relevante.

O projeto atual utiliza:

```text
Solidity + EVM + Foundry
```

enquanto a Stellar utiliza:

```text
Rust + WebAssembly + Soroban (Stellar Smart Contracts)
```

Portanto, a utilização da Stellar exigiria uma adaptação maior da implementação atual.


# 32. Comparação técnica das redes

A comparação abaixo não atribui pontuação. Seu objetivo é consolidar as informações encontradas durante a pesquisa.

| Característica                | Avalanche                                 | Stellar                                            |
| ------------------------------ | ------------------------------------------- | ----------------------------------------------------|
| Tipo de infraestrutura        | L1s personalizáveis                        | Blockchain pública                                  |
| Consenso                      | Snow/Snowman                                | SCP/FBA                                             |
| Validadores                   | Podem ser permissionados                    | Baseados em relações de confiança                    |
| Smart contracts               | EVM                                          | Soroban                                              |
| Linguagem principal           | Solidity                                     | Rust                                                 |
| Máquina de execução           | EVM                                          | WebAssembly                                          |
| Compatibilidade com PoC atual | Alta                                        | Baixa                                                |
| Foundry                       | Compatível                                   | Não é o ambiente nativo                              |
| Permissionamento              | Nativo em L1s                                | Não funciona como uma L1 permissionada tradicional  |
| Privacidade                   | Pode utilizar L1s permissionadas/privadas    | Pública por padrão, com privacidade configurável (X-Ray) |
| DvP                           | Casos de uso documentados                    | Pode utilizar atomicidade de transações              |
| Finalização                   | Baixa latência reportada                     | Aproximadamente 5 segundos                            |
| Taxas                         | Configuráveis em L1                          | Inclusion + resource fee                              |
| Tokenização                   | Sim (inclui BENJI, desde 2024)               | Sim (inclui BENJI, cadeia original)                   |
| Pagamentos                    | Sim                                          | Forte foco                                            |
| Casos institucionais          | Infraestrutura financeira e L1s              | Franklin Templeton, WisdomTree, ABN AMRO, MoneyGram etc. |
| Adaptação necessária ao PoC   | Menor                                        | Maior                                                 |


# 33. Registro de descarte

## 33.1 Stellar

**Status:** descartada para a próxima etapa do PoC atual.

### Motivo do descarte

O projeto estabeleceu como requisito técnico de elegibilidade a compatibilidade com o ambiente **EVM/Solidity/Foundry**, pois o PoC já possui contratos desenvolvidos nesse stack e o cronograma do projeto não contempla uma reimplementação completa em outra plataforma.

A Stellar utiliza Soroban (também chamado Stellar Smart Contracts), com desenvolvimento em **Rust** e execução em **WebAssembly**, não sendo uma rede EVM.

Assim, para utilizar a Stellar seria necessário:

* reescrever os smart contracts;
* substituir o ambiente Foundry;
* adaptar os testes;
* estudar o modelo de execução do Soroban;
* adaptar a integração do backend;
* revisar a arquitetura do PoC.

### Justificativa

O descarte ocorre por **incompatibilidade com o stack técnico definido para o PoC**, e não por ausência de capacidade para aplicações financeiras.

A pesquisa encontrou evidências de que a Stellar possui aplicações reais em:

* tokenização;
* pagamentos;
* fundos;
* ativos financeiros;
* infraestrutura institucional.

O caso Franklin Templeton, por exemplo, demonstra a utilização da Stellar em um fundo de mercado monetário registrado nos Estados Unidos — sendo, inclusive, a rede pioneira nesse tipo de aplicação (2021), ainda que o mesmo fundo tenha se expandido posteriormente para outras redes, incluindo a Avalanche.

Portanto:

> **A Stellar é tecnicamente relevante para o setor financeiro, mas foi descartada neste benchmark específico por incompatibilidade com o stack EVM/Solidity/Foundry definido para o PoC.**


# 34. Registro de continuidade

## 34.1 Avalanche

**Status:** mantida para as próximas etapas do benchmark.

### Motivos para continuidade

A Avalanche apresenta compatibilidade com:

* Solidity;
* EVM;
* Foundry;
* smart contracts já desenvolvidos pelo projeto.

Além disso, possui mecanismos de:

* permissionamento;
* controle de transações;
* controle de deploy;
* gerenciamento de validadores;
* criação de L1s próprias.

A documentação oficial confirma que uma Avalanche L1 pode utilizar permissionamento no conjunto de validadores e controles de acesso para transações e contratos.

Dessa forma, a Avalanche permanece como candidata para os testes práticos do benchmark.


# 35. O que ainda precisa ser validado

A pesquisa documental não é suficiente para concluir como as redes se comportariam no cenário específico do projeto.

Por isso, para a rede que permanecer no benchmark, deverão ser realizados testes experimentais.

## 35.1 Desempenho

Medir:

* tempo de confirmação;
* tempo de finalização;
* média;
* mediana;
* máximo;
* variação.

## 35.2 Concorrência

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
* conflitos;
* tempo de processamento.


## 35.3 Liquidação

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


## 35.4 Custos

Medir:

* custo médio;
* custo mínimo;
* custo máximo;
* variação;
* custo sob aumento de carga.


# 36. Conclusão da pesquisa 

A pesquisa analisou as redes **Avalanche e Stellar** de forma independente, considerando sua arquitetura, consenso, smart contracts, desempenho, custos, privacidade, governança e aplicações financeiras.

A **Avalanche** apresentou uma arquitetura especialmente compatível com o projeto atual devido ao suporte a EVM e Solidity e à possibilidade de criar L1s com regras de participação e validadores próprios. A existência de mecanismos de permissionamento e controle de acesso também é relevante para um cenário institucional.

A **Stellar** apresentou características relevantes para aplicações financeiras, principalmente em pagamentos, tokenização e infraestrutura institucional. A existência de casos como o Franklin OnChain U.S. Government Money Fund demonstra uma aplicação concreta e pioneira da rede em um produto financeiro regulado.

Apesar disso, a Stellar foi registrada como **descartada para o PoC atual** devido à incompatibilidade com o stack tecnológico definido pelo projeto. Seus smart contracts (Soroban) utilizam Rust e WebAssembly, enquanto o projeto foi desenvolvido em Solidity, EVM e Foundry.

A Avalanche, por sua vez, permanece como candidata para a etapa prática.

Assim, o resultado da pesquisa é:

```text
┌──────────────────────────────────────────────┐
│              PESSOA C                        │
├──────────────────────────────────────────────┤
│ Avalanche                                    │
│ → Pesquisada                                 │
│ → Compatível com EVM/Solidity/Foundry        │
│ → Mantida para benchmark                     │
├──────────────────────────────────────────────┤
│ Stellar                                      │
│ → Pesquisada                                 │
│ → Forte atuação financeira                   │
│ → Rust/WASM/Soroban                          │
│ → Descartada por incompatibilidade com PoC  │
└──────────────────────────────────────────────┘
```

# 37. Referências

## Avalanche

**Avalanche Builder Hub.** Avalanche L1s e documentação técnica.
https://build.avax.network/

**Avalanche Builder Hub.** Blockchain Permissioning.
https://build.avax.network/academy/avalanche-l1/permissioned-l1s/02-proof-of-authority/01-blockchain-permissioning

**Avalanche Builder Hub.** Policy enforced by the protocol (Compliance).
https://build.avax.network/solutions/compliance

**Avalanche Builder Hub.** Transaction AllowList.
https://build.avax.network/docs/avalanche-l1s/precompiles/transaction-allowlist

**Avalanche Builder Hub.** Validator Manager Contract.
https://build.avax.network/academy/avalanche-l1/permissioned-l1s/02-proof-of-authority/03-validator-manager-contract

**Avalanche Builder Hub.** Avalanche Warp Messaging.
https://build.avax.network/docs/avalanche-l1s/evm-configuration/warpmessenger

**Amores-Sesar, I.; Cachin, C.; Schneider, P.** *An Analysis of Avalanche Consensus*. 2024.
https://arxiv.org/abs/2401.02811

---

## Stellar

**Stellar Development Foundation.** Stellar Consensus Protocol.
https://developers.stellar.org/docs/learn/fundamentals/stellar-consensus-protocol

**Stellar Development Foundation.** Smart Contracts / Soroban.
https://stellar.org/soroban

**Stellar Development Foundation.** Privacy on Stellar.
https://developers.stellar.org/docs/build/apps/privacy

**Stellar Development Foundation.** Fees, Resource Limits and Metering.
https://developers.stellar.org/docs/learn/fundamentals/fees-resource-limits-metering

**Stellar Development Foundation.** Institutional Case Studies.
https://stellar.org/case-studies

**Stellar Development Foundation.** Franklin Templeton: tokenized money market fund.
https://stellar.org/case-studies/franklin-templeton

**Stellar Development Foundation.** Announcing Stellar X-Ray, Protocol 25 (jan. 2026).
https://stellar.org/blog/developers/announcing-stellar-x-ray-protocol-25

**García-Pérez, Á.; Schett, M. A.** *Deconstructing Stellar Consensus*. 2019.
https://arxiv.org/abs/1911.05145

**Kim, M.; Kwon, Y.; Kim, Y.** *Is Stellar As Secure As You Think?* 2019.
https://arxiv.org/abs/1904.13302

