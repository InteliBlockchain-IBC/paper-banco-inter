# Roteiro de medição

**Projeto:** Protocolo de concessão de crédito interfinanceiro (Mockchain)
**Trilha:** Pesquisa Acadêmica
**Entrega do cronograma:** Roteiro de medição (Semana 4)
**Versão:** v2.1, 22/10/2026 (v2 de 14/10/2026). Conferida contra o código do time de Web3 (commit `3347bf2`, 12/10/2026) [R13]

> **v2.1 (22/10/2026):** o roteiro vale para as três testnets públicas: Ethereum Sepolia, Avalanche Fuji e Monad.

---

## O que mudou na v2

| Ponto | v1 | v2 |
|---|---|---|
| Nomes das funções | Provisórios | Nomes reais do código (seção 2.1) |
| `approve` | "Se existir, entra no ciclo" | Existe, é assinado pelo ofertante; um por ciclo no valor exato (decisão A) |
| Ciclo completo | Ofertar + Aceitar | `approve` + `createOffer` + `acceptOffer` (seção 2.2) |
| Limite do tomador | "Alto o bastante" | É consumido a cada aceite e não volta sozinho; regra de cálculo na seção 4.1 |
| Validade das ofertas | Não tratada | Janela de 24 h em todas as redes (decisão B) |
| Contas | Banco A e Banco B | Admin, ofertante e tomadores, todos cadastrados pelo script de implantação (seção 4.1) |
| Ponto de partida | Não tratado | Implantação nova e mesma configuração em todas as redes (decisão B) |
| Classificação de falhas | Pelo momento do erro | Pelo nome do erro (seção 5) |
| Horário de envio | Não especificado | Registrado no envio real, depois da estimativa de gas (seção 3.2) |
| Complexidade | Regra genérica com `require` | Só o código da equipe em `src/`, regra de contagem fechada (decisão C) |
| C5 "sem alteração" | Genérico | Mesmo código e mesma configuração de compilação (decisão D) |
| Infraestrutura | 2 instituições | 2 instituições + admin (decisão E) |

---

## 0. Como ler este roteiro

Este documento define, antes de qualquer teste rodar, quatro coisas: o que será medido em cada rede, quantas vezes, como cada dado é registrado e como os números viram notas na matriz de decisão. Ele existe para que as três pessoas meçam do mesmo jeito. Se cada pessoa medir de um jeito diferente, os números das redes deixam de ser comparáveis.

Três marcações aparecem ao longo do texto:

| Marcação | Significado |
|---|---|
| **[DECIDIDO]** | Decisão aprovada pela equipe em 14/10 (letras A a E, seção 13.1). |
| **[PROPOSTA]** | Decisão sugerida neste roteiro, ainda para aprovar (seção 13.2). |
| **[CONFERIR]** | Depende do que a equipe descobriu sobre a Monad (INTER-11) ou de confirmação na INTER-15. |

**Prazo:** a entrega original deste roteiro era 11/10 e o artigo fecha em 17/10. A seção 11 traz uma versão reduzida para o caso de faltar tempo.

Termos técnicos estão explicados no texto e reunidos no Glossário, no final.

---

## 1. Escopo

### 1.1 O que é medido e o que é declarado

- **Medido:** número obtido pela própria equipe, rodando testes ou analisando o código.
- **Declarado:** informação tirada da documentação oficial da rede ou de uma publicação, sempre com a fonte registrada.

| Critério | Peso | Origem do dado | Como é obtido | Seção |
|---|---|---|---|---|
| C1. Resiliência (taxa de sucesso sob carga) | 29,78% | Medido | Teste T2 | 3.1 |
| C2. Segurança do contrato | 29,78% | (três medidas abaixo) | | 8.3 |
| C2-M1 Verificação formal | dentro de C2 | Declarado | Documentação das ferramentas de verificação | 8.2 |
| C2-M2 Complexidade do código | dentro de C2 | Medido | Análise do código do contrato | 3.4 |
| C2-M3 Confidencialidade | dentro de C2 | Declarado | Documentação da rede | 8.2 |
| C3. Latência | 15,78% | Medido | Teste T1 | 3.2 |
| C4. Custo | 15,78% | (duas medidas abaixo) | | 8.3 |
| C4-M1 Taxa por transação | dentro de C4 | Medido | Teste T1 | 3.3 |
| C4-M2 Custo de infraestrutura | dentro de C4 | Declarado | Requisitos de hardware e preço de servidor em nuvem | 8.4 |
| C5. Compatibilidade EVM | 8,88% | Declarado, confirmado na implantação | Documentação e tentativa real de implantar o contrato | 8.2 |

Além dos critérios, o roteiro registra o **modelo de finalidade** de cada rede (seção 3.5). Ele não recebe nota. Serve para interpretar a latência no texto do artigo.

### 1.2 Ambientes de teste

| Rede | Ambiente | Responsável | Observação |
|---|---|---|---|
| Ethereum | Testnet Sepolia | Pessoa A (INTER-11) | Um bloco a cada 12 s. O contrato já está implantado e verificado lá desde 05/10, mas os testes usam uma implantação nova (decisão B) |
| Avalanche | Testnet da C-Chain (Fuji) | Pessoa A (INTER-11) | [CONFERIR] endereço de RPC e faucet |
| Monad | Testnet pública | Pessoa A (INTER-11) | [CONFERIR] se a testnet está disponível; se não estiver, seguir a seção 10 |

O que significam os termos da tabela:

- **RPC:** endereço do servidor que recebe as transações enviadas pelo script e responde consultas sobre a rede.
- **Faucet:** site que distribui gratuitamente tokens de testnet, usados para pagar as taxas nos testes.

