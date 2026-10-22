# Resumo Executivo — Seleção de rede para crédito interfinanceiro overnight

> **Atualizado em 22/10/2026:** números de `pesquisa/3-resultados/resultados.md`. Limitações revisadas contra a seção 10 da matriz de critérios.

**Projeto:** Inteli Blockchain × Banco Inter · prova de conceito acadêmica, com ativos simulados e sem integração com sistemas de produção.

## Problema
A gestão de liquidez interbancária de curtíssimo prazo ainda sofre com conciliação e liquidação ineficientes: checagens manuais de limites geram atraso entre a negociação e a conclusão, o que aumenta o risco de contraparte e a complexidade do fechamento diário de caixa. A escolha da rede blockchain que sustentaria uma solução automatizada para esse crédito overnight precisa ser feita com critérios objetivos, e não por preferência técnica.

## Método
A escolha foi tratada como uma decisão multicritério: três redes públicas (Ethereum, Avalanche e Monad) foram comparadas em cinco critérios com pesos obtidos pelo método AHP, que transforma comparações par a par em pesos consistentes. Resiliência sob carga e segurança do contrato pesam 29,78% cada; latência e custo, 15,78% cada; compatibilidade com o código atual, 8,88%.

As três foram escolhidas porque executam a operação de forma atômica (condição para entregar o ativo só contra o pagamento), rodam o contrato do projeto sem reescrita e têm ambiente de teste público, o que permite medir todas nas mesmas condições. Elas cobrem perfis diferentes: a Ethereum é a rede de referência, onde o protocolo já roda; a Avalanche promete confirmação definitiva em menos de 1 segundo; e a Monad é uma rede nova voltada a alto desempenho, cujos números de divulgação o teste também verifica. Solana, Stellar e Miden ficaram de fora por exigirem reescrever o contrato.

Cada rede executou o próprio contrato do projeto (autorizar, ofertar e aceitar) na sua testnet pública: 30 operações completas em sequência e 255 aceites disparados em lotes simultâneos de 10, 25 e 50. Foram 1.095 transações no total, coletadas nas três redes na mesma janela de 16/10/2026.

| Rede | Testnet usada | Coleta |
|---|---|---|
| Ethereum | Sepolia | 16/10/2026 |
| Avalanche | Fuji (C-Chain) | 16/10/2026 |
| Monad | Testnet pública da Monad | 16/10/2026 |

## Resultados
| Posição | Rede | Tempo mediano até a confirmação | Sucesso sob carga | Custo por operação completa | Pontuação |
|---|---|---|---|---|---|
| 1 | Monad | 0,99 s | 100% | US$ 0,0014 | 90,1 |
| 2 | Avalanche | 2,64 s | 100% | US$ 0,029 | 86,0 |
| 3 | Ethereum | 11,04 s | 100% | US$ 0,30 | 58,5 |

As três redes confirmaram todas as operações, inclusive com 50 aceites simultâneos, e nas operações em sequência todas ficaram abaixo do limite de 30 segundos do projeto. A Ethereum, porém, só torna a operação definitiva cerca de 13 minutos depois. O custo foi convertido pelos preços da rede principal de cada blockchain em 16/10/2026.

**Rede recomendada pela matriz:** Monad. Foi a mais rápida (menos de 1 segundo até a confirmação) e a mais barata (cerca de um vigésimo do custo da Avalanche e um duzentos-avos do custo da Ethereum por operação completa), e roda o contrato atual sem nenhuma alteração.

**Alternativa próxima:** Avalanche, 4,1 pontos atrás. Também roda o contrato sem alteração, confirma em menos de 3 segundos e custa cerca de US$ 0,03 por operação completa.

## Robustez da recomendação (análise de sensibilidade)
O ranking foi refeito em 16 variações de pesos. A ordem Monad, Avalanche e Ethereum se mantém em todos os 17 cenários. Isso tem um motivo que precisa ficar claro: as três redes empataram em resiliência (100% de sucesso), segurança do contrato e compatibilidade, porque são todas públicas e rodam o mesmo código. A diferença entre elas vem só de latência e custo, onde a Monad ficou à frente nas duas medidas.

## Limitações
- **Testnet não é rede principal.** As medições foram feitas em testnets, com menos tráfego que as redes principais, coletadas em paralelo, na mesma máquina e com RPC público. O teste cobriu um protocolo e lotes de até 50 operações simultâneas; com 100% de sucesso em todas, o critério de resiliência não diferenciou as redes.
- **Latência sob carga.** No lote de 50 da Avalanche, 98% dos aceites ficaram em até 30 s e o máximo foi 64,3 s; o horário coincide com uma pausa do observador de blocos e está sendo conferido.
- **Custos.** A Sepolia, testnet da Ethereum, recebeu em 06/10/2026 uma atualização que encarece as operações em cerca de 3,5 vezes; a rede principal ainda não recebeu, e a Ethereum é a mais cara de qualquer forma. Tokens de teste não têm valor: o custo usa o preço do gas e a cotação de cada rede principal em 16/10/2026 (CoinGecko e consulta pública aos nós). O custo de infraestrutura para três participantes foi levantado (por mês: US$ 377 na Ethereum, US$ 1.502 na Avalanche e US$ 8.681 na Monad em servidor físico, ou US$ 1.564 em instância virtual), mas, por decisão da equipe, não entra na pontuação. Se entrasse, a Avalanche passaria ao primeiro lugar no cenário com servidor físico para a Monad.
- **Redes públicas.** Nas três redes, qualquer pessoa pode ler as operações registradas; esconder valores e contrapartes depende da aplicação.
- **Método.** Os pesos do AHP vieram de uma regra por níveis. A normalização min-max depende do conjunto fechado de redes. Os critérios qualitativos (C5, C2-M1, C2-M3) seguem escalas definidas pela equipe, e as medidas internas de C2 e C4 usam média simples. Números declarados pelas redes, como os da Monad, não foram verificados por terceiros.
- **Latência.** Mede a inclusão no bloco, não a janela completa do requisito de 30 s, que inclui backend e tela.
- **Escopo.** Os resultados valem para este protocolo.

