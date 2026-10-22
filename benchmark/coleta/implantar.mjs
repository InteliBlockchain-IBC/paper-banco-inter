// Implantação nova em cada rede com o script do time, sem alterar o código (decisões B e D).
// Gera script/config/<rede>.json com as mesmas instituições e valores em todas as redes e roda
//   forge script script/Deploy.s.sol --rpc-url <rpc> --broadcast
// no repositório do contrato. O resultado fica em deployments/<rede>.json.
//   node coleta/implantar.mjs --rede fuji
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { PASTA_DADOS, REPO_WEB3, argumentos, carregarRede, contas, nomeImplantacao } from './lib/comum.mjs';

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
  // Nome próprio (bench-<rede>): nunca sobrescreve a implantação oficial do time (ex.: sepolia.json).
  const nome = nomeImplantacao(rede.id);
  const arquivo = path.join(REPO_WEB3, 'script', 'config', `${nome}.json`);
  fs.writeFileSync(arquivo, `${JSON.stringify(configuracao(rede, c), null, 2)}\n`);
  console.log(`Configuração gravada em ${path.relative(process.cwd(), arquivo)}`);

  const args = ['script', 'script/Deploy.s.sol', '--rpc-url', rede.rpc, '--broadcast', '--slow', '--private-key', c.chaveAdmin()];
  // Redes cujas regras de gas mudaram em relação à simulação local do forge (ex.: Sepolia pós-Glamsterdam).
  if (rede.multiplicadorGasImplantacao) args.push('--gas-estimate-multiplier', String(rede.multiplicadorGasImplantacao));
  // O registro do forge vai para dados/implantacoes/, e não para o broadcast/ versionado do time.
  const registro = path.join(PASTA_DADOS, 'implantacoes');
  fs.mkdirSync(registro, { recursive: true });
  const r = spawnSync('forge', args, { cwd: REPO_WEB3, stdio: 'inherit', env: { ...process.env, DEPLOY_ENV: nome, FOUNDRY_BROADCAST: path.join(registro, 'broadcast') } });
  if (r.status !== 0) process.exit(r.status ?? 1);
  const impl = path.join(REPO_WEB3, 'deployments', `${nome}.json`);
  fs.copyFileSync(impl, path.join(registro, `${rede.id}.json`));
  console.log(`Endereços em ${impl} e em dados/implantacoes/${rede.id}.json`);
}

if (import.meta.url === `file://${process.argv[1]}`) main();