**Observação para o artigo:** o README do repositório diz que as operações fora do ambiente local devem usar "exclusivamente a testnet Sepolia" (RNF01). O protocolo continua rodando só na Sepolia. As implantações nas outras redes servem apenas ao experimento de comparação, com ativos simulados, e o artigo deve dizer isso.

---

## 2. Funções do contrato e ciclo de operação

### 2.1 Funções medidas

Fonte: `src/CreditInterbankOffer.sol`, `src/interfaces/ICreditInterbankOffer.sol` e `docs/guia-integracao.md` [R13].

| Etapa | Função no código | Quem assina | Requisito do TAP | O que faz | Critérios que alimenta |
|---|---|---|---|---|---|
| Autorizar | `BRLToken.approve(CreditInterbankOffer, valor)` | Ofertante | Pré-requisito do RF03 | Autoriza o contrato de ofertas a mover o BRLt do ofertante. Sem isso, o aceite falha com `ERC20InsufficientAllowance` | C4-M1 |
| Ofertar | `createOffer(borrower, amount, rateCDI, term, validityWindow)` | Ofertante | RF01 e RF02 | Grava a oferta, dirigida a um tomador específico. Recusa se o limite do tomador for menor que o valor | C4-M1 |
| Aceitar | `acceptOffer(offerId)` | Tomador da oferta | RF02 e RF03 | Na mesma transação: checa e consome o limite do tomador, transfere o BRLt do ofertante para o tomador e emite o NFT de posição para o ofertante (DvP). Se uma parte falhar, tudo é desfeito | C1, C3, C4-M1 (função principal) |
| Cancelar | `cancelOffer(offerId)` | Ofertante | RF06 | Cancela a oferta antes do aceite | C4-M1, só como dado descritivo (fora da matriz) |

**Eventos** (avisos que o contrato publica e que o backend lê):

| Função | Eventos emitidos |
|---|---|
| `createOffer` | `OfferCreated` |
| `acceptOffer` | `OfferAccepted` e `OfferSettled`, na mesma transação, além das transferências dos dois tokens |
| `cancelOffer` | `OfferCancelled` |

**Fora da medição:** o contrato também tem `rejectOffer` (o tomador recusa a oferta) e `expireOffer` (registra o vencimento). Nenhuma das duas faz parte dos requisitos medidos.

**Por que Aceitar é a função principal:** é nela que acontece a liquidação atômica (DvP), que é o que o protocolo existe para fazer. Ela alimenta latência e resiliência. No custo, porém, entra o ciclo inteiro (seção 2.2).

### 2.2 Ciclo completo [DECIDIDO A]

**Ciclo completo = `approve` (no valor exato da oferta) + `createOffer` + `acceptOffer`.**

O padrão ERC-20 exige que o dono dos tokens autorize o contrato antes que ele possa movê-los [R9]. Uma autorização pode cobrir várias operações, mas a equipe decidiu usar uma autorização por ciclo, no valor exato, porque esse é o fluxo usado na demonstração do README e no exemplo do guia de integração [R13].

**Referência real (demonstração na Sepolia, 06/10/2026)** [R12]:

| Transação | Gas usado | Parte do ciclo |
|---|---|---|
| `approve` | 46.361 | 10,2% |
| `createOffer` | 237.009 | 52,0% |
| `acceptOffer` | 172.050 | 37,8% |
| **Ciclo completo** | **455.420** | **100%** |

Ofertar custa mais que Aceitar porque grava a oferta inteira no armazenamento do contrato. Por isso a matriz usa o custo do ciclo, e não só o do aceite. Esses números são de uma única execução e servem só como referência; os valores do artigo vêm do T1.

---

## 3. Métricas

### 3.1 C1: taxa de sucesso sob carga

```
taxa de sucesso = transações confirmadas ÷ (transações submetidas − falhas das categorias A, B e C) × 100
```

| Item | Valor |
|---|---|
| Unidade | % |
| Sentido | Benefício (quanto maior, melhor) |
| Teste | T2 (seção 4.3) |
| Base | Métricas de desempenho do Hyperledger PSWG, que incluem o tratamento de transações que falham [R2] |

**Por que as categorias A, B e C saem da conta:** são falhas causadas pelo preparo do teste, pelo nosso próprio script ou pelo provedor de RPC. Elas não dizem nada sobre a rede. Só as falhas da categoria D (a rede não incluiu a transação) contam contra a rede. As categorias estão na seção 5.

### 3.2 C3: latência

```
latência = horário do recibo − horário de envio
```

| Item | Valor |
|---|---|
| Unidade | segundos |
| Sentido | Custo (quanto menor, melhor) |
| Teste | T1 (seção 4.2), transação `acceptOffer` |
| Base | O Hyperledger PSWG define latência de transação como o tempo de confirmação menos o tempo de submissão [R2] |

Explicação dos termos:

- **Recibo (receipt):** resposta da rede confirmando que a transação foi incluída em um bloco. Esse é o momento que o projeto definiu como "confirmação" no RNF02.
- **Mesmo relógio:** os dois horários são lidos na máquina que roda o script. Misturar o relógio da máquina com o horário do bloco introduz diferenças entre relógios que não têm a ver com a rede.

**Quando registrar o horário de envio:** as ferramentas de envio costumam estimar o gas antes de mandar a transação, quando o limite de gas não é informado, e essa estimativa já executa a transação no servidor de RPC. O horário de envio deve ser registrado no momento em que a transação assinada é de fato enviada à rede, depois da estimativa. Caso contrário, a latência inclui o tempo da estimativa, que não é tempo da rede. Isso segue a definição do PSWG, que conta a partir da submissão [R2].

