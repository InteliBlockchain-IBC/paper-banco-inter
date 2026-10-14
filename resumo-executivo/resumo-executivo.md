# Resumo Executivo — Seleção de rede para crédito interfinanceiro overnight

> **RASCUNHO. Os campos `[B6]` e `[A7]` dependem do ranking/sensibilidade (Pessoa B, até 15/10) e das ameaças à validade (Pessoa A). Os números finais devem ser copiados do paper, sem recálculo. Prazo: 17/10.**

**Projeto:** Inteli Blockchain × Banco Inter · prova de conceito acadêmica, em testnets, com ativos simulados e sem integração com sistemas de produção.

## Problema
A gestão de liquidez interbancária de curtíssimo prazo ainda sofre com conciliação e liquidação ineficientes: checagens manuais de limites geram atraso entre a negociação e a conclusão, o que aumenta o risco de contraparte e a complexidade do fechamento diário de caixa. A escolha da rede blockchain que sustentaria uma solução automatizada para esse crédito overnight precisa ser feita com critérios objetivos, e não por preferência técnica.

## Método
A escolha foi tratada como uma decisão multicritério: as cinco redes candidatas (Ethereum/Sepolia, Avalanche, Monad, Hyperledger Besu e Canton) foram comparadas em critérios definidos com o parceiro. Os pesos dos critérios foram obtidos pelo método AHP, que transforma comparações par a par entre critérios em pesos numéricos consistentes. Os critérios medidos foram testados em cada rede, nas testnets: taxa de sucesso sob carga, latência até a inclusão da transação, custo por transação e complexidade do código.

## Ranking e recomendação
| Posição | Rede | Pontuação |
|---|---|---|
| 1 | `[B6]` | `[B6]` |
| 2 | `[B6]` | `[B6]` |
| 3 | `[B6]` | `[B6]` |
| 4 | `[B6]` | `[B6]` |
| 5 | `[B6]` | `[B6]` |

**Rede recomendada:** `[B6]`, por `[principais razões, 1 frase, conforme B6]`.

## Robustez da recomendação (análise de sensibilidade)
A Matriz v3.0 prevê quatro cenários de pesos: Base, Regulatório, Econômico e Estresse. `[B6]` Informar, sem fórmulas, se a rede recomendada permanece em 1º lugar em cada um. Se houver cenário em que muda, dizer qual e o que o provoca.

## Limitações
Alinhar com a Pessoa A (A7). Pontos já conhecidos pelo trabalho de coleta:
- Os testes ocorreram em testnets, não em produção; latência e taxas de testnet podem não refletir a mainnet, e o token de teste não tem valor (o custo foi convertido por cotação em `[data/fonte, B6]`).
- Condições variam entre redes: provedor de acesso, número de nós e data das rodadas (registradas por A e B) `[A7]`.
- Os testes de desempenho usaram `[transferências simples / chamadas ao contrato — confirmar]`, que podem diferir do comportamento do contrato final.
- A Canton só pôde ser testada em ambiente local (LocalNet), não em rede pública, o que limita a comparação direta com as demais.
- Stellar, Solana e Miden foram analisadas e descartadas na etapa de pesquisa; a Ethereum Mainnet serviu apenas de referência.
- `[outras ameaças à validade, A7]`

## Próximos passos
- `[confirmar com o parceiro/orientação]` Proposta: repetir os testes com chamadas aos smart contracts do projeto, validar a rede recomendada em condições mais próximas da produção e avaliar requisitos regulatórios e de privacidade.

---
*Checklist antes de circular:* números idênticos ao paper · uma página · sem fórmulas · limitações revisadas pela Pessoa A · sem placeholders restantes.
