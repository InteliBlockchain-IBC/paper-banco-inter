// Peças compartilhadas pelos scripts de coleta: configuração das redes, contas,
// ABIs, CSV no formato da seção 6.1 do roteiro e utilitários de tempo.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import dotenv from 'dotenv';
import { createPublicClient, defineChain, encodePacked, http, keccak256 } from 'viem';
import { mnemonicToAccount, privateKeyToAccount } from 'viem/accounts';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
export const RAIZ = path.resolve(AQUI, '..', '..');
dotenv.config({ path: path.join(RAIZ, '.env') });

export const REPO_WEB3 = path.resolve(RAIZ, process.env.WEB3_REPO ?? '../../projeto-inter-web3');
export const PASTA_DADOS = path.join(RAIZ, 'dados');

// Valores fixos de todas as ofertas, em todas as redes (seção 4.1, item 4).
export const OFERTA = Object.freeze({
  amount: 100n, // R$ 1,00 (BRLt tem 2 casas decimais)
  rateCDI: 10000n, // 100% do CDI, em pontos-base
  term: 1n, // overnight
  validityWindow: 86400n, // 24 h
});

// Índices de derivação das contas a partir do MNEMONIC (as mesmas funções em todas as redes).
export const PAPEIS = Object.freeze({ admin: 0, ofertante: 1, tomador: 2, primeiroTomadorT2: 3 });

export function carregarRedes() {
  return JSON.parse(fs.readFileSync(path.join(RAIZ, 'config', 'redes.json'), 'utf8'));
}

export function carregarRede(id) {
  const redes = carregarRedes();
  const rede = redes[id];
  if (!rede) throw new Error(`Rede desconhecida: ${id}. Opções: ${Object.keys(redes).join(', ')}`);
  const rpc = process.env[rede.rpcEnv] || rede.rpcPadrao;
  const tipoRpc = process.env[rede.rpcEnv] ? 'definido no .env' : 'público padrão';
  return { id, ...rede, rpc, tipoRpc };
}

export function cadeia(rede) {
  return defineChain({
    id: rede.chainId,
    name: rede.nome,
    nativeCurrency: { name: rede.simbolo, symbol: rede.simbolo, decimals: 18 },
    rpcUrls: { default: { http: [rede.rpc] } },
  });
}

// Leituras podem ser repetidas em caso de erro do RPC. Envios não: um 429 no envio
// precisa aparecer como falha da categoria C (seção 5), e não ser escondido por uma nova tentativa.
export function clientes(rede) {
  const chain = cadeia(rede);
  const leitura = createPublicClient({ chain, transport: http(rede.rpc, { retryCount: 5, retryDelay: 300, timeout: 30_000 }) });
  const envio = createPublicClient({ chain, transport: http(rede.rpc, { retryCount: 0, timeout: 30_000 }) });
  return { chain, leitura, envio };
}

export function numTomadoresT2() {
  return Number(process.env.N_TOMADORES_T2 ?? 10);
}

/** Chave privada da carteira com faucet: `<REDE>_PRIVATE_KEY` (ex.: SEPOLIA_PRIVATE_KEY) ou PRIVATE_KEY. */
export function chavePrivada(redeId) {
  const especifica = redeId ? process.env[`${redeId.toUpperCase()}_PRIVATE_KEY`] : undefined;
  const k = (especifica || process.env.PRIVATE_KEY || '').trim();
  if (!k) return null;
  return k.startsWith('0x') ? k : `0x${k}`;
}

/**
 * Contas do experimento (as mesmas funções em todas as redes, seção 4.1).
 * Com PRIVATE_KEY: essa carteira é o admin e as outras contas são derivadas dela de forma
 * determinística (keccak256(chave, "benchmark-redes", índice)); o admin financia todas.
 * Sem PRIVATE_KEY: tudo sai do MNEMONIC (índices 0, 1, 2, 3...).
 */