**O que a medição não cobre:** a janela de 30 s do RNF02 inclui três etapas: inclusão no bloco, leitura do evento `OfferSettled` pelo backend e atualização da tela. A medição cobre só a primeira, porque as outras duas dependem da aplicação e não da rede.

**Inclusão não é o mesmo que finalidade:** na Ethereum, a transação entra em um bloco antes de se tornar definitiva. Por isso o modelo de finalidade de cada rede é registrado à parte (seção 3.5).

As latências do teste de carga (T2) também são registradas e reportadas como "latência sob carga", mas não entram na matriz.

### 3.3 C4-M1: taxa por transação

**O problema:** tokens de testnet não têm valor de mercado, e o preço do gas na testnet não reflete o preço na rede principal (mainnet). Usar a taxa paga na testnet daria um custo artificial.

**Gas** é a unidade que mede quanto trabalho computacional uma transação exige. A taxa paga é, de forma simplificada, o gas usado multiplicado pelo preço de cada unidade de gas [R3].

**[PROPOSTA] Redes EVM (Ethereum, Avalanche, Monad):**

```
custo = gas usado (medido na testnet) × preço de referência do gas na mainnet × cotação do token nativo
```

| Componente | De onde vem |
|---|---|
| Gas usado (`gasUsed`) | Lido do recibo de cada transação no teste T1 |
| Preço de referência do gas | Mediana do preço na mainnet durante a janela de coleta, de uma fonte pública (explorador oficial ou serviço de preço de gas), com data e hora registradas |
| Cotação do token nativo | Mesma fonte de cotação para todos os tokens, em USD, com data e hora. Conversão para BRL opcional, com a cotação do dia |

Premissa a declarar no artigo: a mesma operação consome a mesma quantidade de gas na testnet e na mainnet da mesma rede, porque as duas seguem as mesmas regras de cobrança. [CONFERIR] essa premissa para a Monad na documentação oficial.

**O que é reportado:** custo por função (`approve`, `createOffer`, `acceptOffer`, `cancelOffer`) e por ciclo completo. O valor do ciclo completo é o que entra na matriz. Lazăr et al. indicam que o total de taxa paga é uma base de comparação mais robusta entre redes do que métricas isoladas [R4].

### 3.4 C2-M2: complexidade do código [DECIDIDO C]

**Medida: complexidade ciclomática de McCabe [R5].**

A complexidade ciclomática conta quantos caminhos independentes existem dentro do código. Cada ponto de decisão (um `if`, um laço) cria um caminho novo. Quanto mais caminhos, mais casos precisam ser testados e verificados.

```
M = E − N + 2P
```

- E = número de arestas (setas) do grafo de fluxo do código
- N = número de nós (blocos de instruções) do grafo
- P = número de partes desconectadas do grafo (normalmente uma por função)

Na prática, para código estruturado, McCabe mostra que o resultado equivale a **número de pontos de decisão + 1**, por função [R5].

**O que entra na contagem (decisão C: o código exato da equipe):**

| Entra | Fica fora |
|---|---|
| Os três contratos da pasta `src/`: `CreditInterbankOffer`, `BRLToken`, `CDIPositionToken` | Bibliotecas da OpenZeppelin (controle de acesso, proteção contra reentrância, padrões ERC-20 e ERC-721), porque não foram escritas pela equipe |
| | A interface `ICreditInterbankOffer`, que não tem código executável |
| | Script de implantação e testes, porque não vão para a rede |

**Regra de contagem dos pontos de decisão:**

| Conta | Não conta |
|---|---|
| Cada `if`, inclusive o padrão `if (...) revert Erro()` que o código usa no lugar de `require` | Modificadores `onlyRole` e `nonReentrant` (checagens que rodam antes da função), porque a decisão está dentro da OpenZeppelin |
| Cada `else if`, laço (`for`, `while`) e operador ternário | |
| Cada `&&` e `\|\|` dentro de uma condição, porque estão escritos no código da equipe | |

**Contagem preliminar** [CONFERIR na INTER-15]:

| Contrato | Funções | Pontos de decisão | M total |
|---|---|---|---|
| `CreditInterbankOffer` | 17 | 25 (19 `if` + 6 `&&`/`\|\|`) | 42 |
| `BRLToken` | 3 | 0 | 3 |
| `CDIPositionToken` | 4 | 0 | 4 |
| **Total (versão Solidity)** | **24** | **25** | **49** |

| Item | Valor |
|---|---|
| Unidade | número inteiro (soma de M em todas as funções) |
| Sentido | Custo (quanto maior, pior) |
| Base | Shin et al. encontraram associação entre métricas de complexidade e vulnerabilidades de software [R6] |
| Ferramenta | [CONFERIR] ferramenta automática ou contagem manual documentada (INTER-15) |

**Limitações para Ameaças à Validade:**

- Existe uma só versão do código (Solidity), a mesma nas três redes. Portanto, C2-M2 dá o mesmo valor a todas e não diferencia nenhuma. A medida fica no método porque diferenciaria uma rede que exigisse reescrever o contrato.
- Como cada função soma 1 ao total, uma versão com mais funções tem total maior mesmo sem mais decisões. Na versão Solidity, 24 dos 49 pontos vêm só do número de funções.

### 3.5 Modelo de finalidade (registro, sem nota)

**Finalidade** é o momento a partir do qual a transação não pode mais ser desfeita.

| Tipo | O que significa |
|---|---|
| Determinística (imediata) | A transação é definitiva assim que entra no bloco |
| Não imediata | A transação entra no bloco e só se torna definitiva depois de uma etapa adicional ou de um certo número de blocos |

Para cada rede, registrar o tipo e o tempo até a finalidade, com a fonte. As redes são preenchidas a partir da documentação oficial nas tarefas de dados declarados (INTER-16 e INTER-17).

