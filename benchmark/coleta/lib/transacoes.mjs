// Envio e acompanhamento de transações com o horário de envio registrado no envio real,
// depois da estimativa de gas (seção 3.2), e o horário do recibo lido no mesmo relógio.
import { decodeEventLog, encodeFunctionData } from 'viem';
import { FALHA_TEMPO_LIMITE, classificarErro, classificarRecibo } from './falhas.mjs';
import { esperar, isoMs } from './comum.mjs';

export const TEMPO_LIMITE_MS = Number(process.env.TEMPO_LIMITE_S ?? 300) * 1000; // 5 min (seção 4.3)
export const MULTIPLICADOR_GAS = Number(process.env.MULTIPLICADOR_GAS ?? 1.2);

/**
 * Acompanha blocos novos e marca o momento em que cada transação esperada aparece.
 * Uma consulta de blocos serve todas as transações pendentes, o que evita estourar
 * o limite de requisições do RPC no T2 (50 transações ao mesmo tempo).
 */
export class ObservadorBlocos {
  constructor(cliente, intervaloMs) {
    this.cliente = cliente;
    this.intervaloMs = intervaloMs;
    this.pendentes = new Map(); // hash -> { resolver, prazo }
    this.ultimo = null;
    this.ativo = false;
    this.errosConsulta = 0;
    this.pausas = [];
  }

  async iniciar() {
    this.ultimo = await this.cliente.getBlockNumber({ cacheTime: 0 });
    this.ativo = true;
    this.laco = this.#rodar();
  }

  async parar() {
    this.ativo = false;
    await this.laco;
  }

  esperar(hash, tempoLimiteMs = TEMPO_LIMITE_MS) {
    return new Promise((resolver) => {
      this.pendentes.set(hash.toLowerCase(), { resolver, prazo: Date.now() + tempoLimiteMs });
    });
  }

  async #rodar() {
    let anterior = Date.now();
    while (this.ativo) {
      // Um intervalo muito maior que o esperado indica máquina suspensa ou processo parado:
      // o horário observado deixa de valer como horário do recibo.
      const volta = Date.now();
      if (volta - anterior > Math.max(10_000, this.intervaloMs * 20)) this.pausas.push({ de: isoMs(anterior), ate: isoMs(volta) });
      anterior = volta;
      let consultou = false;
      try {
        const atual = await this.cliente.getBlockNumber({ cacheTime: 0 });
        while (this.ultimo < atual) {
          const numero = this.ultimo + 1n;
          const bloco = await this.cliente.getBlock({ blockNumber: numero });
          if (!bloco) break; // RPC com balanceador pode estar atrás; tenta de novo
          const visto = Date.now();
          for (const h of bloco.transactions) {
            const p = this.pendentes.get(h.toLowerCase());
            if (p) {
              this.pendentes.delete(h.toLowerCase());
              p.resolver({ incluida: true, bloco: numero, tRecibo: visto, tBloco: Number(bloco.timestamp) * 1000 });
            }
          }
          this.ultimo = numero;
        }
        consultou = true;
      } catch {
        this.errosConsulta++;
      }
      // Prazo só vence quando a consulta funcionou; antes de declarar falha D, confere o recibo.
      if (consultou) {
        const agora = Date.now();
        for (const [h, p] of this.pendentes) {
          if (agora <= p.prazo) continue;
          this.pendentes.delete(h);
          p.resolver(await this.#conferirAtrasada(h));
        }
      }
      await esperar(this.intervaloMs);
    }
  }

  async #conferirAtrasada(hash) {
    try {
      const r = await this.cliente.getTransactionReceipt({ hash });
      const b = await this.cliente.getBlock({ blockNumber: r.blockNumber });
      return { incluida: true, atrasada: true, bloco: r.blockNumber, tBloco: Number(b.timestamp) * 1000 };
    } catch {
      return { incluida: false };
    }
  }
}

/** Controle explícito de nonce por conta (seção 4.3, item 3). */
export class Nonces {
  constructor(cliente) {
    this.cliente = cliente;
    this.mapa = new Map();
  }

  async proximo(endereco) {
    if (!this.mapa.has(endereco)) {
      this.mapa.set(endereco, await this.cliente.getTransactionCount({ address: endereco, blockTag: 'pending' }));
    }
    const n = this.mapa.get(endereco);
    this.mapa.set(endereco, n + 1);
    return n;
  }

  async ressincronizar(endereco) {
    this.mapa.set(endereco, await this.cliente.getTransactionCount({ address: endereco, blockTag: 'pending' }));
  }
}

export async function taxas(cliente, rede) {
  return cliente.estimateFeesPerGas({ type: 'eip1559' });
}

/**
 * Executa transações de contrato e devolve linhas no formato do CSV da seção 6.1.
 */
export class Executor {
  constructor({ rede, clientes, observador, abis }) {
    this.rede = rede;
    this.leitura = clientes.leitura;
    this.envio = clientes.envio;
    this.observador = observador;
    this.abis = abis;
    this.nonces = new Nonces(clientes.leitura);
  }

  async estimar({ conta, endereco, abi, funcao, args }) {
    const est = await this.leitura.estimateContractGas({ account: conta, address: endereco, abi, functionName: funcao, args });
    return BigInt(Math.ceil(Number(est) * MULTIPLICADOR_GAS));
  }

