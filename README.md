# paper-banco-inter

Trilha de pesquisa acadêmica do projeto Inteli Blockchain × Banco Inter: o estudo que escolhe a
rede blockchain para o protocolo de crédito interfinanceiro overnight com liquidação DvP.

**Pergunta de pesquisa:** qual rede blockchain é mais adequada para executar um protocolo de
concessão de crédito interfinanceiro overnight com liquidação por entrega contra pagamento (DvP)?

**Método:** decisão multicritério. Três redes públicas (Ethereum, Avalanche e Monad), medidas nas
testnets Sepolia, Fuji e Monad, são avaliadas em cinco critérios com pesos do AHP: resiliência
29,78%, segurança do contrato 29,78%, latência 15,78%, custo 15,78% e compatibilidade EVM 8,88%.
Parte dos dados vem da documentação oficial de cada rede. A outra parte é medida executando o
mesmo contrato, sem alterações, em cada testnet.

## Estrutura

```
paper-banco-inter/
├── artigo/        artigo-alpha: só uma versão base em LaTeX, não usada no artigo final
├── pesquisa/
│   ├── 1-redes-candidatas/      pesquisas exploratórias de setembro (registro histórico)
│   ├── 2-metodo/                matriz de critérios e roteiro de medição
│   ├── 3-resultados/            resultados, gráficos e resumo.json (gerados por script)
│   └── 4-custo-infraestrutura/  custo de infraestrutura por rede (C4-M2), só descritivo
├── benchmark/     código de coleta e análise, e a documentação dos experimentos
└── dados/         dados brutos da coleta (CSV, metadados, preços, logs)
```

| Caminho | O que é |
|---|---|
| [`benchmark/README.md`](benchmark/README.md) | **Como os experimentos foram feitos e como repeti-los:** objeto medido, testes T1 e T2, definições, parâmetros, a coleta de 16/10/2026 e o passo a passo |
| [`pesquisa/2-metodo/matriz-de-criterios.md`](pesquisa/2-metodo/matriz-de-criterios.md) | Fonte única das decisões: pergunta, redes, critérios, pesos, escalas, ameaças à validade e referências |
| [`pesquisa/2-metodo/roteiro-medicao.md`](pesquisa/2-metodo/roteiro-medicao.md) | Especificação da medição: testes, falhas, formato dos dados, normalização e sensibilidade |
| [`pesquisa/3-resultados/resultados.md`](pesquisa/3-resultados/resultados.md) | Ranking, sensibilidade, custo e uma seção por rede. Gerado por `npm run analisar`; não edite à mão |
| [`pesquisa/4-custo-infraestrutura/`](pesquisa/4-custo-infraestrutura/custo-infraestrutura.md) | Custo mensal de três nós por rede (C4-M2), fora da pontuação por decisão da equipe |
| [`pesquisa/1-redes-candidatas/`](pesquisa/1-redes-candidatas/) | Pesquisas de setembro que levaram à lista final, incluindo as redes descartadas |
| [`artigo/`](artigo/README.md) | `artigo-alpha.tex`: **só uma versão base**, de 22/10/2026, com os números de `resultados.md`. Fica como registro e **não foi usada no artigo final**, que foi escrito à parte, fora deste repositório |
| [`dados/`](dados/README.md) | Uma linha por transação medida, mais metadados, preços de referência e registros da implantação. Só os scripts escrevem aqui |

O contrato avaliado fica em outro repositório, `projeto-inter-web3` (commit `3347bf2`). O
benchmark espera encontrá-lo ao lado deste.

## Fluxo

1. A **matriz** define os critérios e quanto cada um pesa.
2. O **roteiro** define como cada critério é medido.
3. O **benchmark** implanta o contrato, executa o roteiro em cada testnet e grava em `dados/`.
4. `npm run analisar` (dentro de `benchmark/`) transforma os dados em notas, ranking e
   sensibilidade, e regera `pesquisa/3-resultados/`.
5. O artigo final, escrito fora deste repositório, usa os números de `pesquisa/3-resultados/resultados.md`.

## Resultado

As três testnets foram medidas em paralelo em 16/10/2026, entre 22:40 e 23:22 UTC. Foram 1.095
transações, sem nenhuma falha.

| Posição | Rede | Latência mediana (T1) | Sucesso no T2 | Custo do ciclo | Pontuação |
|---|---|---|---|---|---|
| 1 | Monad | 0,99 s | 100% | US$ 0,0014 | 90,1 |
| 2 | Avalanche | 2,64 s | 100% | US$ 0,029 | 86,0 |
| 3 | Ethereum | 11,04 s | 100% | US$ 0,296 | 58,5 |

**Sensibilidade.** A ordem não muda em nenhum dos 17 cenários de pesos. Com três redes EVM
públicas executando o mesmo código, resiliência, segurança e compatibilidade dão a mesma nota a
todas; a diferença vem só de latência e custo.

**Glamsterdam.** A Sepolia mudou as regras de gas durante o estudo, com a atualização Glamsterdam
em 06/10/2026. O ciclo gastou 3,50 vezes o gas medido na Fuji, que segue as regras ainda em vigor
na mainnet da Ethereum.

Detalhes em [`pesquisa/3-resultados/resultados.md`](pesquisa/3-resultados/resultados.md).

## Pendências

- [ ] Conferir as três latências de cerca de 64 s na Fuji (lote de 50, primeira rodada do T2), que
  coincidem com uma pausa do observador de blocos.
- [ ] Aprovar as propostas pendentes da seção 11.2 da matriz.