---

## 4. Procedimentos

### 4.1 Preparação (igual em todas as redes) [DECIDIDO B e D]

**Por que o ponto de partida precisa ser igual:** o gas de uma mesma função muda conforme o estado anterior do contrato. Gravar em uma posição vazia do armazenamento custa mais do que alterar uma posição já preenchida [R11]. Se uma rede começar com contas e saldos diferentes de outra, o custo deixa de ser comparável.

**Passos:**

1. **Implantação nova em cada rede**, inclusive na Sepolia, com o script `script/Deploy.s.sol`. O script implanta os três contratos, dá ao contrato de ofertas a permissão de emitir o NFT, cadastra as instituições, define os limites e emite o BRLt inicial, tudo a partir de um arquivo `script/config/<rede>.json` [R13].
2. **Sem alterar o código (decisão D):** para cada rede EVM, criar só o arquivo de configuração e adicionar o endereço de RPC no `foundry.toml`. Usar o mesmo commit e a mesma configuração de compilação (Solidity 0.8.24, otimizador com 200 execuções).
3. **Contas** (as mesmas funções em todas as redes):

| Conta | Papel no contrato | O que assina nos testes |
|---|---|---|
| Admin | `DEFAULT_ADMIN_ROLE`; simula o Banco Central | Implantação, cadastro, limites, emissão de BRLt |
| Ofertante (Banco A) | Instituição cadastrada, quem empresta | `approve`, `createOffer`, `cancelOffer` |
| Tomador (Banco B) | Instituição cadastrada, quem toma | `acceptOffer` no T1 |
| Tomadores adicionais (T2) | Instituições cadastradas | `acceptOffer` no T2 (ver 4.3) |

4. **Valores fixos em todas as ofertas e em todas as redes:**

| Parâmetro | Valor | Significado |
|---|---|---|
| `amount` | 100 | R$ 1,00 (o BRLt tem 2 casas decimais, então 100 = 100 centavos) |
| `rateCDI` | 10000 | 100% do CDI (em pontos-base) |
| `term` | 1 | Overnight (1 dia) |
| `validityWindow` | 86400 | 24 h, em segundos. Precisa ser maior que a duração dos testes; se a oferta vencer antes do aceite, ele falha com `OfferHasExpired` |

5. **Limites e saldos:** o limite do tomador é consumido a cada aceite e não volta sozinho (só o admin recompõe com `setCreditLimit`). Por isso:
   - limite de cada tomador ≥ número de aceites dele × R$ 1,00;
   - saldo de BRLt do ofertante ≥ número total de aceites × R$ 1,00.
   Na versão completa são 30 aceites no T1 e 255 no T2, ou seja, R$ 285,00 saindo do ofertante. Os valores padrão do arquivo de configuração (limite de R$ 5 milhões e saldo de R$ 10 milhões por instituição) cobrem isso com folga, desde que cada tomador adicional também receba limite.
6. **Tokens nativos:** obter no faucet tokens para todas as contas que assinam transações (admin, ofertante e tomadores).
7. **Mesma ordem:** em todas as redes, rodar T1 e depois T2, na mesma sequência.
8. **Registrar os metadados** da seção 6.2 antes de começar.

**Orçamento estimado na Sepolia:** com o gas da demonstração [R12] e o preço de gas daquele dia (cerca de 1,1 gwei), T1 e T2 completos consomem cerca de 118 milhões de gas, perto de 0,13 SepoliaETH, sem contar cancelamentos e implantação. O preço na testnet varia, então o valor é só uma ordem de grandeza.

### 4.2 Teste T1: sequencial, sem carga

**Objetivo:** medir latência e custo em condição normal, uma transação por vez.

**[PROPOSTA] Por rede:**

| Etapa | Sequência | Quantidade |
|---|---|---|
| Ciclos completos | `approve` → recibo → `createOffer` → recibo → `acceptOffer` → recibo | 30 |
| Cancelamentos | `createOffer` → recibo → `cancelOffer` → recibo (sem `approve`, porque o cancelamento não move tokens) | 10 |

**Gera:** latência do `acceptOffer` (C3), gas e taxa de cada função (C4-M1) e eventuais falhas.

**Tempo estimado na Sepolia:** cada transação leva pelo menos um bloco (12 s). Ciclos: 30 × 3 × 12 s = no mínimo 18 min. Cancelamentos: 10 × 2 × 12 s = no mínimo 4 min.

**Sobre o número 30:** não existe referência que fixe esse número para este tipo de teste. Ele é uma escolha da equipe, que cabe na janela de tempo e permite calcular mediana e percentil 95. Deve ser declarado no artigo como escolha.

### 4.3 Teste T2: carga simultânea

**Objetivo:** medir a taxa de sucesso (C1) quando muitas transações de aceite chegam ao mesmo tempo.

**Preparação (fora da medição):**

1. **Um único `approve`** do ofertante, no valor total dos aceites do T2 (255 × R$ 1,00 = 25.500 centavos) [DECIDIDO A].
2. **Criar as 255 ofertas antes**, cada uma já dirigida à conta tomadora que vai aceitá-la, porque só o tomador indicado na oferta pode aceitar.
3. Enviar as ofertas com controle de nonce, sem esperar cada recibo. Uma de cada vez, esperando o recibo, levaria no mínimo 255 × 12 s = 51 min na Sepolia.

**Medição:**

