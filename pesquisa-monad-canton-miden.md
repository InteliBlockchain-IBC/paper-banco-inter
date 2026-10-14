
## Protocolo de Concessão de Crédito Interfinanceiro

### Mockchain — Banco Inter

**Frente:** Pesquisa Acadêmica
**Redes pesquisadas:** Monad, Canton e Miden
**Data:** Setembro de 2026 (fontes consultadas em 29/09/2026)

# 1. Objetivo da pesquisa

Esta pesquisa analisa três redes candidatas à infraestrutura do **Protocolo de Concessão de Crédito Interfinanceiro** e responde a uma pergunta prévia: **é possível, hoje, usar cada rede no PoC do grupo?**

Seguindo as pesquisas anteriores, a **Matriz de Critérios v3.0** serve apenas como referência para identificar o que importa ao projeto. Não são atribuídas notas nesta etapa. A seção 6 indica, de forma qualitativa, como cada rede se posiciona diante dos filtros eliminatórios (Filtro A: governança identificada; Filtro B: compatibilidade EVM/Solidity/Foundry).

As três redes têm perfis muito diferentes:

| Rede | Tipo | Linguagem de contratos | Estado em set/2026 |
| --- | --- | --- | --- |
| **Monad** | Layer 1 pública, compatível com EVM | Solidity (bytecode EVM) | Mainnet em operação desde nov/2025 |
| **Canton** | Rede institucional com privacidade por sub-transação | Daml (EVM via Zenith, ainda em testnet) | Mainnet em operação; Zenith EVM em testnet permissionada |
| **Miden** | Rollup ZK com estado privado por padrão | Rust → Miden Assembly (MASM) | Testnet (v0.16, última antes da mainnet); mainnet não confirmada no momento da consulta |


# 2. Resposta direta: é possível usar cada rede?

| Rede | Pode usar no PoC? | Como | Restrições |
| --- | --- | --- | --- |
| **Monad** | **Sim, sem barreiras** | Testnet pública com faucet; RPC compatível com Ethereum; contratos Solidity e Foundry funcionam sem alteração | Rede pública e aberta: não há controle de quem participa nem privacidade |
| **Canton** | **Sim, localmente; rede compartilhada exige patrocínio** | *LocalNet* (projeto `cn-quickstart`, Docker Compose) roda uma Canton completa no computador, sem aprovação externa | DevNet/TestNet/MainNet exigem um *Super Validator* patrocinador e IP liberado em lista de permissão. Os contratos precisam ser reescritos em Daml. O caminho EVM (Zenith) ainda está em testnet permissionada |
| **Miden** | **Sim, apenas em testnet** | Testnet aberta com faucet (`midenup install testnet`); ponte de teste com Sepolia via Agglayer | Não é EVM: exige reescrita em Rust. A rede ainda não está em produção, e as APIs mudaram entre versões recentes |

**Conclusão prática:** as três redes permitem experimentação gratuita, mas só a **Monad** aceita o código atual do grupo (Solidity/Foundry) sem reescrita. A **Canton** pode ser usada localmente sem pedir permissão a ninguém; para usar a rede real é preciso patrocínio. A **Miden** só pode ser usada em ambiente de teste.


# 3. Monad

## 3.1 Visão geral

Monad é uma Layer 1 compatível com a EVM, focada em desempenho. A mainnet foi lançada em novembro de 2025, junto com o token MON. A rede mantém compatibilidade em nível de bytecode com a Ethereum, portanto contratos, carteiras e ferramentas (Foundry, Hardhat, MetaMask) funcionam sem adaptação.

## 3.2 Arquitetura e consenso

* **MonadBFT:** consenso BFT derivado da família HotStuff, com assinaturas BLS.
* **Execução paralela otimista:** transações são executadas em paralelo e reexecutadas quando há conflito de estado, preservando o resultado de uma execução sequencial.
* **Execução diferida:** o consenso ordena as transações e a execução ocorre em seguida, desacoplada.
* **Desempenho divulgado:** cerca de 10.000 TPS, blocos a cada 400 ms e finalidade inferior a 1 segundo. São números do próprio projeto e precisariam ser confirmados no teste empírico da Semana 4.

## 3.3 Validadores e governança

