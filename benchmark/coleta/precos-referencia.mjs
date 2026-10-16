// Preço de referência do gas na mainnet e cotação do token nativo (seção 3.3, C4-M1).
// Cada execução acrescenta uma amostra; rode durante a janela de coleta e a análise usa a mediana.
//   node coleta/precos-referencia.mjs                       uma amostra de cada rede EVM pública
//   node coleta/precos-referencia.mjs --amostras 12 --intervalo 300   12 amostras, a cada 5 min
import fs from 'node:fs';
import path from 'node:path';
import { createPublicClient, http } from 'viem';
import { PASTA_DADOS, argumentos, carregarRedes, dataUtc, esperar } from './lib/comum.mjs';

const FONTE_COTACAO = 'https://api.coingecko.com/api/v3/simple/price';

// Preço efetivo típico de uma transação: base fee do bloco + gorjeta mediana (percentil 50).
async function precoGas(rpc) {
  const cli = createPublicClient({ transport: http(rpc, { retryCount: 3 }) });
  const h = await cli.getFeeHistory({ blockCount: 20, rewardPercentiles: [50] });
  const efetivos = h.baseFeePerGas.slice(0, -1).map((b, i) => b + (h.reward?.[i]?.[0] ?? 0n));
  efetivos.sort((a, b) => (a < b ? -1 : a > b ? 1 : 0));
  return { mediana_wei: efetivos[Math.floor(efetivos.length / 2)].toString(), bloco_final: h.oldestBlock + BigInt(efetivos.length) - 1n };
}

async function cotacoes(ids) {
  const url = `${FONTE_COTACAO}?ids=${ids.join(',')}&vs_currencies=usd,brl`;
  const r = await fetch(url, { headers: { accept: 'application/json' } });
  if (!r.ok) throw new Error(`Cotação: HTTP ${r.status}`);
  return { url, dados: await r.json() };
}

async function amostra() {
  const redes = Object.entries(carregarRedes()).filter(([, r]) => r.mainnet);
  const momento = new Date().toISOString();
  const { url, dados } = await cotacoes(redes.map(([, r]) => r.mainnet.coingeckoId));
  const porRede = {};
  for (const [id, r] of redes) {
    const rpc = process.env[r.mainnet.rpcEnv] || r.mainnet.rpcPadrao;
    try {
      const g = await precoGas(rpc);
      porRede[id] = {
        mainnet_chain_id: r.mainnet.chainId,
        rpc_mainnet: rpc,
        gas_preco_wei: g.mediana_wei,
        bloco_referencia: g.bloco_final.toString(),
        token: r.mainnet.coingeckoId,
        cotacao_usd: dados[r.mainnet.coingeckoId]?.usd ?? null,
        cotacao_brl: dados[r.mainnet.coingeckoId]?.brl ?? null,
      };
    } catch (e) {
      porRede[id] = { erro: e.shortMessage ?? e.message };
    }
  }
  return { momento_utc: momento, fonte_gas: 'eth_feeHistory (20 blocos, base fee + gorjeta p50)', fonte_cotacao: url, redes: porRede };
}

async function main() {
  const a = argumentos();
  const n = Number(a.amostras ?? 1);
  const intervalo = Number(a.intervalo ?? 300) * 1000;
  const arquivo = path.join(PASTA_DADOS, `precos_referencia_${a.data ?? dataUtc()}.json`);
  for (let i = 0; i < n; i++) {
    const atual = fs.existsSync(arquivo) ? JSON.parse(fs.readFileSync(arquivo, 'utf8')) : { amostras: [] };
    const s = await amostra();
    atual.amostras.push(s);
    fs.mkdirSync(PASTA_DADOS, { recursive: true });
    fs.writeFileSync(arquivo, `${JSON.stringify(atual, null, 2)}\n`);
    console.log(`[${s.momento_utc}] amostra ${i + 1}/${n}:`, Object.entries(s.redes).map(([k, v]) => `${k} ${v.gas_preco_wei ?? v.erro} wei @ US$ ${v.cotacao_usd}`).join(' | '));
    if (i < n - 1) await esperar(intervalo);
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
