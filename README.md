# paper-banco-inter

Trilha de pesquisa acadêmica do projeto Inteli Blockchain × Banco Inter: o paper que escolhe a
rede blockchain para o protocolo de crédito interfinanceiro overnight (CDI) com liquidação DvP.

**Pergunta de pesquisa:** qual rede blockchain é mais adequada para executar um protocolo de
concessão de crédito interfinanceiro overnight com liquidação por entrega contra pagamento (DvP)?

**Método:** decisão multicritério. Cinco redes (Ethereum, Avalanche, Monad, Hyperledger Besu e
Canton) são avaliadas em cinco critérios com pesos do AHP: resiliência 29,78%, segurança do
contrato 29,78%, latência 15,78%, custo 15,78% e compatibilidade EVM 8,88%. Parte dos dados vem
da documentação oficial e parte é medida rodando o contrato do projeto em cada rede.

## Estrutura

```
paper-banco-inter/
├── pesquisa/                    o conteúdo do paper, na ordem em que foi produzido
│   ├── 1-redes-candidatas/      pesquisas exploratórias de setembro (histórico, não atualizado)
│   ├── 2-metodo/                matriz de critérios e roteiro de medição (vigentes)
│   └── 3-resultados/            resultados.md, gráficos e resumo.json (gerados por script)
├── entregas/                    o que sai para fora: resumo executivo
├── dados/                       dados brutos de cada coleta (CSV, metadados, logs)
└── benchmark/                   código que coleta e analisa os dados
```

| Caminho | O que é | Quem edita |
|---|---|---|
| [`pesquisa/1-redes-candidatas/`](pesquisa/1-redes-candidatas/) | Pesquisas de setembro sobre cada rede, que levaram à lista final. Inclui as descartadas (Solana, Stellar e Miden) | Ninguém: registro histórico |
| [`pesquisa/2-metodo/matriz-de-criterios.md`](pesquisa/2-metodo/matriz-de-criterios.md) | Fonte única das decisões: pergunta, redes, critérios, pesos, escalas, ameaças à validade e referências | A equipe. Atualize aqui primeiro quando algo mudar |
| [`pesquisa/2-metodo/roteiro-medicao.md`](pesquisa/2-metodo/roteiro-medicao.md) | Como medir: testes T1 e T2, falhas, formato dos dados, normalização e sensibilidade | A equipe |
| [`pesquisa/3-resultados/resultados.md`](pesquisa/3-resultados/resultados.md) | Situação da coleta, ranking, sensibilidade, custo e uma seção por rede | Só o script (`npm run analisar`) |
| [`entregas/resumo-executivo.md`](entregas/resumo-executivo.md) | Resumo de uma página para o parceiro | A equipe, copiando os números de `resultados.md` |
| [`dados/`](dados/) | Uma linha por transação de cada coleta, mais metadados e preços de referência | Só os scripts de coleta |
| [`benchmark/`](benchmark/) | Coletores, análise, redes locais (Besu e Canton) e testes | Quem mantém o código |

O contrato avaliado fica em outro repositório, `projeto-inter-web3` (commit `3347bf2`), que o
benchmark espera encontrar ao lado deste.

## Fluxo

1. A **matriz** define o que vale como critério e quanto pesa.
2. O **roteiro** define como cada critério é medido.
3. O **benchmark** executa o roteiro e grava em `dados/`.
4. `npm run analisar` (dentro de `benchmark/`) transforma os dados em notas e ranking e regera `pesquisa/3-resultados/`.
5. O paper e o resumo executivo copiam os números de `pesquisa/3-resultados/resultados.md`.

## Situação em 16/10/2026

| Etapa | Situação |
|---|---|
| Critérios, pesos e método | Decididos |
| Roteiro de medição | Pronto (v2) |
| Código de coleta e análise | Pronto e testado (27 testes) |
| Hyperledger Besu | Medido em 14/10 |
| Sepolia, Fuji e Monad | Aguardando coleta (precisa da chave com faucet em `benchmark/.env`) |
| Canton | Aguardando LocalNet; modelo Daml escrito, ainda não compilado |
| Custo de infraestrutura (C4-M2) | Não levantado (INTER-16 e INTER-17) |
| Resumo executivo | Rascunho, aguardando o ranking final |
| Prazos | Paper em 17/10/2026 · demo day em 21/10/2026 |

**Resultado preliminar:** Hyperledger Besu em 1º (82,9 pontos), Monad 80,1, Avalanche 78,8 e
Ethereum 48,6. A Canton fica entre 54,6 e 86,2 até ser medida. Só o Besu tem dados medidos; as
demais redes usam valores declarados.

## Próximos passos

- [ ] Coletar Sepolia, Fuji e Monad no mesmo dia ([instruções](benchmark/README.md#coleta))
- [ ] Subir o LocalNet da Canton e coletar ([instruções](benchmark/README.md#canton))
- [ ] Levantar o custo de infraestrutura por rede (C4-M2)
- [ ] Rodar `npm run analisar` e copiar o ranking final para o paper e o resumo executivo
- [ ] Aprovar as propostas pendentes da seção 11.2 da matriz