Os validadores fazem *stake* de MON. A participação é **aberta** (*permissionless*), e a rede não oferece mecanismo nativo para restringir quem transaciona, implanta contratos ou valida. Controle de acesso só é possível na camada da aplicação (listas de permissão dentro dos contratos).

## 3.4 Privacidade

Não há privacidade nativa. Valores, contrapartes e estado dos contratos ficam públicos, como na Ethereum. Para o caso interbancário, seria preciso manter dados sensíveis fora da cadeia (PostgreSQL) e registrar apenas *hashes* e assinaturas.

## 3.5 Atomicidade (DvP)

Como é EVM síncrona em uma única cadeia, um contrato pode transferir o token de crédito e o ativo de liquidação na mesma transação, com reversão integral em caso de falha.

## 3.6 Custos

Taxas baixas, mas sujeitas a um mercado de *gas* público. O custo varia com a demanda da rede, e o banco não teria como subsidiá-lo ou fixá-lo.

## 3.7 Relação com o PoC

É a rede de **menor custo de migração**: o código Solidity e os testes Foundry do grupo rodam como estão, bastando trocar o RPC. O ponto fraco é o mesmo das L1 públicas já analisadas: governança aberta e ausência de privacidade.


# 4. Canton

## 4.1 Visão geral

A Canton Network é uma rede voltada a instituições financeiras, desenvolvida originalmente pela Digital Asset e hoje governada pela Canton Foundation. Seu diferencial é a **privacidade por sub-transação**: cada participante recebe apenas a parte da transação que lhe diz respeito.

## 4.2 Arquitetura

* **Participantes (validators):** nós operados pelas instituições. Cada um guarda somente os contratos dos quais é parte.
* **Synchronizers:** ordenam e coordenam mensagens criptografadas entre participantes sem ver o conteúdo das transações.
* **Global Synchronizer:** synchronizer público operado por um conjunto de *Super Validators* identificados, que conecta as sub-redes (a chamada "rede de redes").
* Instituições também podem operar **synchronizers privados** e conectá-los à rede global quando for necessário interoperar.

## 4.3 Consenso, validadores e governança

A validação é feita pelas partes envolvidas em cada transação, e a ordenação é feita pelo synchronizer (BFT no Global Synchronizer). Os *Super Validators* são entidades conhecidas, e novos validadores entram por patrocínio de um *Super Validator*. Esse modelo de governança identificada é o mais próximo, entre as três redes, do exigido por uma tesouraria regulada.

## 4.4 Smart contracts: Daml e o caminho EVM (Zenith)

* **Linguagem nativa: Daml**, funcional e orientada a contratos entre partes, com permissões (*signatories*, *observers*, *controllers*) declaradas no próprio contrato.
* **Zenith:** anunciado em março de 2026 como camada de execução EVM integrada à Canton. Permite implantar Solidity sem modificação e usar Foundry/Hardhat/MetaMask. A interoperabilidade com contratos Daml é feita pela primitiva `external_call()`, que permite chamadas atômicas entre Daml e EVM.
* **Estado do Zenith:** em julho de 2026 o projeto concluiu o Milestone 1 da CIP-0091 e opera uma **testnet permissionada**. A previsão de mainnet era de cerca de 4 meses. Ainda não é uma opção madura para o PoC.
* Não foi possível confirmar em fonte primária se contratos no Zenith herdam a mesma privacidade por sub-transação dos contratos Daml. Esse ponto precisaria ser verificado antes de qualquer recomendação.

## 4.5 Privacidade

Nativa e granular: os dados de uma operação só chegam aos nós das partes envolvidas, e o synchronizer vê apenas mensagens criptografadas. Atende diretamente ao requisito de sigilo de taxas, volumes e limites de crédito.

## 4.6 Atomicidade (DvP)

Suportada nativamente: uma transação Daml pode envolver vários contratos e partes, inclusive em synchronizers diferentes, e é confirmada ou rejeitada integralmente. DvP entre instituições é um dos casos de uso centrais da rede.

## 4.7 Acesso e uso

| Ambiente | Acesso | Uso no projeto |
| --- | --- | --- |
| **Daml Sandbox / LocalNet** | Livre. `cn-quickstart` sobe via Docker Compose um Super Validator, dois validadores, carteira e Canton Coin (mínimo recomendado: 8 GB de RAM) | Viável para o PoC |
| **DevNet** | Exige *Super Validator* patrocinador, IP fixo liberado e VPN | Exige contato institucional; improvável no prazo de 5 semanas |
| **TestNet / MainNet** | Exige patrocínio e aprovação | Fora do escopo do PoC |
| **Zenith EVM** | Testnet permissionada | Depende de aprovação do projeto Zenith |

