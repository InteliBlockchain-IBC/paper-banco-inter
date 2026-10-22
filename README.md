# paper-banco-inter

Trilha de pesquisa acadêmica do projeto Inteli Blockchain × Banco Inter: o paper que escolhe a
rede blockchain para o protocolo de crédito interfinanceiro overnight (CDI) com liquidação DvP.

**Pergunta de pesquisa:** qual rede blockchain é mais adequada para executar um protocolo de
concessão de crédito interfinanceiro overnight com liquidação por entrega contra pagamento (DvP)?

**Método:** decisão multicritério. Três redes públicas (Ethereum, Avalanche e Monad), medidas nas
testnets Sepolia, Fuji e Monad, são avaliadas em cinco critérios com pesos do AHP: resiliência
29,78%, segurança do contrato 29,78%, latência 15,78%, custo 15,78% e compatibilidade EVM 8,88%.
Parte dos dados vem da documentação oficial e parte é medida rodando o contrato do projeto em cada
rede.

## Estrutura

```
paper-banco-inter/
├── pesquisa/                    o conteúdo do paper, na ordem em que foi produzido
│   ├── 1-redes-candidatas/      pesquisas exploratórias de setembro (histórico, não atualizado)
│   ├── 2-metodo/                matriz de critérios e roteiro de medição (vigentes)
│   ├── 3-resultados/            resultados.md, gráficos e resumo.json (gerados por script)
│   └── 4-custo-infraestrutura/  levantamento do custo de infraestrutura (C4-M2), descritivo
├── entregas/                    o que sai para fora: resumo executivo
├── artigo/                      versão preliminar do artigo em LaTeX (artigo-alpha.tex + referencias.bib)
├── dados/                       dados brutos de cada coleta (CSV, metadados, logs)
└── benchmark/                   código que coleta e analisa os dados
```

| Caminho | O que é | Quem edita |
|---|---|---|
| [`pesquisa/1-redes-candidatas/`](pesquisa/1-redes-candidatas/) | Pesquisas de setembro sobre cada rede, que levaram à lista final. Inclui as descartadas (Solana, Stellar e Miden) | Ninguém: registro histórico |
| [`pesquisa/2-metodo/matriz-de-criterios.md`](pesquisa/2-metodo/matriz-de-criterios.md) | Fonte única das decisões: pergunta, redes, critérios, pesos, escalas, ameaças à validade e referências | A equipe. Atualize aqui primeiro quando algo mudar |
| [`pesquisa/2-metodo/roteiro-medicao.md`](pesquisa/2-metodo/roteiro-medicao.md) | Como medir: testes T1 e T2, falhas, formato dos dados, normalização e sensibilidade | A equipe |
| [`pesquisa/3-resultados/resultados.md`](pesquisa/3-resultados/resultados.md) | Situação da coleta, ranking, sensibilidade, custo e uma seção por rede | Só o script (`npm run analisar`) |
| [`pesquisa/4-custo-infraestrutura/custo-infraestrutura.md`](pesquisa/4-custo-infraestrutura/custo-infraestrutura.md) | Custo mensal de infraestrutura por rede (C4-M2), fora da pontuação por decisão da equipe | A equipe |
| [`entregas/resumo-executivo.md`](entregas/resumo-executivo.md) | Resumo de uma página para o parceiro | A equipe, copiando os números de `resultados.md` |
| [`artigo/`](artigo/) | Versão preliminar do artigo em LaTeX, com os números de `resultados.md` e as figuras de `pesquisa/3-resultados/graficos/` | A equipe |
| [`dados/`](dados/) | Uma linha por transação de cada coleta, mais metadados e preços de referência | Só os scripts de coleta |
| [`benchmark/`](benchmark/) | Coletores, análise e testes | Quem mantém o código |

O contrato avaliado fica em outro repositório, `projeto-inter-web3` (commit `3347bf2`), que o
benchmark espera encontrar ao lado deste.

## Fluxo

1. A **matriz** define o que vale como critério e quanto pesa.
2. O **roteiro** define como cada critério é medido.
3. O **benchmark** executa o roteiro e grava em `dados/`.
4. `npm run analisar` (dentro de `benchmark/`) transforma os dados em notas e ranking e regera `pesquisa/3-resultados/`.
5. O artigo (`artigo/`) e o resumo executivo copiam os números de `pesquisa/3-resultados/resultados.md`.

## Situação em 22/10/2026

As três testnets foram medidas no mesmo dia (16/10/2026, entre 22:40 e 23:22 UTC): 1.095
transações, nenhuma falha. Todo número vem de testnet pública (`TESTNET`).

| Etapa | Situação |
|---|---|
| Critérios, pesos e método | Decididos |
| Lista de redes | Fechada em três testnets (decisão F, 22/10/2026) |
| Roteiro de medição | Pronto (v2.1) |
| Código de coleta e análise | Pronto e testado (13 testes dos coletores e 9 da análise) |
| Coleta | Completa: Sepolia, Fuji e Monad em 16/10 |
| Custo de infraestrutura (C4-M2) | Levantado em 19/10 (`pesquisa/4-custo-infraestrutura/`); só descritivo, fora da pontuação |
| Resumo executivo | Fechado, com as três testnets e as limitações revisadas |
| Artigo | Versão preliminar em LaTeX em `artigo/`; texto final a escrever |

**Resultado (pesos do cenário base):**

| Posição | Rede | Latência mediana | Sucesso no T2 | Custo do ciclo | Pontuação |
|---|---|---|---|---|---|
| 1 | Monad | 0,99 s | 100% | US$ 0,0014 | 90,1 |
| 2 | Avalanche | 2,64 s | 100% | US$ 0,029 | 86,0 |
| 3 | Ethereum | 11,04 s | 100% | US$ 0,296 | 58,5 |

A ordem não muda em nenhum dos 17 cenários de pesos. Com as três redes EVM públicas, resiliência,
segurança e compatibilidade dão a mesma nota a todas; a diferença vem só de latência e custo. A
Sepolia mudou de regras de gas durante o estudo (Glamsterdam, 06/10/2026): o ciclo gastou 3,50
vezes o gas medido na Fuji, que segue as regras ainda em vigor na mainnet da Ethereum.
Detalhes em [`pesquisa/3-resultados/resultados.md`](pesquisa/3-resultados/resultados.md).

## Próximos passos

- [x] Coletar Sepolia, Fuji e Monad no mesmo dia (16/10/2026)
- [x] Versão preliminar do artigo em LaTeX (`artigo/`)
- [ ] Escrever o artigo a partir da versão preliminar
- [ ] Conferir as três latências de 64 s na Fuji (lote de 50), que coincidem com uma pausa do observador
- [x] Levantar o custo de infraestrutura por rede (C4-M2), apenas descritivo
- [x] Fechar o resumo executivo (limitações revisadas)
- [ ] Aprovar as propostas pendentes da seção 11.2 da matriz