1. **[PROPOSTA]** Enviar lotes de 10, 25 e 50 transações `acceptOffer` ao mesmo tempo, em 3 rodadas por tamanho de lote. Total: (10 + 25 + 50) × 3 = 255 aceites por rede.
2. Tempo limite de 5 min: transação não incluída em um bloco nesse tempo conta como não confirmada (categoria D).
3. Usar várias contas tomadoras ou controlar o nonce explicitamente. O **nonce** é um número sequencial de cada conta: a rede só aceita a transação de número n depois da n − 1. Se o script mandar duas transações com o mesmo nonce, uma é descartada, e isso é erro do script, não da rede [R4]. O número de contas tomadoras usado vai para os metadados.

**Por que lotes de 10, 25 e 50:** Javed et al. observaram na Sepolia que 30 a 50 transações simultâneas ocupam de 80% a 90% do limite de gas do bloco e quase dobram o tempo até a finalização [R7]. Os três lotes ficam abaixo, dentro e no topo dessa faixa.

**Limites desse desenho, para declarar no artigo:**

- Em redes com blocos maiores ou mais rápidos, 50 transações podem não gerar carga. O resultado deve ser descrito como "taxa de sucesso com até 50 transações simultâneas", e não como capacidade máxima da rede.
- As testnets públicas são compartilhadas com outros usuários e o tráfego varia. Para que as condições fossem parecidas, as três foram coletadas na mesma janela.

### 4.4 Janela de coleta

- Todas as redes testadas no mesmo dia, se possível.
- Horários registrados em UTC (horário universal, sem fuso), para evitar confusão entre fusos.
- Mesma máquina e mesma região de rede para todos os testes.
- Mesmo tipo de RPC para todas as redes (todos públicos gratuitos ou todos de provedor pago).
- Registrar início e fim de cada rodada.

---

## 5. Classificação de falhas

Toda transação que não for confirmada recebe uma categoria. **Só a categoria D conta contra a rede em C1.**

**A categoria é decidida pelo nome do erro, e não pelo momento em que ele aparece.** Como as ferramentas de envio estimam o gas antes de enviar (seção 3.2), um erro do contrato pode aparecer antes de a transação ter hash, e não só no recibo.

| Categoria | O que é | Como reconhecer | O que fazer |
|---|---|---|---|
| A. Erro do contrato ou do token | O contrato ou o token recusou a operação por uma regra dele | Qualquer erro definido no código: `InsufficientLimit`, `OfferHasExpired`, `InvalidOfferStatus`, `NotEligibleBorrower`, `NotOfferOwner`, `NotRegisteredInstitution`, `InvalidOfferParameters`, `InvalidValidityWindow`, `InvalidCounterparty`, `OfferNotFound`, `ERC20InsufficientAllowance`, `ERC20InsufficientBalance`, `ReentrancyGuardReentrantCall` [R13] | Corrigir o preparo e repetir. Fica fora de C1 |
| B. Erro do cliente de teste | Erro do nosso script: nonce repetido, saldo de token nativo insuficiente para a taxa, assinatura errada, limite de gas baixo demais | Mensagens do nó como "nonce too low", "insufficient funds" ou falta de gas (out of gas) | Corrigir, excluir do denominador e registrar à parte |
| C. Rejeição do provedor de RPC | O servidor de RPC recusou a requisição, por exemplo por limite de requisições | Erro HTTP do provedor, como o código 429 (muitas requisições) | Não conta. Declarar como limitação |
| D. Falha da rede | A transação foi aceita pelo RPC (recebeu um hash), mas foi descartada ou não entrou em bloco dentro do tempo limite | Sem recibo após 5 min, ou transação descartada | Conta em C1 |

Base: Lazăr et al. mostraram que falhas por reutilização de nonce vinham do cliente de teste, e não da rede [R4]. Sem essa separação, a taxa de sucesso mediria a qualidade do script, e não a rede.

---

## 6. Registro de dados

### 6.1 Uma linha por transação (arquivo CSV)

**[PROPOSTA]** Nome do arquivo: `medicoes_<rede>_<data>.csv`.

| Coluna | Conteúdo |
|---|---|
| rede | Nome da rede |
| teste | T1 ou T2 |
| lote | Tamanho do lote (T2) ou vazio (T1) |
| rodada | Número da rodada |
| funcao | `approve`, `createOffer`, `acceptOffer` ou `cancelOffer` |
| conta | Endereço da conta que assinou |
| offer_id | Número da oferta (vazio no `approve`) |
| tx_hash | Identificador da transação na rede (vazio se o erro veio antes do envio) |
| t_envio_utc | Horário do envio real, depois da estimativa de gas, em UTC, com milissegundos |
| t_recibo_utc | Horário do recibo, em UTC, com milissegundos |
| latencia_s | t_recibo_utc − t_envio_utc, em segundos |
| bloco | Número do bloco em que a transação entrou |
| status | Confirmada ou falha |
| etapa_erro | Estimativa, envio ou recibo (vazio se confirmada) |
| nome_erro | Nome do erro (por exemplo `OfferHasExpired`) ou mensagem do nó |
| categoria_falha | A, B, C, D ou vazio |
| gas_used | Gas usado, lido do recibo |
| gas_price_testnet | Preço do gas pago na testnet (só registro, não entra no custo) |
| taxa_nativa | Taxa paga, em token nativo da testnet (só registro) |

### 6.2 Metadados por rede (registrados uma vez)

- Data e janela de horário da coleta (UTC)
- Endereço de RPC e tipo (público ou provedor pago)
- Máquina e região de onde os testes foram rodados
- Endereços dos três contratos implantados e o bloco da implantação
- Commit do código, versão do compilador (Solidity 0.8.24), configuração do otimizador (200 execuções) e versão da OpenZeppelin (5.4.0)
- Arquivo `script/config/<rede>.json` usado
- Endereços das contas (admin, ofertante, tomadores) e número de contas tomadoras no T2
- Versão do cliente da rede, quando o RPC informa
- Preço de referência do gas e cotação do token, com fonte, data e hora