## 4.8 Relação com o PoC

É a rede mais alinhada aos critérios de **privacidade (C2)**, **DvP (C1)** e **governança identificada (Filtro A)**. Em contrapartida, **não cumpre hoje o Filtro B**: usar a Canton exigiria reescrever os contratos em Daml ou depender do Zenith, que ainda não está em produção. Para a Semana 4, dá para rodar um teste em LocalNet, mas os resultados medem um ambiente local, não a rede real.


# 5. Miden

## 5.1 Visão geral

Miden começou como projeto da Polygon e tornou-se independente em 2025, com captação de US$ 25 milhões liderada por a16z crypto. É um **rollup de conhecimento zero (ZK)** em que o estado é **privado por padrão**.

## 5.2 Arquitetura

* **Modelo de contas e notas:** cada conta é uma máquina de estado independente. Ativos circulam entre contas por meio de "notas", de modo semelhante a UTXOs.
* **Prova no cliente:** o usuário executa a transação localmente e gera uma prova ZK. A rede verifica apenas a prova, sem ver o estado privado.
* **Contas e notas públicas ou privadas:** em notas privadas, o operador guarda somente um *commitment*, e os detalhes precisam ser enviados à contraparte fora da cadeia.
* **Miden VM:** máquina virtual própria, baseada em pilha. Contratos são escritos em Rust e compilados para Miden Assembly (MASM).
* **Interoperabilidade:** ponte via Agglayer; a testnet já conecta com Sepolia.

## 5.3 Estado atual

* Testnet v0.16 é descrita pelo projeto como "a última grande versão de testnet antes da mainnet", já com taxas de rede (cerca de um centésimo de centavo por transação, com taxas de mainnet previstas em USDC).
* A mainnet estava prevista inicialmente para o 4º trimestre de 2025 e foi adiada para 2026. **Não foi encontrada confirmação de mainnet em operação até a data da consulta.**
* As APIs mudaram de forma relevante entre versões recentes (v0.13 a v0.16), o que aumenta o risco para um projeto curto.

## 5.4 Privacidade

É o ponto mais forte da rede: estado e transações privados por padrão, com verificação por prova ZK. Atende conceitualmente ao requisito de sigilo. Por outro lado, a troca de notas privadas fora da cadeia cria uma nova responsabilidade operacional para a aplicação.

## 5.5 Atomicidade (DvP)

O modelo de notas é **assíncrono**: uma conta emite uma nota e outra a consome em uma transação posterior. Trocas atômicas são possíveis com notas de *swap* (a nota só pode ser consumida se entregar o ativo de contrapartida), e a testnet v0.15 adicionou swaps nativos de tokens. Ainda assim, isso não equivale à composição síncrona em uma única transação avaliada pela matriz.

## 5.6 Governança e validadores

Na fase atual, o operador (sequenciador e produtor de blocos) é centralizado no próprio projeto. Não há, nas fontes consultadas, um modelo de permissionamento institucional (listas de permissão de participantes ou validadores) comparável ao da Canton ou da Avalanche L1.

## 5.7 Relação com o PoC

É uma **referência tecnológica relevante para privacidade**, mas pouco viável como infraestrutura do PoC atual: não é EVM (falha o Filtro B), exige reescrita em Rust, não tem mainnet confirmada e usa um modelo de liquidação assíncrono.


# 6. Posicionamento qualitativo frente à Matriz v3.0

*Sem atribuição de notas: indica apenas a direção de cada rede em relação aos critérios.*