  /**
   * Prepara e assina a transação (estimativa incluída, fora do tempo medido).
   * Em caso de erro na estimativa devolve { erro } já classificado.
   */
  async preparar({ conta, endereco, abi, funcao, args, gas, fees }) {
    try {
      const gasLimite = gas ?? (await this.estimar({ conta, endereco, abi, funcao, args }));
      const f = fees ?? (await taxas(this.leitura, this.rede));
      const nonce = await this.nonces.proximo(conta.address);
      const tx = {
        chainId: this.rede.chainId,
        type: 'eip1559',
        to: endereco,
        data: encodeFunctionData({ abi, functionName: funcao, args }),
        gas: gasLimite,
        nonce,
        maxFeePerGas: f.maxFeePerGas,
        maxPriorityFeePerGas: f.maxPriorityFeePerGas,
        value: 0n,
      };
      const assinada = await conta.signTransaction(tx);
      return { conta, funcao, tx, assinada };
    } catch (erro) {
      return { conta, funcao, erro: { etapa: 'estimativa', ...classificarErro(erro, this.abis.erros) } };
    }
  }

  /** Envia a transação assinada; o horário de envio é o instante do envio real. */
  async enviar(preparada) {
    if (preparada.erro) return preparada;
    const tEnvio = Date.now();
    try {
      const hash = await this.envio.request({ method: 'eth_sendRawTransaction', params: [preparada.assinada] });
      const espera = this.observador.esperar(hash);
      return { ...preparada, hash, tEnvio, espera };
    } catch (erro) {
      await this.nonces.ressincronizar(preparada.conta.address).catch(() => {});
      return { ...preparada, tEnvio, erro: { etapa: 'envio', ...classificarErro(erro, this.abis.erros) } };
    }
  }

  /** Espera o recibo e monta a linha do CSV. */
  async concluir(enviada, base) {
    const linha = {
      ...base,
      funcao: enviada.funcao,
      conta: enviada.conta.address,
      t_envio_utc: enviada.tEnvio ? isoMs(enviada.tEnvio) : '',
      gas_limit: enviada.tx?.gas?.toString() ?? '',
      nonce: enviada.tx?.nonce ?? '',
    };
    if (enviada.erro) {
      return { linha: { ...linha, status: 'falha', etapa_erro: enviada.erro.etapa, nome_erro: enviada.erro.nome, categoria_falha: enviada.erro.categoria } };
    }
    linha.tx_hash = enviada.hash;
    const r = await enviada.espera;
    if (!r.incluida) {
      return { linha: { ...linha, status: 'falha', etapa_erro: 'recibo', nome_erro: FALHA_TEMPO_LIMITE.nome, categoria_falha: FALHA_TEMPO_LIMITE.categoria } };
    }
    const recibo = await this.leitura.getTransactionReceipt({ hash: enviada.hash });
    const preco = recibo.effectiveGasPrice ?? 0n;
    if (r.atrasada) {
      // O observador não viu o bloco a tempo (máquina suspensa, RPC fora). A inclusão é real, mas o
      // horário do recibo não foi observado: a latência vem do horário do bloco (outro relógio) e a
      // análise exclui essa linha das estatísticas de latência.
      const dentro = r.tBloco - enviada.tEnvio <= TEMPO_LIMITE_MS;
      Object.assign(linha, {
        t_recibo_utc: isoMs(r.tBloco),
        latencia_s: ((r.tBloco - enviada.tEnvio) / 1000).toFixed(3),
        bloco: recibo.blockNumber.toString(),
        gas_used: recibo.gasUsed.toString(),
        gas_price_testnet: preco.toString(),
        taxa_nativa: (recibo.gasUsed * preco).toString(),
        nome_erro: 'recibo não observado a tempo; horário do bloco',
      });
      if (!dentro) return { linha: { ...linha, status: 'falha', etapa_erro: 'recibo', categoria_falha: FALHA_TEMPO_LIMITE.categoria }, recibo };
      if (recibo.status === 'success') return { linha: { ...linha, status: 'confirmada' }, recibo };
    } else Object.assign(linha, {
      t_recibo_utc: isoMs(r.tRecibo),
      latencia_s: ((r.tRecibo - enviada.tEnvio) / 1000).toFixed(3),
      bloco: recibo.blockNumber.toString(),
      gas_used: recibo.gasUsed.toString(),
      gas_price_testnet: preco.toString(),
      taxa_nativa: (recibo.gasUsed * preco).toString(),
    });
    if (recibo.status === 'success') return { linha: { ...linha, status: 'confirmada' }, recibo };
    const nome = await this.motivoRevert(enviada, recibo);
    const c = classificarRecibo({ gasUsed: recibo.gasUsed, gasLimit: enviada.tx.gas, nome });
    return { linha: { ...linha, status: 'falha', etapa_erro: 'recibo', nome_erro: c.nome, categoria_falha: c.categoria }, recibo };
  }

  /** Reexecuta a chamada no estado do bloco anterior para recuperar o nome do erro. */
  async motivoRevert(enviada, recibo) {
    try {
      await this.leitura.call({ account: enviada.conta.address, to: enviada.tx.to, data: enviada.tx.data, gas: enviada.tx.gas, blockNumber: recibo.blockNumber - 1n });
      return null;
    } catch (erro) {
      const c = classificarErro(erro, this.abis.erros);
      return c.categoria === 'A' ? c.nome : null;
    }
  }

  /** Atalho para uma transação sequencial: prepara, envia, espera. */
  async executar(params, base) {
    const p = await this.preparar(params);
    const e = await this.enviar(p);
    return this.concluir(e, base);
  }

  idOferta(recibo) {
    for (const log of recibo?.logs ?? []) {
      try {
        const ev = decodeEventLog({ abi: this.abis.oferta, data: log.data, topics: log.topics });
        if (ev.eventName === 'OfferCreated') return ev.args.offerId;
      } catch {
        /* outro evento */
      }
    }
    return null;
  }
}
