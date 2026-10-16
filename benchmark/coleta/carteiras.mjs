// Contas de teste e tokens de faucet.
//   node coleta/carteiras.mjs nova                       gera um mnemonic novo, só para testnet
//   node coleta/carteiras.mjs enderecos                  lista as contas e seus papéis
//   node coleta/carteiras.mjs orcamento --rede fuji      quanto token nativo cada conta precisa, pelo gas atual
//   node coleta/carteiras.mjs saldos --rede fuji         saldo de cada conta
//   node coleta/carteiras.mjs distribuir --rede fuji     o admin envia a cada conta o que falta
//
// Fluxo: coloque no .env a PRIVATE_KEY da carteira que recebeu os faucets (ela vira o admin),
// rode `orcamento` para ver se o saldo cobre o plano e `distribuir` para financiar as outras contas.
import { createWalletClient, formatEther, http } from 'viem';
import { english, generateMnemonic } from 'viem/accounts';
import { argumentos, carregarRede, clientes, contas } from './lib/comum.mjs';
import { MULTIPLICADOR_GAS, taxas } from './lib/transacoes.mjs';
import { PLANOS, totalAceitesT2 } from './coletar-evm.mjs';

// Gas por função medido na demonstração da Sepolia de 06/10/2026 [R12]; cancelOffer e
// implantação medidos no ensaio local (Anvil). Servem só para orçar o faucet.
export const GAS_REFERENCIA = {
  approve: 46_361n,
  createOffer: 237_009n,
  acceptOffer: 172_050n,
  cancelOffer: 51_810n,
  implantacaoBase: 3_273_207n, // 3 contratos + grantRole
  implantacaoPorInstituicao: 156_454n, // registerInstitution + setCreditLimit + mint
};

export function gasPorPapel(plano, nTomadoresT2) {
  const g = GAS_REFERENCIA;
  const aceitesT2 = BigInt(totalAceitesT2(plano));
  const porTomadorT2 = (aceitesT2 + BigInt(nTomadoresT2) - 1n) / BigInt(nTomadoresT2);
  const instituicoes = BigInt(2 + nTomadoresT2);
  return {
    admin: g.implantacaoBase + g.implantacaoPorInstituicao * instituicoes,
    ofertante:
      BigInt(plano.ciclosT1) * (g.approve + g.createOffer) +
      BigInt(plano.cancelamentosT1) * (g.createOffer + g.cancelOffer) +
      g.approve + aceitesT2 * g.createOffer,
    tomador: BigInt(plano.ciclosT1) * g.acceptOffer,
    tomadorT2: porTomadorT2 * g.acceptOffer,
  };
}

// Margem sobre o preço de gas atual: o preço da testnet oscila durante a coleta.
const MARGEM = 2n;

async function orcamento(rede, plano, c) {
  const { leitura } = clientes(rede);
  const f = await taxas(leitura, rede);
  const porGas = (gas) => (gas * BigInt(Math.round(MULTIPLICADOR_GAS * 100)) * f.maxFeePerGas * MARGEM) / 100n;
  const gp = gasPorPapel(plano, c.tomadoresT2.length);
  const linhas = [
    { papel: 'admin', conta: c.admin, gas: gp.admin },
    { papel: 'ofertante', conta: c.ofertante, gas: gp.ofertante },
    { papel: 'tomador', conta: c.tomador, gas: gp.tomador },
    ...c.tomadoresT2.map((t, k) => ({ papel: `tomador_t2_${k + 1}`, conta: t, gas: gp.tomadorT2 })),
  ];
  for (const l of linhas) l.necessario = porGas(l.gas);
  return { linhas, maxFeePerGas: f.maxFeePerGas, total: linhas.reduce((s, l) => s + l.necessario, 0n) };
}

async function main() {
  const a = argumentos();
  const cmd = a._[0];
  if (cmd === 'nova') {
    const m = generateMnemonic(english);
    console.log('Mnemonic novo (USE SÓ EM TESTNET; nunca coloque fundos reais nestas contas):\n');
    console.log(`MNEMONIC="${m}"\n`);
    console.log('Copie a linha acima para o arquivo .env e rode `npm run carteiras -- enderecos`.');
    return;
  }
  const c = contas(a.rede);
  if (cmd === 'enderecos') {
    console.log(`Contas derivadas de ${c.origem}${a.rede ? ` (rede ${a.rede})` : ''}:`);
    console.log(`admin       ${c.admin.address}   <- carteira com os tokens de faucet`);
    console.log(`ofertante   ${c.ofertante.address}`);
    console.log(`tomador     ${c.tomador.address}`);
    c.tomadoresT2.forEach((t, k) => console.log(`tomador_t2_${String(k + 1).padEnd(2)} ${t.address}`));
    return;
  }
  if (!a.rede) throw new Error('Informe --rede');
  const rede = carregarRede(a.rede);
  const plano = a.reduzida ? PLANOS.reduzido : PLANOS.completo;
  const { leitura } = clientes(rede);

  if (cmd === 'orcamento' || cmd === 'saldos') {
    const o = await orcamento(rede, plano, c);
    console.log(`${rede.nome}: maxFeePerGas atual ${o.maxFeePerGas} wei, margem ${MARGEM}x, multiplicador de gas ${MULTIPLICADOR_GAS}`);
    let falta = 0n;
    for (const l of o.linhas) {
      const saldo = await leitura.getBalance({ address: l.conta.address });
      const f = l.necessario > saldo ? l.necessario - saldo : 0n;
      falta += f;
      console.log(`${l.papel.padEnd(14)} ${l.conta.address}  precisa ${formatEther(l.necessario).padStart(12)}  saldo ${formatEther(saldo).padStart(12)}  ${f ? `falta ${formatEther(f)}` : 'ok'}`);
    }
    console.log(`\nTotal necessário: ${formatEther(o.total)} ${rede.simbolo}. Falta no conjunto: ${formatEther(falta)} ${rede.simbolo}.`);
    if (rede.faucets?.length) console.log(`Faucets: ${rede.faucets.join('  ')}`);
    return;
  }

  if (cmd === 'distribuir') {
    const o = await orcamento(rede, plano, c);
    const carteira = createWalletClient({ account: c.admin, chain: clientes(rede).chain, transport: http(rede.rpc) });
    for (const l of o.linhas.slice(1)) {
      const saldo = await leitura.getBalance({ address: l.conta.address });
      if (saldo >= l.necessario) continue;
      const valor = l.necessario - saldo;
      const hash = await carteira.sendTransaction({ to: l.conta.address, value: valor });
      await leitura.waitForTransactionReceipt({ hash });
      console.log(`${l.papel.padEnd(14)} +${formatEther(valor)} ${rede.simbolo}  ${hash}`);
    }
    console.log('Distribuição concluída. Confira com `saldos`.');
    return;
  }
  throw new Error(`Comando desconhecido: ${cmd}`);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((e) => {
    console.error(e.shortMessage ?? e.message ?? e);
    process.exit(1);
  });
}
