# Resumo Executivo — Seleção de rede para crédito interfinanceiro overnight

> **Atualizado em 19/10/2026:** números de `pesquisa/3-resultados/resultados.md`. Limitações aguardam revisão da Pessoa A.

## Problema
Checagens manuais de limites atrasam a negociação e a liquidação do crédito overnight, elevando o risco de contraparte e a complexidade do fechamento de caixa. O projeto avalia, com critérios explícitos, qual rede é mais adequada para automatizar esse processo.

## Método
Comparamos Ethereum, Avalanche, Monad, Hyperledger Besu e Canton por decisão multicritério, com pesos AHP: resiliência e segurança, 29,78% cada; latência e custo, 15,78% cada; compatibilidade EVM, 8,88%. Cada rede passou por 30 ciclos T1 e 255 aceites T2 simultâneos em lotes de 10, 25 e 50 (1.825 transações). C2-M2 mediu complexidade ciclomática de 49 pontos em Solidity e 24 em Daml.

**Ambientes:** testnets Sepolia, Fuji e Monad; redes locais Besu (4 validadores) e Canton (sandbox do SDK, um participante). Coletas em 14 e 16/10.

## Resultados
| Posição | Rede | Ambiente | Latência mediana T1 até inclusão | Sucesso sob carga | Custo por ciclo completo | Pontuação |
|---|---|---|---|---|---|---|
| 1 | Canton* | Rede local | 0,37 s | 100% | US$ 0* | 86,2* |
| 2 | Hyperledger Besu* | Rede local | 1,96 s | 100% | US$ 0* | 82,8* |
| 3 | Monad | Testnet | 0,99 s | 100% | US$ 0,0014 | 79,2 |
| 4 | Avalanche | Testnet | 2,64 s | 100% | US$ 0,029 | 75,2 |
| 5 | Ethereum | Testnet | 11,04 s | 100% | US$ 0,30 | 48,6 |

Todas confirmaram os 255 aceites T2; no lote 50 da Fuji, 98% ficaram até 30 s e o máximo foi 64,3 s. No T1, todas ficaram abaixo de 30 s; a finalidade probabilística da Ethereum leva cerca de 16 min após inclusão. Custos usam preços e cotações das mainnets em 16/10.

\* **Rede local, não comparável diretamente às testnets.** Canton e Besu rodaram na máquina da equipe, onde não há cobrança de taxa; o US$ 0 é o custo do ambiente de teste, não de produção. A Canton é uma rede privada, acessível apenas a instituições autorizadas, e não há como medir seu custo real sem esse acesso. Supor um valor seria arbitrário e comprometeria a integridade da pesquisa; por isso o custo real não foi estimado, e as pontuações marcadas com asterisco devem ser lidas com essa ressalva.

**Recomendação no cenário-base:** Canton* (86,2*), por privacidade por subtransação e menor latência. A vantagem de 3,4 pontos sobre o Besu* existe porque ambos foram medidos sem taxa; se o custo real da Canton fosse considerado indefinido, o Besu lideraria.

**Alternativa robusta:** Hyperledger Besu* (82,8*), executa o contrato sem alteração e fica em primeiro ou segundo nos cenários de sensibilidade. Canton exige reescrita em Daml.

## Robustez da recomendação (análise de sensibilidade)
Em 16 variações, além do cenário-base, Canton fica em primeiro em 13 de 17 cenários. Besu lidera com pesos iguais, segurança reduzida à metade ou compatibilidade EVM aumentada em 50%; Monad, sem o critério de segurança.

## Limitações
- **Ambientes e escopo:** Besu e Canton foram testados localmente; Canton, em sandbox de um participante. Sem internet nem carga de terceiros, seus tempos não representam produção. O teste cobriu um protocolo e lotes de até 50; 100% de sucesso não diferenciou as redes.
- **Custos:** a Sepolia ativou Glamsterdam em 06/10 e seu gas medido foi 3,56 vezes o das regras atuais da mainnet. A tarifa real da Canton, rede privada de acesso restrito a instituições, não pôde ser medida e não foi estimada; o custo de infraestrutura (C4-M2) também não foi levantado.
- **Método:** pesos AHP vieram de uma regra por níveis. C2-M2 compara uma versão Solidity e uma Daml, com linguagens e números de funções diferentes. Stellar, Solana e Miden foram descartadas.
- Limitações da matriz; revisão final da Pessoa A pendente.

## Próximos passos
- Obter o custo real da Canton junto a um operador da rede e estimar a infraestrutura para três participantes; validar a rede em máquinas separadas, com carga maior e revisão regulatória/de privacidade.

---
