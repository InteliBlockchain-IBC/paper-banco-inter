// Coleta T1 (sequencial) e T2 (carga simultânea) numa rede EVM, conforme as seções 4.2 e 4.3
// do roteiro de medição. Uso:
//   node coleta/coletar-evm.mjs --rede sepolia [--teste T1|T2|todos] [--reduzida]
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execSync } from 'node:child_process';
import {
  ArquivoCsv, OFERTA, PASTA_DADOS, REPO_WEB3, argumentos, carregarAbis, carregarImplantacao,
  carregarRede, clientes, contas, dataUtc, esperar, isoMs, ocultarChave,
} from './lib/comum.mjs';
import { Executor, MULTIPLICADOR_GAS, ObservadorBlocos, TEMPO_LIMITE_MS, taxas } from './lib/transacoes.mjs';

// Plano completo e reduzido (seções 4.2, 4.3 e 11).
export const PLANOS = {
  completo: { ciclosT1: 30, cancelamentosT1: 10, lotesT2: [10, 25, 50], rodadasT2: 3 },
  reduzido: { ciclosT1: 20, cancelamentosT1: 0, lotesT2: [10, 50], rodadasT2: 2 },
};

export function totalAceitesT2(plano) {
  return plano.lotesT2.reduce((s, n) => s + n, 0) * plano.rodadasT2;
}

function log(...a) {
  console.log(`[${new Date().toISOString()}]`, ...a);
}

function resumoLinha(l) {
  return `${l.funcao.padEnd(11)} ${l.status.padEnd(10)} ${l.latencia_s ? `${l.latencia_s}s` : ''} ${l.categoria_falha ? `[${l.categoria_falha}] ${l.nome_erro}` : ''}`;
}

async function metadados({ rede, cli, impl, c, plano, arquivoMeta, extra = {} }) {
  let commit = '';
  try {
    commit = execSync('git rev-parse --short HEAD', { cwd: REPO_WEB3 }).toString().trim();
  } catch {
    /* repositório sem git */
  }
  let versaoCliente = '';
  try {
    versaoCliente = await cli.leitura.request({ method: 'web3_clientVersion' });
  } catch {
    /* nem todo RPC expõe */
  }
  const anterior = fs.existsSync(arquivoMeta) ? JSON.parse(fs.readFileSync(arquivoMeta, 'utf8')) : {};
  const meta = {
    ...anterior,
    rede: rede.id,
    nome: rede.nome,
    chainId: rede.chainId,
    rpc: ocultarChave(rede.rpc),
    tipo_rpc: process.env.TIPO_RPC ?? rede.tipoRpc,
    maquina: { hostname: os.hostname(), plataforma: `${os.platform()} ${os.release()}`, cpus: os.cpus().length, regiao: process.env.REGIAO ?? '' },
    contratos: { BRLToken: impl.BRLToken, CDIPositionToken: impl.CDIPositionToken, CreditInterbankOffer: impl.CreditInterbankOffer, bloco_implantacao: impl.startBlock },
    codigo: { commit, solc: '0.8.24', otimizador_runs: 200, openzeppelin: '5.4.0', config: `script/config/${rede.id}.json` },
    contas: { admin: c.admin.address, ofertante: c.ofertante.address, tomador: c.tomador.address, tomadores_t2: c.tomadoresT2.map((a) => a.address) },
    n_tomadores_t2: c.tomadoresT2.length,
    versao_cliente: versaoCliente,
    validadores: rede.validadores ?? null,
    plano,
    multiplicador_gas: MULTIPLICADOR_GAS,
    tempo_limite_s: TEMPO_LIMITE_MS / 1000,
    intervalo_consulta_ms: rede.intervaloConsultaMs,
    cobranca_gas: rede.cobrancaGas,
    ...extra,
  };
  fs.writeFileSync(arquivoMeta, `${JSON.stringify(meta, null, 2)}\n`);
  return meta;
}

