# Resumo Executivo — Seleção de rede para crédito interfinanceiro overnight

> **Situação (16/10/2026):** as cinco redes foram medidas. Os números vêm de `pesquisa/3-resultados/resultados.md` e devem ser copiados sem recálculo. Antes de circular, a equipe precisa decidir o item marcado `[DECIDIR]` e revisar as limitações `[A7]`.

**Projeto:** Inteli Blockchain × Banco Inter · prova de conceito acadêmica, com ativos simulados e sem integração com sistemas de produção.

## Problema
A gestão de liquidez interbancária de curtíssimo prazo ainda sofre com conciliação e liquidação ineficientes: checagens manuais de limites geram atraso entre a negociação e a conclusão, o que aumenta o risco de contraparte e a complexidade do fechamento diário de caixa. A escolha da rede blockchain que sustentaria uma solução automatizada para esse crédito overnight precisa ser feita com critérios objetivos, e não por preferência técnica.

## Método
A escolha foi tratada como uma decisão multicritério: cinco redes candidatas (Ethereum, Avalanche, Monad, Hyperledger Besu e Canton) foram comparadas em cinco critérios com pesos obtidos pelo método AHP, que transforma comparações par a par em pesos consistentes. Resiliência sob carga e segurança do contrato pesam 29,78% cada; latência e custo, 15,78% cada; compatibilidade com o código atual, 8,88%.

Cada rede executou o próprio contrato do projeto (autorizar, ofertar e aceitar): 30 operações completas em sequência e 255 aceites disparados em lotes simultâneos de 10, 25 e 50. Foram 1.825 transações no total.

| Ambiente | Redes | Coleta |
|---|---|---|
| Testnet pública | Ethereum (Sepolia), Avalanche (Fuji), Monad | 16/10/2026 |
| Rede local, montada pela equipe numa máquina | Hyperledger Besu (4 validadores); Canton (ambiente local do SDK oficial) | 14/10 e 16/10/2026 |

## Resultados
| Posição | Rede | Ambiente | Tempo mediano até a confirmação | Sucesso sob carga | Custo por operação completa | Pontuação |
|---|---|---|---|---|---|---|
| 1 | Canton | Rede local | 0,37 s | 100% | US$ 0 (sem taxa no ambiente local) | 86,2 |
| 2 | Hyperledger Besu | Rede local | 1,96 s | 100% | US$ 0 (rede sem taxa) | 82,8 |
| 3 | Monad | Testnet | 0,99 s | 100% | US$ 0,0014 | 79,2 |
| 4 | Avalanche | Testnet | 2,64 s | 100% | US$ 0,029 | 75,2 |
| 5 | Ethereum | Testnet | 11,04 s | 100% | US$ 0,30 | 48,6 |

Todas as redes confirmaram todas as operações, inclusive com 50 aceites simultâneos, e todas ficaram abaixo do limite de 30 segundos do projeto. A Ethereum, porém, só torna a operação definitiva cerca de 13 minutos depois. O custo foi convertido pelos preços da rede principal de cada blockchain em 16/10/2026.

**Rede recomendada pela matriz:** Canton, por ser a única em que cada banco vê só as próprias operações, com a confirmação mais rápida medida. `[DECIDIR]` A vantagem de 3,4 pontos sobre o Besu depende de tratar a Canton como sem custo por operação, como no ambiente local. Na rede real, o tráfego é pago. Se esse custo ficar indefinido, o Besu passa ao primeiro lugar.

**Alternativa robusta:** Hyperledger Besu. Roda o contrato atual sem nenhuma alteração, fica em 1º ou 2º lugar em todos os cenários testados e é a base técnica do piloto do Drex. A Canton exige reescrever o contrato em outra linguagem (Daml).

## Robustez da recomendação (análise de sensibilidade)
O ranking foi refeito em 16 variações de pesos. A Canton permanece em 1º em 13 dos 17 cenários. O 1º lugar passa ao Besu com pesos iguais, com o peso de segurança reduzido à metade ou com o peso de compatibilidade aumentado em 50%, e à Monad quando o critério de segurança é retirado. Ou seja, a escolha entre Canton e Besu depende de quanto o banco valoriza a privacidade e de quanto aceita reescrever o contrato.

## Limitações
- **Rede local não é rede real.** Besu e Canton rodaram na máquina da equipe, sem tráfego de outros usuários nem latência de internet; a Canton rodou com um único participante. Os tempos delas são um piso.
- **Testnet mudou durante o estudo.** A Sepolia, testnet da Ethereum, recebeu em 06/10/2026 uma atualização que encarece operações em cerca de 3,6 vezes; a rede principal ainda não recebeu. A Ethereum é a mais cara de qualquer forma, então a ordem não muda.
- **Carga limitada.** Os testes usaram até 50 operações simultâneas; nenhuma rede falhou, então o critério de resiliência não diferenciou as redes.
- **Custos convertidos.** Tokens de teste não têm valor; o custo foi calculado com o preço do gas e a cotação de cada rede principal em 16/10/2026 (CoinGecko e consulta pública aos nós). O custo de infraestrutura ainda não foi levantado.
- **Redes descartadas antes.** Stellar, Solana e Miden foram analisadas e descartadas na etapa de pesquisa.
- `[outras ameaças à validade, A7]`

## Próximos passos
- Decidir como tratar o custo da Canton e levantar o custo de infraestrutura de cada rede para três participantes.
- `[confirmar com o parceiro/orientação]` Validar a rede escolhida com participantes em máquinas separadas e carga maior, e avaliar requisitos regulatórios e de privacidade.

---
*Checklist antes de circular:* números idênticos a `pesquisa/3-resultados/resultados.md` e ao paper · uma página · sem fórmulas · limitações revisadas pela Pessoa A · nenhum `[DECIDIR]` ou `[A7]` restante.