---

## 7. Estatísticas e valor que entra na matriz

Termos usados:

- **Média:** soma dos valores dividida pela quantidade.
- **Mediana:** valor do meio quando os resultados são ordenados. É menos afetada por uma única transação muito lenta.
- **Percentil 95 (p95):** valor abaixo do qual estão 95% dos resultados. Com 30 amostras, é uma estimativa aproximada.

**[PROPOSTA]**

| Critério | O que é reportado no artigo | O que entra na matriz |
|---|---|---|
| C3. Latência | Média, mediana, p95 e máximo do `acceptOffer` no T1; latência sob carga do T2; proporção de aceites incluídos em até 30 s | Mediana do `acceptOffer` no T1 |
| C4-M1. Taxa por transação | Custo de cada função e do ciclo | Média do ciclo completo (`approve` + `createOffer` + `acceptOffer`), em USD |
| C1. Resiliência | Taxa por tamanho de lote e por rodada | Taxa agregada de todas as rodadas do T2 |
| C2-M2. Complexidade | Valor por função e total | Total da versão do código usada na rede |

**Por que o máximo da latência é reportado:** o RNF02 é um limite máximo (30 s). Uma rede com mediana baixa mas com algumas transações muito lentas pode descumprir o requisito, e isso precisa aparecer no texto. A proporção de aceites incluídos em até 30 s é indicativa, porque a janela do RNF02 também inclui backend e tela (seção 3.2).

---

## 8. Notas: do dado bruto para uma nota de 0 a 1

### 8.1 Normalização min-max

Cada critério tem uma unidade diferente (segundos, dólares, porcentagem). A normalização converte tudo para uma escala de 0 a 1, em que 1 é sempre o melhor.

```
Critério de benefício (maior é melhor):  r = (x − mín) ÷ (máx − mín)
Critério de custo (menor é melhor):      r = (máx − x) ÷ (máx − mín)
```

**Exemplo com números hipotéticos:** latências de 2 s, 5 s e 12 s (custo, menor é melhor).

| Rede | x | Cálculo | Nota |
|---|---|---|---|
| Rede 1 | 2 s | (12 − 2) ÷ (12 − 2) | 1,0 |
| Rede 2 | 5 s | (12 − 5) ÷ (12 − 2) | 0,7 |
| Rede 3 | 12 s | (12 − 12) ÷ (12 − 2) | 0,0 |

**[PROPOSTA] Empate:** se todas as redes tiverem o mesmo valor (máx = mín), a fórmula dividiria por zero. Nesse caso, todas recebem 1, porque ninguém deve ser penalizado em um critério em que todos são iguais.

**Atenção para C2-M2:** com uma só versão do código, as três redes empatam e recebem 1 (regra de empate). Isso deve ser comentado na Discussão.

**Lista de redes fechada antes do cálculo:** a normalização min-max depende do menor e do maior valor do conjunto. Incluir ou retirar uma rede muda as notas de todas as outras e pode inverter a ordem entre elas. Belton e Gear (1983) mostraram esse efeito, chamado de inversão de ranking, em métodos em que a nota depende do conjunto de alternativas [R10]. Por isso, a lista de redes é fechada antes de qualquer nota ser calculada.

### 8.2 Escalas dos critérios declarados

**[PROPOSTA]** Para cada nota atribuída, registrar a fonte usada.

**C5. Compatibilidade EVM** [DECIDIDO D para a definição de "sem alteração"]

| Nível | Nota | Significado |
|---|---|---|
| Sem alteração | 1,0 | O mesmo código (mesmo commit) compila com a mesma configuração (Solidity 0.8.24, otimizador com 200 execuções) e é implantado com sucesso. Arquivo de configuração de implantação e endereço de RPC novos não contam como alteração |
| Compilador modificado | 0,5 | Exige outra versão ou outra configuração de compilação, ou mudanças no código |
| Reescrita | 0,0 | Exige reescrever o contrato em outra linguagem |

**C2-M1. Verificação formal** (existência de ferramentas que provam matematicamente que o contrato faz o que deveria)

| Nível | Nota | Significado |
|---|---|---|
| Alto | 1,0 | Ferramenta com documentação oficial ou publicação revisada por pares, e manutenção ativa |
| Médio | 0,5 | Ferramenta experimental, sem manutenção ativa ou limitada a uma função |
| Baixo | 0,0 | Nenhuma ferramenta disponível |

**C2-M3. Confidencialidade** (quem consegue ver os dados das transações)

| Nível | Nota | Significado |
|---|---|---|
| Alto | 1,0 | Cada participante vê só as transações de que faz parte |
| Médio | 0,5 | Rede permissionada (só participantes autorizados entram), mas todos os participantes veem tudo |
| Baixo | 0,0 | Rede pública: qualquer pessoa vê todas as transações |

Evidência do próprio projeto para a Sepolia: o guia de integração registra que, na Sepolia, qualquer pessoa lê os eventos, e que esconder as ofertas encerradas é feito só na aplicação [R13]. Os eventos `OfferCreated` e `OfferSettled` trazem as partes, o valor e a taxa.

As notas de cada rede nessas escalas são atribuídas nas tarefas de dados declarados (INTER-16 e INTER-17), com fonte.

### 8.3 Como as medidas de um mesmo critério se juntam

**[PROPOSTA]** Depois da normalização, todas as medidas estão na escala de 0 a 1 em que 1 é melhor. Por isso, uma média simples funciona:

```
C2 = (C2-M1 + C2-M2 + C2-M3) ÷ 3      (C2-M2 normalizada como custo)
C4 = (C4-M1 + C4-M2) ÷ 2              (as duas normalizadas como custo)
```

