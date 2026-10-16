// Implantação nova em cada rede com o script do time, sem alterar o código (decisões B e D).
// Gera script/config/<rede>.json com as mesmas instituições e valores em todas as redes e roda
//   forge script script/Deploy.s.sol --rpc-url <rpc> --broadcast
// no repositório do contrato. O resultado fica em deployments/<rede>.json.
//   node src/implantar.mjs --rede fuji
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { REPO_WEB3, argumentos, carregarRede, contas } from './lib/comum.mjs';

// Valores padrão do arquivo de configuração do time: limite de R$ 5 milhões e saldo de R$ 10 milhões.
const LIMITE = 500_000_000;
const SALDO = 1_000_000_000;

export function configuracao(rede, c) {
  const inst = (conta) => ({ wallet: conta.address, creditLimit: LIMITE, brlMint: SALDO });
  return {
    chainId: rede.chainId,
    institutions: [inst(c.ofertante), inst(c.tomador), ...c.tomadoresT2.map(inst)],
  };
}

function main() {
  const a = argumentos();
  if (!a.rede) throw new Error('Informe --rede');
  const rede = carregarRede(a.rede);
  const c = contas(rede.id);
  const arquivo = path.join(REPO_WEB3, 'script', 'config', `${rede.id}.json`);
  fs.writeFileSync(arquivo, `${JSON.stringify(configuracao(rede, c), null, 2)}\n`);
  console.log(`Configuração gravada em ${path.relative(process.cwd(), arquivo)}`);

  const args = ['script', 'script/Deploy.s.sol', '--rpc-url', rede.rpc, '--broadcast', '--slow', '--private-key', c.chaveAdmin()];
  if (rede.cobrancaGas === 'gratis') args.push('--with-gas-price', '0', '--priority-gas-price', '0');
  const r = spawnSync('forge', args, { cwd: REPO_WEB3, stdio: 'inherit', env: { ...process.env, DEPLOY_ENV: rede.id } });
  if (r.status !== 0) process.exit(r.status ?? 1);
  console.log(`Endereços em ${path.join('deployments', `${rede.id}.json`)} (repositório do contrato)`);
}

if (import.meta.url === `file://${process.argv[1]}`) main();
