# Resumo Executivo — Seleção de rede para crédito interfinanceiro overnight

> **VERSÃO PRELIMINAR (16/10/2026).** Só o Hyperledger Besu foi medido, numa rede local. As demais redes aparecem com projeções tiradas da documentação oficial, sem teste. Quando as testnets e a Canton forem coletadas, os campos marcados com `[TESTNET]` e `[CANTON]` recebem os números de `pesquisa/3-resultados/resultados.md`, sem recálculo. Prazo: 17/10.

**Projeto:** Inteli Blockchain × Banco Inter · prova de conceito acadêmica, com ativos simulados e sem integração com sistemas de produção.

## Problema
A gestão de liquidez interbancária de curtíssimo prazo ainda sofre com conciliação e liquidação ineficientes: checagens manuais de limites geram atraso entre a negociação e a conclusão, o que aumenta o risco de contraparte e a complexidade do fechamento diário de caixa. A escolha da rede blockchain que sustentaria uma solução automatizada para esse crédito overnight precisa ser feita com critérios objetivos, e não por preferência técnica.

## Método
A escolha foi tratada como uma decisão multicritério: cinco redes candidatas (Ethereum, Avalanche, Monad, Hyperledger Besu e Canton) foram comparadas em cinco critérios com pesos obtidos pelo método AHP, que transforma comparações par a par em pesos consistentes. Resiliência sob carga e segurança do contrato pesam 29,78% cada; latência e custo, 15,78% cada; compatibilidade com o código atual, 8,88%.

Os critérios medidos usam o próprio contrato do projeto (autorizar, ofertar e aceitar). Eles são coletados em dois tipos de ambiente:

| Ambiente | Redes | Situação |
|---|---|---|
| Rede local, montada pela equipe numa máquina | Hyperledger Besu; Canton | Besu medido em 14/10. Canton `[CANTON]` aguardando o ambiente local |
| Testnet pública | Ethereum (Sepolia), Avalanche (Fuji), Monad | `[TESTNET]` aguardando coleta; até lá, projeção a partir da documentação oficial |

## Ranking e recomendação (preliminar)
| Posição | Rede | Origem dos números | Pontuação |
|---|---|---|---|
| 1 | Hyperledger Besu | Medido em rede local | 82,9 |
| 2 | Monad | Projeção, sem teste `[TESTNET]` | 80,1 |
| 3 | Avalanche | Projeção, sem teste `[TESTNET]` | 78,8 |
| 4 | Canton | A medir `[CANTON]` | entre 54,6 e 86,2 |
| 5 | Ethereum | Projeção, sem teste `[TESTNET]` | 48,6 |

**Rede recomendada (preliminar):** Hyperledger Besu, porque roda o contrato atual sem alteração, conclui cada operação em cerca de 2 segundos de forma definitiva, liquidou 100% das operações simultâneas no teste de carga e, por ser uma rede restrita aos participantes, protege melhor os dados das operações do que as redes públicas.

**O que ainda pode mudar a recomendação:**
- **Canton:** é a única rede que ainda pode passar o Besu. Isso acontece se, no ambiente local, ela tiver custo zero por operação e concluir cada operação em até cerca de 2,7 segundos `[CANTON]`.
- **Testnets:** se Monad ou Avalanche falharem sob carga nas testnets, a vantagem do Besu aumenta `[TESTNET]`.
- **Custo de infraestrutura:** ainda não foi levantado. O Besu exige 4 servidores validadores, e esse custo pode reduzir a vantagem dele.

## Robustez da recomendação (análise de sensibilidade)
A análise refez o ranking em 16 variações de pesos: todos iguais, cada peso 50% maior e 50% menor, e cada critério retirado da conta. O Besu permanece em 1º lugar em 16 dos 17 cenários (as 16 variações mais o cenário base). A exceção é retirar o critério de segurança: aí a Monad passa à frente, porque a vantagem do Besu vem da privacidade de uma rede restrita aos participantes. Este resultado é preliminar enquanto houver projeção `[TESTNET]` `[CANTON]`.

## Limitações
- **Rede local não é rede real.** O Besu foi medido numa rede montada na máquina da equipe, sem tráfego de outros usuários nem latência de internet; a Canton será medida da mesma forma.
- **Projeção não é medição.** Nas testnets ainda não coletadas, os números vêm da documentação oficial das próprias redes, e o sucesso sob carga é suposto em 100%.
- **Custos convertidos.** Tokens de teste não têm valor. O custo foi calculado com o preço do gas e a cotação de cada rede na rede principal, em 14/10/2026 (CoinGecko e consulta pública aos nós).
- **Carga limitada.** Os testes usaram até 50 operações simultâneas; o resultado não mede a capacidade máxima de cada rede.
- **Canton exige reescrever o contrato** em outra linguagem (Daml), o que pesa contra ela no critério de compatibilidade.
- **Redes descartadas antes.** Stellar, Solana e Miden foram analisadas e descartadas na etapa de pesquisa; a Ethereum principal serviu apenas de referência.
- `[outras ameaças à validade, A7]`

## Próximos passos
- Coletar as três testnets no mesmo dia e a Canton no ambiente local; atualizar esta página com os números finais.
- Levantar o custo de infraestrutura de cada rede para três participantes (duas instituições e o regulador simulado).
- `[confirmar com o parceiro/orientação]` Validar a rede recomendada em condições mais próximas da produção, com participantes em máquinas separadas, e avaliar requisitos regulatórios e de privacidade.

---
*Checklist antes de circular:* números idênticos a `pesquisa/3-resultados/resultados.md` e ao paper · uma página · sem fórmulas · limitações revisadas pela Pessoa A · nenhum `[TESTNET]`, `[CANTON]` ou `[A7]` restante.
