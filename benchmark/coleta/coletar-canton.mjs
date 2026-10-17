// Coleta T1 e T2 na Canton (LocalNet do cn-quickstart) pela JSON Ledger API v2 (INTER-14).
// Mesmo CSV das redes EVM; as colunas de gas ficam vazias.
//
// [CONFERIR] Os caminhos e o formato dos comandos seguem a JSON Ledger API v2 do Canton 3.x.
// Confira com `GET <api>/v2/version` e o Swagger do LocalNet (perfil swagger-ui) antes da rodada.
//
// Preparação:
//   1. Subir o LocalNet (cn-quickstart: make setup && make start).
//   2. Compilar e enviar o DAR: cd redes-locais/canton && dpm build; depois
//      curl -X POST -H "Authorization: Bearer $CANTON_TOKEN" --data-binary @.daml/dist/credit-interbank-1.0.0.dar \
//        -H 'content-type: application/octet-stream' $CANTON_API/v2/packages
//   3. Variáveis no .env: CANTON_API (ex.: http://localhost:3975), CANTON_TOKEN, CANTON_USER_ID.
// Uso:
//   node coleta/coletar-canton.mjs [--teste T1|T2|todos] [--reduzida]
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { ArquivoCsv, PASTA_DADOS, argumentos, dataUtc, esperar, isoMs } from './lib/comum.mjs';
import { PLANOS, totalAceitesT2 } from './coletar-evm.mjs';
import { ERROS_CONTRATO } from './lib/falhas.mjs';

const API = process.env.CANTON_API || 'http://localhost:3975';
const TOKEN = process.env.CANTON_TOKEN || '';
const USUARIO = process.env.CANTON_USER_ID || 'participant_admin';
// Atenção: no .env o valor precisa de aspas ("#credit-interbank"); sem elas o dotenv lê o # como comentário.
const PACOTE = process.env.CANTON_PACOTE || '#credit-interbank';
const TEMPO_LIMITE_MS = Number(process.env.TEMPO_LIMITE_S || 300) * 1000;
const tpl = (nome) => `${PACOTE}:CreditInterbank:${nome}`;

// Categorias da seção 5 a partir do código de erro da Canton.
export function classificarCanton(status, corpo) {
  const texto = typeof corpo === 'string' ? corpo : JSON.stringify(corpo ?? {});
  for (const nome of ERROS_CONTRATO) if (texto.includes(nome)) return { categoria: 'A', nome };
  if (/CONTRACT_NOT_FOUND|CONTRACT_NOT_ACTIVE|LOCAL_VERDICT_LOCKED_CONTRACTS|INCONSISTENT_CONTRACT/.test(texto)) {
    return { categoria: 'A', nome: texto.match(/[A-Z_]{8,}/)?.[0] ?? 'contrato inativo' };
  }
  if (status === 429 || /RESOURCE_EXHAUSTED|PARTICIPANT_BACKPRESSURE/.test(texto)) return { categoria: 'C', nome: texto.match(/[A-Z_]{8,}/)?.[0] ?? `HTTP ${status}` };
  if (status === 401 || status === 403 || /PERMISSION_DENIED|UNAUTHENTICATED|INVALID_ARGUMENT/.test(texto)) {
    const causa = typeof corpo === 'object' && corpo?.cause ? `: ${String(corpo.cause).slice(0, 120)}` : '';
    return { categoria: 'B', nome: `${texto.match(/[A-Z_]{8,}/)?.[0] ?? `HTTP ${status}`}${causa}` };
  }
  if (/SUBMISSION_TIMEOUT|REQUEST_TIME_OUT|TIMEOUT|SEQUENCER_.*UNAVAILABLE|NOT_SEQUENCED/i.test(texto)) return { categoria: 'D', nome: texto.match(/[A-Z_]{8,}/)?.[0] ?? 'tempo limite' };
  return { categoria: 'X', nome: texto.slice(0, 160) };
}

async function chamar(caminho, corpo, metodo = 'POST') {
  const r = await fetch(`${API}${caminho}`, {
    method: metodo,
    headers: { 'content-type': 'application/json', ...(TOKEN ? { authorization: `Bearer ${TOKEN}` } : {}) },
    body: corpo === undefined ? undefined : JSON.stringify(corpo),
    signal: AbortSignal.timeout(TEMPO_LIMITE_MS),
  });
  const texto = await r.text();
  let json;
  try {
    json = JSON.parse(texto);
  } catch {
    json = texto;
  }
  return { status: r.status, ok: r.ok, json };
}

async function alocarParte(dica) {
  const r = await chamar('/v2/parties', { partyIdHint: dica, identityProviderId: '' });
  if (!r.ok) throw new Error(`Alocar parte ${dica}: HTTP ${r.status} ${JSON.stringify(r.json)}`);
  return r.json.partyDetails?.party ?? r.json.party;
}

function criados(json, nomeTemplate) {
  const eventos = json?.transaction?.events ?? [];
  return eventos
    .map((e) => e.CreatedEvent ?? e.created)
    .filter((e) => e && String(e.templateId).endsWith(`:${nomeTemplate}`))
    .map((e) => e.contractId);
}

