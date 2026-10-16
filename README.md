# paper-banco-inter

Trilha de pesquisa acadêmica do projeto Inteli Blockchain × Banco Inter: o paper que escolhe a
rede blockchain para o protocolo de crédito interfinanceiro overnight (CDI) com liquidação DvP.

**Pergunta de pesquisa:** qual rede blockchain é mais adequada para executar um protocolo de
concessão de crédito interfinanceiro overnight com liquidação por entrega contra pagamento (DvP)?

**Método:** decisão multicritério. Cinco redes (Ethereum, Avalanche, Monad, Hyperledger Besu e
Canton) são avaliadas em cinco critérios com pesos do AHP: resiliência 29,78%, segurança do
contrato 29,78%, latência 15,78%, custo 15,78% e compatibilidade EVM 8,88%. Parte dos dados vem
da documentação oficial e parte é medida rodando o contrato do projeto em cada rede.

## Situação em 16/10/2026

| Etapa | Situação |
|---|---|
| Critérios, pesos e método | Decididos ([matriz de critérios](docs/matriz-de-criterios.md)) |
| Roteiro de medição | Pronto, v2 ([roteiro](docs/roteiro-medicao.md)) |
| Scripts de coleta e análise | Prontos e testados ([benchmark-redes](benchmark-redes/)) |
| Hyperledger Besu | Medido em 14/10 |
| Sepolia, Fuji e Monad | Aguardando coleta (precisa da chave com faucet no `.env`) |
| Canton | Aguardando LocalNet; modelo Daml escrito, ainda não compilado |
| Custo de infraestrutura (C4-M2) | Não levantado (INTER-16 e INTER-17) |
| Resumo executivo | Rascunho, aguardando o ranking final |
| Entrega do paper | 17/10/2026 · demo day 21/10/2026 |

**Resultado preliminar:** Hyperledger Besu em 1º (82,9 pontos), Monad 80,1, Avalanche 78,8 e
Ethereum 48,6. A Canton fica entre 54,6 e 86,2 até ser medida. Só o Besu tem dados medidos; as
demais redes usam valores declarados. Detalhes e origem de cada número em
[`docs/resultados.md`](docs/resultados.md).

## O que tem em cada lugar

| Caminho | O que é | Status |
|---|---|---|
| [`docs/matriz-de-criterios.md`](docs/matriz-de-criterios.md) | Fonte única das decisões: pergunta, redes, critérios, pesos, escalas, ameaças à validade e referências | Vigente. Atualize aqui primeiro quando algo mudar |
| [`docs/roteiro-medicao.md`](docs/roteiro-medicao.md) | Como medir: testes T1 e T2, classificação de falhas, formato dos dados, normalização e sensibilidade | Vigente (v2) |
| [`docs/resultados.md`](docs/resultados.md) | Resultados: situação da coleta, ranking, sensibilidade, custo e uma seção por rede | Gerado por script. Não edite à mão |
| [`docs/resumo-executivo/`](docs/resumo-executivo/resumo-executivo.md) | Resumo de uma página para o parceiro | Rascunho |
| [`docs/pesquisa-redes/`](docs/pesquisa-redes/) | Pesquisas exploratórias de setembro sobre cada rede, que levaram à lista final (inclui as descartadas: Solana, Stellar e Miden) | Histórico, não atualizado |
| [`benchmark-redes/`](benchmark-redes/) | Código da coleta e da análise, dados brutos e gráficos | Ativo |

O contrato avaliado fica em outro repositório, `projeto-inter-web3` (commit `3347bf2`), que o
benchmark espera encontrar ao lado deste.

## Como os documentos se ligam

1. A **matriz** define o que vale como critério e quanto pesa.
2. O **roteiro** define como cada critério é medido.
3. O **benchmark** executa o roteiro e grava os dados em `benchmark-redes/dados/`.
4. `npm run analisar` transforma os dados em notas e ranking e regera `docs/resultados.md`.
5. O paper e o resumo executivo copiam os números de `docs/resultados.md`.

## Próximos passos

- [ ] Coletar Sepolia, Fuji e Monad no mesmo dia ([instruções](benchmark-redes/README.md#coleta))
- [ ] Subir o LocalNet da Canton e coletar ([instruções](benchmark-redes/README.md#canton))
- [ ] Levantar o custo de infraestrutura por rede (C4-M2)
- [ ] Rodar `npm run analisar` e copiar o ranking final para o paper e o resumo executivo
- [ ] Aprovar as propostas pendentes da seção 11.2 da matriz