// ---------------------------------------------------------------------------
// T1: um ciclo de cada vez, esperando cada recibo (seção 4.2)
// ---------------------------------------------------------------------------
async function rodarT1({ ex, impl, abis, c, plano, csv, redeId }) {
  const base = (rodada, extra = {}) => ({ rede: redeId, teste: 'T1', lote: '', rodada, ...extra });
  const oferta = impl.CreditInterbankOffer;
  for (let i = 1; i <= plano.ciclosT1; i++) {
    const ap = await ex.executar(
      { conta: c.ofertante, endereco: impl.BRLToken, abi: abis.brl, funcao: 'approve', args: [oferta, OFERTA.amount] },
      base(i),
    );
    csv.escrever(ap.linha);
    log(`T1 ciclo ${i}`, resumoLinha(ap.linha));
    if (ap.linha.status !== 'confirmada') continue;

    const cr = await ex.executar(
      { conta: c.ofertante, endereco: oferta, abi: abis.oferta, funcao: 'createOffer', args: [c.tomador.address, OFERTA.amount, OFERTA.rateCDI, OFERTA.term, OFERTA.validityWindow] },
      base(i),
    );
    const id = ex.idOferta(cr.recibo);
    cr.linha.offer_id = id?.toString() ?? '';
    csv.escrever(cr.linha);
    log(`T1 ciclo ${i}`, resumoLinha(cr.linha));
    if (cr.linha.status !== 'confirmada' || id === null) continue;

    const ac = await ex.executar(
      { conta: c.tomador, endereco: oferta, abi: abis.oferta, funcao: 'acceptOffer', args: [id] },
      base(i, { offer_id: id.toString() }),
    );
    csv.escrever(ac.linha);
    log(`T1 ciclo ${i}`, resumoLinha(ac.linha));
  }

  for (let i = 1; i <= plano.cancelamentosT1; i++) {
    const rodada = plano.ciclosT1 + i;
    const cr = await ex.executar(
      { conta: c.ofertante, endereco: oferta, abi: abis.oferta, funcao: 'createOffer', args: [c.tomador.address, OFERTA.amount, OFERTA.rateCDI, OFERTA.term, OFERTA.validityWindow] },
      base(rodada),
    );
    const id = ex.idOferta(cr.recibo);
    cr.linha.offer_id = id?.toString() ?? '';
    csv.escrever(cr.linha);
    log(`T1 cancelamento ${i}`, resumoLinha(cr.linha));
    if (cr.linha.status !== 'confirmada' || id === null) continue;
    const ca = await ex.executar(
      { conta: c.ofertante, endereco: oferta, abi: abis.oferta, funcao: 'cancelOffer', args: [id] },
      base(rodada, { offer_id: id.toString() }),
    );
    csv.escrever(ca.linha);
    log(`T1 cancelamento ${i}`, resumoLinha(ca.linha));
  }
}

// ---------------------------------------------------------------------------
// T2: preparação fora da medição + lotes simultâneos de acceptOffer (seção 4.3)
// ---------------------------------------------------------------------------
async function prepararT2({ ex, impl, abis, c, plano, csvPreparo, redeId }) {
  const total = totalAceitesT2(plano);
  const oferta = impl.CreditInterbankOffer;
  const base = { rede: redeId, teste: 'T2-preparo', lote: '', rodada: 0 };

  // 1. Um único approve no valor total (decisão A).
  const ap = await ex.executar(
    { conta: c.ofertante, endereco: impl.BRLToken, abi: abis.brl, funcao: 'approve', args: [oferta, OFERTA.amount * BigInt(total)] },
    base,
  );
  csvPreparo.escrever(ap.linha);
  if (ap.linha.status !== 'confirmada') throw new Error(`approve do T2 falhou: ${ap.linha.nome_erro}`);

  // 2. Criar as ofertas, cada uma dirigida ao tomador que vai aceitá-la (rodízio entre os tomadores).
  // 3. Envio com controle de nonce, em blocos de 16 (limite padrão de transações pendentes por conta no Geth).
  const destino = Array.from({ length: total }, (_, k) => c.tomadoresT2[k % c.tomadoresT2.length]);
  const argsOferta = (t) => [t.address, OFERTA.amount, OFERTA.rateCDI, OFERTA.term, OFERTA.validityWindow];
  const gas = await ex.estimar({ conta: c.ofertante, endereco: oferta, abi: abis.oferta, funcao: 'createOffer', args: argsOferta(destino[0]) });
  const ofertas = [];
  const BLOCO = 16;
  for (let ini = 0; ini < total; ini += BLOCO) {
    const fees = await taxas(ex.leitura, ex.rede);
    const fatia = destino.slice(ini, ini + BLOCO);
    const prep = [];
    for (const t of fatia) prep.push(await ex.preparar({ conta: c.ofertante, endereco: oferta, abi: abis.oferta, funcao: 'createOffer', args: argsOferta(t), gas, fees }));
    const enviadas = [];
    for (const p of prep) enviadas.push(await ex.enviar(p)); // em ordem de nonce
    const feitas = await Promise.all(enviadas.map((e) => ex.concluir(e, base)));
    feitas.forEach((f, k) => {
      const id = ex.idOferta(f.recibo);
      f.linha.offer_id = id?.toString() ?? '';
      csvPreparo.escrever(f.linha);
      if (f.linha.status === 'confirmada' && id !== null) ofertas.push({ id, tomador: fatia[k] });
    });
    log(`T2 preparo: ${ofertas.length}/${total} ofertas criadas`);
  }
  if (ofertas.length < total) throw new Error(`Só ${ofertas.length} de ${total} ofertas foram criadas; confira dados/preparo_*.csv`);
  return ofertas;
}