/** Envia um comando e mede a latência até a resposta do submit-and-wait (após o commit). */
async function submeter({ actAs, comando, base, funcao }) {
  const corpo = { commands: { commands: [comando], commandId: randomUUID(), userId: USUARIO, actAs: [actAs], readAs: [] } };
  const tEnvio = Date.now();
  let r;
  try {
    r = await chamar('/v2/commands/submit-and-wait-for-transaction', corpo);
  } catch (e) {
    const c = e.name === 'TimeoutError' ? { categoria: 'D', nome: 'sem resposta no tempo limite' } : { categoria: 'C', nome: String(e.message).slice(0, 160) };
    return { linha: { ...base, funcao, conta: actAs, t_envio_utc: isoMs(tEnvio), status: 'falha', etapa_erro: 'envio', nome_erro: c.nome, categoria_falha: c.categoria } };
  }
  const tRecibo = Date.now();
  const linha = { ...base, funcao, conta: actAs, t_envio_utc: isoMs(tEnvio) };
  if (!r.ok) {
    const c = classificarCanton(r.status, r.json);
    return { linha: { ...linha, status: 'falha', etapa_erro: 'envio', nome_erro: c.nome, categoria_falha: c.categoria } };
  }
  return {
    json: r.json,
    linha: {
      ...linha,
      tx_hash: r.json?.transaction?.updateId ?? '',
      t_recibo_utc: isoMs(tRecibo),
      latencia_s: ((tRecibo - tEnvio) / 1000).toFixed(3),
      bloco: r.json?.transaction?.offset ?? '',
      status: 'confirmada',
    },
  };
}

const exercer = (templateId, contractId, choice, choiceArgument) => ({ ExerciseCommand: { templateId, contractId, choice, choiceArgument } });
const criar = (templateId, createArguments) => ({ CreateCommand: { templateId, createArguments } });

async function cicloOferta({ partes, saldo, tomador, base, csv }) {
  const ap = await submeter({ actAs: partes.ofertante, funcao: 'approve', base, comando: exercer(tpl('BRLHolding'), saldo, 'Approve', { borrower: tomador, value: '100' }) });
  csv?.escrever(ap.linha);
  if (ap.linha.status !== 'confirmada') return { saldo };
  const aprovados = criados(ap.json, 'BRLHolding');
  // O primeiro BRLHolding criado é o aprovado; o segundo, se existir, é o troco.
  const [aprovado, troco] = aprovados;
  const expira = new Date(Date.now() + 86_400_000).toISOString();
  const cr = await submeter({
    actAs: partes.ofertante, funcao: 'createOffer', base,
    comando: criar(tpl('Offer'), { admin: partes.admin, lender: partes.ofertante, borrower: tomador, amount: '100', rateCDI: '10000', term: '1', expiresAt: expira, fundsCid: aprovado }),
  });
  const oferta = criados(cr.json, 'Offer')[0];
  cr.linha.offer_id = oferta ?? '';
  csv?.escrever(cr.linha);
  return { saldo: troco ?? saldo, oferta };
}