export function contas(redeId) {
  const chave = chavePrivada(redeId);
  const mnemonic = process.env.MNEMONIC;
  if (!chave && !mnemonic) throw new Error('Defina PRIVATE_KEY (carteira com faucet) ou MNEMONIC no .env.');
  const derivada = (i) => privateKeyToAccount(keccak256(encodePacked(['bytes32', 'string', 'uint256'], [chave, 'benchmark-redes', BigInt(i)])));
  const conta = chave
    ? (i) => (i === PAPEIS.admin ? privateKeyToAccount(chave) : derivada(i))
    : (i) => mnemonicToAccount(mnemonic, { addressIndex: i });
  const chaveDe = chave
    ? (i) => (i === PAPEIS.admin ? chave : keccak256(encodePacked(['bytes32', 'string', 'uint256'], [chave, 'benchmark-redes', BigInt(i)])))
    : (i) => `0x${Buffer.from(mnemonicToAccount(mnemonic, { addressIndex: i }).getHdKey().privateKey).toString('hex')}`;
  const tomadoresT2 = Array.from({ length: numTomadoresT2() }, (_, k) => conta(PAPEIS.primeiroTomadorT2 + k));
  return {
    origem: chave ? 'PRIVATE_KEY' : 'MNEMONIC',
    admin: conta(PAPEIS.admin),
    ofertante: conta(PAPEIS.ofertante),
    tomador: conta(PAPEIS.tomador),
    tomadoresT2,
    chaveAdmin: () => chaveDe(PAPEIS.admin),
    todas() {
      return [this.admin, this.ofertante, this.tomador, ...this.tomadoresT2];
    },
  };
}

export function carregarAbis() {
  const ler = (nome) => JSON.parse(fs.readFileSync(path.join(REPO_WEB3, 'abi', `${nome}.json`), 'utf8'));
  const oferta = ler('CreditInterbankOffer');
  const brl = ler('BRLToken');
  const posicao = ler('CDIPositionToken');
  // ABI combinada só com os erros, para decodificar reverts vindos de qualquer contrato do ciclo.
  const erros = [...oferta, ...brl, ...posicao].filter((x) => x.type === 'error');
  const unicos = [...new Map(erros.map((e) => [`${e.name}(${e.inputs.map((i) => i.type)})`, e])).values()];
  return { oferta, brl, posicao, erros: unicos };
}

export function carregarImplantacao(redeId) {
  const arquivo = path.join(REPO_WEB3, 'deployments', `${redeId}.json`);
  if (!fs.existsSync(arquivo)) throw new Error(`Sem implantação para ${redeId}. Rode \`npm run implantar -- --rede ${redeId}\`.`);
  return JSON.parse(fs.readFileSync(arquivo, 'utf8'));
}

// ---------------------------------------------------------------------------
// CSV (seção 6.1). As duas últimas colunas são extras deste coletor:
// gas_limit (a Monad cobra pelo limite, não pelo gas usado) e nonce (auditoria do T2).
// ---------------------------------------------------------------------------
export const COLUNAS = [
  'rede', 'teste', 'lote', 'rodada', 'funcao', 'conta', 'offer_id', 'tx_hash',
  't_envio_utc', 't_recibo_utc', 'latencia_s', 'bloco', 'status', 'etapa_erro',
  'nome_erro', 'categoria_falha', 'gas_used', 'gas_price_testnet', 'taxa_nativa',
  'gas_limit', 'nonce',
];

function celula(v) {
  if (v === undefined || v === null) return '';
  const s = String(v);
  return /[",\n]/.test(s) ? `"${s.replaceAll('"', '""')}"` : s;
}

export class ArquivoCsv {
  constructor(arquivo, colunas = COLUNAS) {
    this.arquivo = arquivo;
    this.colunas = colunas;
    fs.mkdirSync(path.dirname(arquivo), { recursive: true });
    if (!fs.existsSync(arquivo)) fs.writeFileSync(arquivo, `${colunas.join(',')}\n`);
  }

  escrever(linha) {
    const extras = Object.keys(linha).filter((k) => !this.colunas.includes(k));
    if (extras.length) throw new Error(`Colunas fora do formato: ${extras.join(', ')}`);
    fs.appendFileSync(this.arquivo, `${this.colunas.map((c) => celula(linha[c])).join(',')}\n`);
  }
}

export function dataUtc(d = new Date()) {
  return d.toISOString().slice(0, 10);
}

export function isoMs(ms) {
  return new Date(ms).toISOString();
}

export const esperar = (ms) => new Promise((r) => setTimeout(r, ms));

export function argumentos(argv = process.argv.slice(2)) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const chave = a.slice(2);
      const prox = argv[i + 1];
      if (prox === undefined || prox.startsWith('--')) out[chave] = true;
      else {
        out[chave] = prox;
        i++;
      }
    } else out._.push(a);
  }
  return out;
}

export function ocultarChave(url) {
  // Remove chaves de API do endereço de RPC antes de gravar os metadados.
  return url.replace(/(\/v\d+\/|\/v2\/|\/)([A-Za-z0-9_-]{20,})(\/?$)/, '$1<chave>$3');
}