async function rodarT2({ ex, impl, abis, plano, csv, ofertas, redeId }) {
  const oferta = impl.CreditInterbankOffer;
  let cursor = 0;
  // Gas fixo para todos os aceites, estimado uma vez com a primeira oferta (mesmo multiplicador do T1).
  const gas = await ex.estimar({ conta: ofertas[0].tomador, endereco: oferta, abi: abis.oferta, funcao: 'acceptOffer', args: [ofertas[0].id] });
  for (const lote of plano.lotesT2) {
    for (let rodada = 1; rodada <= plano.rodadasT2; rodada++) {
      const fatia = ofertas.slice(cursor, cursor + lote);
      cursor += lote;
      const fees = await taxas(ex.leitura, ex.rede);
      const prep = [];
      for (const o of fatia) prep.push(await ex.preparar({ conta: o.tomador, endereco: oferta, abi: abis.oferta, funcao: 'acceptOffer', args: [o.id], gas, fees }));
      // Disparo simultâneo: todas as transações assinadas antes, enviadas juntas.
      const inicio = Date.now();
      const enviadas = await Promise.all(prep.map((p) => ex.enviar(p)));
      const feitas = await Promise.all(enviadas.map((e, k) => ex.concluir(e, { rede: redeId, teste: 'T2', lote, rodada, offer_id: fatia[k].id.toString() })));
      for (const f of feitas) csv.escrever(f.linha);
      const ok = feitas.filter((f) => f.linha.status === 'confirmada').length;
      log(`T2 lote ${lote} rodada ${rodada}: ${ok}/${lote} confirmadas em ${((Date.now() - inicio) / 1000).toFixed(1)}s`);
      await esperar(2000); // folga entre rodadas para o mempool esvaziar
    }
  }
}

export async function main(argv) {
  const a = argumentos(argv);
  if (!a.rede) throw new Error('Informe --rede (sepolia, fuji, monad, anvil)');
  const teste = (a.teste ?? 'todos').toUpperCase();
  const plano = a.reduzida ? PLANOS.reduzido : PLANOS.completo;
  const rede = carregarRede(a.rede);
  const cli = clientes(rede);
  const chainId = await cli.leitura.getChainId();
  if (chainId !== rede.chainId) throw new Error(`RPC aponta para chainId ${chainId}, esperado ${rede.chainId}`);

  const abis = carregarAbis();
  const impl = carregarImplantacao(rede.id);
  const c = contas(rede.id);
  const dia = a.data ?? dataUtc();
  const pasta = a.saida ?? PASTA_DADOS;
  const csv = new ArquivoCsv(path.join(pasta, `medicoes_${rede.id}_${dia}.csv`));
  const csvPreparo = new ArquivoCsv(path.join(pasta, `preparo_${rede.id}_${dia}.csv`));
  const arquivoMeta = path.join(pasta, `metadados_${rede.id}_${dia}.json`);
  await metadados({ rede, cli, impl, c, plano, arquivoMeta });

  const observador = new ObservadorBlocos(cli.leitura, rede.intervaloConsultaMs);
  await observador.iniciar();
  const ex = new Executor({ rede, clientes: cli, observador, abis });
  const janelas = {};
  try {
    if (teste === 'T1' || teste === 'TODOS') {
      const ini = Date.now();
      log(`T1 em ${rede.nome}: ${plano.ciclosT1} ciclos + ${plano.cancelamentosT1} cancelamentos`);
      await rodarT1({ ex, impl, abis, c, plano, csv, redeId: rede.id });
      janelas.T1 = { inicio_utc: isoMs(ini), fim_utc: isoMs(Date.now()) };
    }
    if (teste === 'T2' || teste === 'TODOS') {
      log(`T2 em ${rede.nome}: preparando ${totalAceitesT2(plano)} ofertas`);
      const ofertas = await prepararT2({ ex, impl, abis, c, plano, csvPreparo, redeId: rede.id });
      const ini = Date.now();
      await rodarT2({ ex, impl, abis, plano, csv, ofertas, redeId: rede.id });
      janelas.T2 = { inicio_utc: isoMs(ini), fim_utc: isoMs(Date.now()) };
    }
  } finally {
    await observador.parar();
    const anterior = JSON.parse(fs.readFileSync(arquivoMeta, 'utf8'));
    await metadados({ rede, cli, impl, c, plano, arquivoMeta, extra: { janelas: { ...anterior.janelas, ...janelas }, erros_consulta_blocos: observador.errosConsulta, pausas_observador: observador.pausas } });
  }
  log(`Dados em ${csv.arquivo}`);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main(process.argv.slice(2)).catch((e) => {
    console.error(e);
    process.exit(1);
  });
}