async function main() {
  const a = argumentos();
  const teste = (a.teste ?? 'todos').toUpperCase();
  const plano = a.reduzida ? PLANOS.reduzido : PLANOS.completo;
  const dia = a.data ?? dataUtc();
  const csv = new ArquivoCsv(path.join(a.saida ?? PASTA_DADOS, `medicoes_canton_${dia}.csv`));
  const preparo = new ArquivoCsv(path.join(a.saida ?? PASTA_DADOS, `preparo_canton_${dia}.csv`));
  const versao = await chamar('/v2/version', undefined, 'GET');
  console.log('Ledger API:', versao.status, JSON.stringify(versao.json).slice(0, 120));
  const arquivoMeta = path.join(a.saida ?? PASTA_DADOS, `metadados_canton_${dia}.json`);
  const janelas = {};
  const gravarMeta = (extra = {}) => fs.writeFileSync(arquivoMeta, `${JSON.stringify({
    rede: 'canton',
    nome: 'Canton',
    ambiente: process.env.CANTON_AMBIENTE || 'dpm sandbox: participante, sequencer e mediator num processo local',
    api: API,
    tipo_rpc: 'JSON Ledger API v2 local, sem autenticação',
    versao_cliente: `Canton ${versao.json?.version ?? '?'}`,
    maquina: { hostname: os.hostname(), plataforma: `${os.platform()} ${os.release()}`, cpus: os.cpus().length },
    pacote: PACOTE,
    plano: plano,
    tempo_limite_s: TEMPO_LIMITE_MS / 1000,
    janelas,
    ...extra,
  }, null, 2)}\n`);
  gravarMeta();

  // Partes e estado inicial iguais aos das redes EVM: limite de R$ 5 milhões, saldo de R$ 10 milhões.
  // Um tomador por aceite simultâneo no T2: aceites do mesmo tomador disputariam o mesmo CreditLimit.
  const sufixo = Date.now().toString(36);
  const nT2 = Math.max(...plano.lotesT2);
  const partes = { admin: await alocarParte(`admin-${sufixo}`), ofertante: await alocarParte(`bancoA-${sufixo}`), tomador: await alocarParte(`bancoB-${sufixo}`), tomadoresT2: [] };
  for (let k = 0; k < nT2; k++) partes.tomadoresT2.push(await alocarParte(`tomador${k + 1}-${sufixo}`));
  const pBase = { rede: 'canton', teste: 'preparo', lote: '', rodada: 0 };
  const limite = {};
  for (const t of [partes.tomador, ...partes.tomadoresT2]) {
    const r = await submeter({ actAs: partes.admin, funcao: 'setCreditLimit', base: pBase, comando: criar(tpl('CreditLimit'), { admin: partes.admin, borrower: t, available: '500000000' }) });
    preparo.escrever(r.linha);
    limite[t] = criados(r.json, 'CreditLimit')[0];
  }
  const m = await submeter({ actAs: partes.admin, funcao: 'mint', base: pBase, comando: criar(tpl('BRLHolding'), { admin: partes.admin, owner: partes.ofertante, amount: '1000000000', spender: null }) });
  preparo.escrever(m.linha);
  let saldo = criados(m.json, 'BRLHolding')[0];

  if (teste === 'T1' || teste === 'TODOS') {
    const iniT1 = Date.now();
    for (let i = 1; i <= plano.ciclosT1; i++) {
      const base = { rede: 'canton', teste: 'T1', lote: '', rodada: i };
      const c = await cicloOferta({ partes, saldo, tomador: partes.tomador, base, csv });
      saldo = c.saldo;
      if (!c.oferta) continue;
      const ac = await submeter({ actAs: partes.tomador, funcao: 'acceptOffer', base: { ...base, offer_id: c.oferta }, comando: exercer(tpl('Offer'), c.oferta, 'AcceptOffer', { limitCid: limite[partes.tomador] }) });
      csv.escrever(ac.linha);
      if (ac.linha.status === 'confirmada') limite[partes.tomador] = criados(ac.json, 'CreditLimit')[0];
      console.log(`T1 ciclo ${i}: ${ac.linha.status} ${ac.linha.latencia_s ?? ''}s ${ac.linha.nome_erro ?? ''}`);
    }
    for (let i = 1; i <= plano.cancelamentosT1; i++) {
      const base = { rede: 'canton', teste: 'T1', lote: '', rodada: plano.ciclosT1 + i };
      const c = await cicloOferta({ partes, saldo, tomador: partes.tomador, base, csv: null });
      saldo = c.saldo;
      if (!c.oferta) continue;
      const ca = await submeter({ actAs: partes.ofertante, funcao: 'cancelOffer', base: { ...base, offer_id: c.oferta }, comando: exercer(tpl('Offer'), c.oferta, 'CancelOffer', {}) });
      csv.escrever(ca.linha);
    }
    janelas.T1 = { inicio_utc: isoMs(iniT1), fim_utc: isoMs(Date.now()) };
    gravarMeta();
  }

  if (teste === 'T2' || teste === 'TODOS') {
    // Preparação fora da medição: uma oferta aprovada por aceite, dirigida ao tomador que vai aceitá-la.
    const ofertas = [];
    for (let k = 0; k < totalAceitesT2(plano); k++) {
      const tomador = partes.tomadoresT2[k % nT2];
      const c = await cicloOferta({ partes, saldo, tomador, base: pBase, csv: preparo });
      saldo = c.saldo;
      if (c.oferta) ofertas.push({ id: c.oferta, tomador });
    }
    let cursor = 0;
    const iniT2 = Date.now();
    for (const lote of plano.lotesT2) {
      for (let rodada = 1; rodada <= plano.rodadasT2; rodada++) {
        const fatia = ofertas.slice(cursor, cursor + lote);
        cursor += lote;
        const feitas = await Promise.all(fatia.map((o) => submeter({
          actAs: o.tomador, funcao: 'acceptOffer', base: { rede: 'canton', teste: 'T2', lote, rodada, offer_id: o.id },
          comando: exercer(tpl('Offer'), o.id, 'AcceptOffer', { limitCid: limite[o.tomador] }),
        })));
        feitas.forEach((f, k) => {
          csv.escrever(f.linha);
          if (f.linha.status === 'confirmada') limite[fatia[k].tomador] = criados(f.json, 'CreditLimit')[0];
        });
        console.log(`T2 lote ${lote} rodada ${rodada}: ${feitas.filter((f) => f.linha.status === 'confirmada').length}/${lote}`);
        await esperar(2000);
      }
    }
    janelas.T2 = { inicio_utc: isoMs(iniT2), fim_utc: isoMs(Date.now()) };
    gravarMeta({ n_tomadores_t2: nT2 });
  }
  console.log(`Dados em ${csv.arquivo}`);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((e) => {
    console.error(e);
    process.exit(1);
  });
}