Alternativa descartada por causa do prazo: dar pesos diferentes às medidas internas usando AHP, como foi feito com os critérios. Isso deve ser declarado no artigo como limitação.

### 8.4 Cenário de infraestrutura (C4-M2) [DECIDIDO E]

Cenário: três participantes operando o protocolo, os mesmos dos testes: duas instituições (ofertante e tomador) e o admin, que simula o Banco Central.

| Rede | Nós considerados |
|---|---|
| Ethereum, Avalanche, Monad | **[PROPOSTA]** 1 nó próprio por participante (3 no total) |

**Procedimento:**

1. Ler os requisitos mínimos de hardware na documentação oficial de cada rede.
2. Escolher a instância (servidor alugado) mais barata que atende esses requisitos, no mesmo provedor de nuvem e na mesma região para todas as redes.
3. Calcular:

```
custo mensal = preço por hora × 730 × número de nós
```

730 é o número médio de horas em um mês (8.760 horas no ano ÷ 12).

4. Registrar provedor, instância, preço e data da consulta.

---

## 9. Análise de sensibilidade

**O que é:** testar se o ranking muda quando os pesos mudam. Se a rede em primeiro lugar continuar em primeiro mesmo com pesos diferentes, o resultado é robusto. Se mudar com pouca variação, isso precisa ser dito no artigo. Base: Triantaphyllou e Sánchez [R8].

**[PROPOSTA] Cenários:**

| Cenário | O que muda | Quantidade |
|---|---|---|
| S1 | Todos os pesos iguais (20% cada) | 1 |
| S2 | Cada peso aumentado em 50% e depois reduzido em 50%, um de cada vez, com renormalização | 10 (5 critérios × 2) |
| S3 | Retirar um critério de cada vez, com renormalização | 5 |
| | **Total** | **16** |

**Renormalização:** depois de mudar um peso, dividir todos os pesos pela nova soma, para que voltem a somar 100%.

Exemplo (S2, latência +50%): C3 passa de 15,78% para 23,67%. A soma vira 107,89%. Dividindo cada peso por 1,0789:

| Critério | Peso original | Peso no cenário |
|---|---|---|
| C1 | 29,78% | 27,60% |
| C2 | 29,78% | 27,60% |
| C3 | 15,78% | 21,94% |
| C4 | 15,78% | 14,63% |
| C5 | 8,88% | 8,23% |

**O que reportar:** uma tabela com a posição de cada rede em cada cenário e a indicação de se o primeiro lugar mudou.

---

## 10. Plano alternativo

| Problema | O que fazer |
|---|---|
| Monad sem testnet disponível | Usar dados declarados e declarar como limitação |
| Faucet não fornece tokens suficientes | Reduzir os lotes (seção 11) |
| Muitas falhas da categoria C | Trocar o RPC para todas as redes, não só para a que falhou, e repetir |
| Muitas falhas da categoria A no T2 | Conferir limites dos tomadores, `approve` total e janela de validade (seção 4.1) e repetir a rodada |

Em todos os casos, registrar célula a célula na matriz se o dado é medido ou declarado.

---

## 11. Versão reduzida (se faltar tempo)

| Item | Versão completa | Versão reduzida |
|---|---|---|
| T1 | 30 ciclos e 10 cancelamentos | 20 ciclos, sem cancelamentos (no mínimo 12 min na Sepolia) |
| T2 | Lotes de 10, 25 e 50, 3 rodadas (255 aceites) | Lotes de 10 e 50, 2 rodadas (120 aceites) |
| Sensibilidade | S1, S2 e S3 | S1 e S2 |
| Critérios | Todos | Todos (nenhum critério é retirado) |

---

## 12. Responsáveis (Linear)

| O quê | Pessoa | Tarefa |
|---|---|---|
| Rodadas T1 e T2 em Ethereum, Avalanche e Monad | A | INTER-11 |
| Script de coleta EVM | C | INTER-10 |
| Complexidade do código | C | INTER-15 |
| Consolidação dos dados medidos | C | INTER-18 |
| Dados declarados: Ethereum, Avalanche, Monad | A | INTER-16 |
| Normalização, ranking e sensibilidade | B | INTER-21 |

---

## 13. Decisões

### 13.1 Decididas em 14/10, após a leitura do código

| | Decisão | Seções |
|---|---|---|
| A | Um `approve` por ciclo, no valor exato da oferta; no T2, um único `approve` na preparação, no valor total | 2.2, 4.3 |
| B | Ponto de partida igual em todas as redes: implantação nova, mesma configuração, R$ 1,00 por oferta, janela de validade de 24 h | 4.1 |
| C | Complexidade conta só o código exato da equipe (pasta `src/`), sem OpenZeppelin | 3.4 |
| D | "Sem alteração" em C5 = mesmo código e mesma configuração de compilação; configuração de implantação e RPC não contam | 4.1, 8.2 |
| E | O admin entra no cenário de infraestrutura, como nos testes e na captura de dados | 8.4 |

### 13.2 Ainda para aprovar

- [ ] 1. T1 com 30 ciclos; T2 com lotes de 10, 25 e 50 em 3 rodadas (4.2 e 4.3)
- [ ] 2. Custo das redes EVM com gas medido na testnet e preço da mainnet (3.3)
- [ ] 3. Classificação de falhas pelo nome do erro, com só a categoria D contando (5)
- [ ] 4. Valores na matriz: mediana da latência, média do ciclo, taxa agregada (7)
- [ ] 5. Complexidade ciclomática como medida de C2-M2 (3.4)
- [ ] 6. Escalas de C2-M1 e C2-M3, e níveis 0,5 e 0,0 de C5 (8.2)
- [ ] 7. Média simples dentro de C2 e de C4 (8.3)
- [ ] 8. Um nó por participante nas redes públicas (8.4)
- [ ] 9. Cenários de sensibilidade S1, S2 e S3 (9)