| Aspecto | Monad | Canton | Miden |
| --- | --- | --- | --- |
| **Filtro A — Governança identificada** | Não atende (validadores abertos) | Atende (Super Validators identificados; patrocínio) | Não atende hoje (operador centralizado, sem modelo institucional) |
| **Filtro B — EVM / Solidity / Foundry** | Atende plenamente | Não atende hoje (Daml); pode vir a atender com o Zenith | Não atende (Rust/MASM) |
| **C1 — DvP** | Atomicidade síncrona na EVM | Atomicidade nativa multi-parte | Assíncrona (notas); swaps possíveis |
| **C2 — Privacidade** | Nenhuma nativa | Nativa por sub-transação | Nativa por prova ZK |
| **C3 — Finalidade** | Determinística, inferior a 1 s (dado divulgado) | Determinística; depende do synchronizer | Depende da produção e da prova de blocos; sem dados de mainnet |
| **C4 — Previsibilidade de custo** | Taxas baixas, mas de mercado aberto | Modelo de tráfego pago/subsidiável por validador | Taxas muito baixas em testnet; mainnet indefinida |
| **C5 — Resiliência sob concorrência** | Testável na testnet pública | Testável apenas em LocalNet sem patrocínio | Testável apenas em testnet instável |
| **Uso no PoC em 5 semanas** | Imediato | Local apenas, com reescrita | Testnet apenas, com reescrita |

**Leitura resumida:**

* **Monad** passa no Filtro B e é trivial de testar, mas é eliminada pelo Filtro A e tem privacidade nula, na mesma situação das L1 públicas já analisadas.
* **Canton** é a mais aderente ao problema de negócio (privacidade, DvP e governança) e é eliminada apenas pelo Filtro B, por causa da stack. Se o Zenith chegar à mainnet mantendo a privacidade, ela pode se tornar a candidata mais forte para produção. Vale registrar como alternativa de roadmap na seção 6 da matriz ("Critérios que PODERIAM ser incluídos").
* **Miden** falha nos dois filtros e ainda não está em produção. Cabe na pesquisa como referência de privacidade via ZK, não como candidata.


# 7. Pontos a confirmar antes da decisão do grupo

1. Se contratos no Zenith preservam a privacidade por sub-transação da Canton ou se o estado EVM fica visível aos participantes do synchronizer.
2. Data efetiva da mainnet do Zenith e da Miden.
3. Se o grupo aceita manter a Canton na análise, mesmo reprovada no Filtro B, como "alternativa de produção", dado que ela atende melhor a C1 e C2 que qualquer candidata EVM.
4. Se o teste empírico da Semana 4 incluirá a Monad (viável) e a Canton em LocalNet (viável, mas não comparável a testnet pública).


# 8. Referências

**Monad**
* Documentação oficial — https://docs.monad.xyz/
* Site oficial — https://monad.xyz/
* Figment, *Monad First Look: Hyperscaling the EVM* — https://www.figment.io/insights/monad-first-look-hyperscaling-the-evm/
* Bankless, lançamento da mainnet — https://www.bankless.com/monad-mainnet-launches-with-airdrop-and-50-of-supply-locked

**Canton**
* Canton Network — Developer Resources — https://www.canton.network/developer-resources
* Canton Network Docs — SDKs e ferramentas — https://docs.canton.network/sdks-tools/overview
* `cn-quickstart` (LocalNet) — https://github.com/digital-asset/cn-quickstart
* Splice — Validator Onboarding — https://docs.dev.sync.global/validator_operator/validator_onboarding.html
* Canton Network, *How to get started with a validator* — https://www.canton.network/blog/how-to-get-started-with-a-validator-on-canton
* *Polyglot Canton* (whitepaper) — https://www.canton.network/hubfs/Canton%20Network%20Files/whitepapers/Polyglot_Canton_Whitepaper_11_02_25.pdf
* CIP-0091 (Zenith) — https://github.com/canton-foundation/cips/blob/main/cip-0091/cip-0091.md
* Zenith EVM Docs — https://docs.zenith.network/zenith-evm
* Anúncio do Zenith (mar/2026) — https://www.globenewswire.com/news-release/2026/03/09/3252106/0/en/zenith-launches-as-the-evm-layer-for-canton-network-merging-ethereum-s-developer-ecosystem-into-wall-street-s-blockchain.html

**Miden**
* Documentação oficial — https://docs.miden.xyz/builder/
* Testnet v0.16 — https://www.miden.xyz/blog/testnet-v0-16
* Testnet v0.15 — https://www.miden.xyz/blog/testnet-v0-15
* Polygon, captação de US$ 25M — https://polygon.technology/blog/miden-raises-25m-from-a16z-crypto-1kx-and-hackvc-to-build-the-edge-blockchain
* The Block, spin-off da Polygon — https://www.theblock.co/post/352342/polygon-miden-funding-blockchain