---

## Glossário

| Termo | Explicação |
|---|---|
| Testnet | Rede de testes que funciona como a rede real, mas com tokens sem valor |
| Mainnet | A rede principal, em que os tokens têm valor de mercado |
| RPC | Servidor que recebe as transações do script e responde consultas sobre a rede |
| Faucet | Site que distribui tokens de testnet de graça |
| Gas | Unidade que mede o trabalho computacional de uma transação nas redes EVM |
| Estimativa de gas | Execução da transação no servidor, sem gravar nada, para calcular quanto gas ela vai usar antes do envio |
| Recibo (receipt) | Resposta da rede dizendo que a transação entrou em um bloco, com o gas usado e o status |
| Nonce | Número sequencial de cada conta; impede que a mesma transação seja processada duas vezes |
| `approve` | Transação do padrão ERC-20 em que o dono dos tokens autoriza um contrato a movê-los |
| BRLt | Token do projeto que representa o real (fictício, só para testnet) |
| NFT de posição | Token único emitido para o ofertante no aceite; representa o direito de receber o valor emprestado |
| Evento | Aviso que o contrato publica na rede e que o backend lê |
| Modificador | Trecho de código que roda uma checagem antes de uma função (por exemplo, `onlyRole`) |
| Validador | Participante da rede que aprova os blocos |
| Finalidade | Momento em que a transação não pode mais ser desfeita |
| UTC | Horário universal, sem fuso horário |
| Mediana | Valor do meio de uma lista ordenada |
| Percentil 95 (p95) | Valor abaixo do qual estão 95% dos resultados |
| Normalização min-max | Conversão de valores com unidades diferentes para uma escala de 0 a 1 |
| Inversão de ranking | Quando incluir ou retirar uma alternativa muda a ordem das outras |
| Renormalização | Ajustar os pesos para voltarem a somar 100% |

---

## Referências

[R2] Hyperledger Performance and Scale Working Group. *Blockchain Performance Metrics*. Usado para: definições de latência e de tratamento de transações que falham.
https://www.lfdecentralizedtrust.org/learn/publications/blockchain-performance-metrics

[R3] Ethereum Foundation. *Gas and fees*. Usado para: o que é gas e como a taxa é calculada.
https://ethereum.org/developers/docs/gas

[R4] Lazăr, Secrieru, Onica (2025). arXiv:2504.10535. Usado para: falhas por reutilização de nonce vindas do cliente; total de taxa paga como base de comparação.
https://arxiv.org/abs/2504.10535

[R5] McCabe, T. J. *A Complexity Measure*. IEEE Transactions on Software Engineering, 2(4):308-320, 1976. Usado para: definição da complexidade ciclomática.
https://doi.org/10.1109/TSE.1976.233837

[R6] Shin et al. (2011). IEEE Transactions on Software Engineering. Usado para: associação entre complexidade e vulnerabilidades.
https://ieeexplore.ieee.org/document/5560680

[R7] Javed et al. (2025). arXiv:2503.01397. Usado para: efeito de 30 a 50 transações simultâneas na Sepolia.
https://arxiv.org/abs/2503.01397

[R8] Triantaphyllou, E.; Sánchez, A. (1997). *A sensitivity analysis approach for some deterministic multi-criteria decision-making methods*. Decision Sciences, 28(1). Usado para: análise de sensibilidade dos pesos.
https://doi.org/10.1111/j.1540-5915.1997.tb01306.x

[R9] Ethereum Improvement Proposals. *EIP-20: Token Standard*. Usado para: a autorização `approve` antes de um contrato mover tokens de uma conta.
https://eips.ethereum.org/EIPS/eip-20

[R10] Belton, V.; Gear, T. (1983). *On a short-coming of Saaty's method of analytic hierarchies*. Omega, 11(3):228-230. Usado para: inversão de ranking quando o conjunto de alternativas muda.
https://ideas.repec.org/a/eee/jomega/v11y1983i3p228-230.html

[R11] Ethereum Improvement Proposals. *EIP-2200: Structured Definitions for Net Gas Metering*. Usado para: gravar em uma posição vazia do armazenamento custa mais do que alterar uma preenchida.
https://eips.ethereum.org/EIPS/eip-2200

[R12] Transações da demonstração na Sepolia, 06/10/2026 (Etherscan). Usado para: gas de referência do ciclo.
- `approve`: https://sepolia.etherscan.io/tx/0xac5f8c4b2678129920ef2c91fb677d6c4d3324dc62dc9d63afe23934ecfeb3aa
- `createOffer`: https://sepolia.etherscan.io/tx/0x1fcfa5db23515922b644a39fa15cec2dc7203a5d01dddbda212025f6a911467d
- `acceptOffer`: https://sepolia.etherscan.io/tx/0xe503d1c3f1dddf19cb0de517e291be9b8be34539c0963243414899782658084f

[R13] Repositório do time de Web3, `projeto-inter-web3`, commit `3347bf2` (12/10/2026). Arquivos usados: `src/CreditInterbankOffer.sol`, `src/interfaces/ICreditInterbankOffer.sol`, `src/tokens/BRLToken.sol`, `src/tokens/CDIPositionToken.sol`, `script/Deploy.s.sol`, `script/config/sepolia.json`, `foundry.toml`, `README.md`, `docs/guia-integracao.md`, `docs/maquina-estados-oferta.md`.
https://github.com/anacampos-crypto/projeto-inter-web3
