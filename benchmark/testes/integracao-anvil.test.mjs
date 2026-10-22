// Teste de integração contra uma rede local de ensaio já implantada (Anvil).
// Pulado se a rede não estiver no ar. Para rodar:
//   anvil --port 8546 --block-time 1 --accounts 15 &
//   MNEMONIC="test test test test test test test test test test test junk" npm run implantar -- --rede anvil
//   MNEMONIC="test test test test test test test test test test test junk" npm test
import assert from 'node:assert/strict';
import { after, before, test } from 'node:test';
import { OFERTA, carregarAbis, carregarImplantacao, carregarRede, clientes, contas } from '../coleta/lib/comum.mjs';
import { Executor, ObservadorBlocos } from '../coleta/lib/transacoes.mjs';

const REDE = process.env.REDE_INTEGRACAO ?? 'anvil';
let ex;
let obs;
let impl;
let c;
let abis;
let pronto = false;

before(async () => {
  try {
    if (!process.env.MNEMONIC) return;
    // O Anvil usa o mnemonic público dele; a PRIVATE_KEY das testnets não vale aqui.
    delete process.env.PRIVATE_KEY;
    delete process.env.ANVIL_PRIVATE_KEY;
    const rede = carregarRede(REDE);
    const cli = clientes(rede);
    await cli.leitura.getChainId();
    impl = carregarImplantacao(REDE);
    abis = carregarAbis();
    c = contas('anvil');
    obs = new ObservadorBlocos(cli.leitura, rede.intervaloConsultaMs);
    await obs.iniciar();
    ex = new Executor({ rede, clientes: cli, observador: obs, abis });
    pronto = true;
  } catch {
    pronto = false;
  }
});

after(async () => {
  if (obs) await obs.parar();
});

const base = { rede: REDE, teste: 'teste', lote: '', rodada: 0 };

async function criarOferta() {
  const r = await ex.executar(
    { conta: c.ofertante, endereco: impl.CreditInterbankOffer, abi: abis.oferta, funcao: 'createOffer', args: [c.tomador.address, OFERTA.amount, OFERTA.rateCDI, OFERTA.term, OFERTA.validityWindow] },
    base,
  );
  return ex.idOferta(r.recibo);
}

test('ciclo completo confirma as três transações com latência e gas', async (t) => {
  if (!pronto) return t.skip(`rede ${REDE} fora do ar ou sem implantação`);
  const ap = await ex.executar({ conta: c.ofertante, endereco: impl.BRLToken, abi: abis.brl, funcao: 'approve', args: [impl.CreditInterbankOffer, OFERTA.amount] }, base);
  assert.equal(ap.linha.status, 'confirmada');
  const id = await criarOferta();
  assert.ok(id > 0n);
  const ac = await ex.executar({ conta: c.tomador, endereco: impl.CreditInterbankOffer, abi: abis.oferta, funcao: 'acceptOffer', args: [id] }, base);
  assert.equal(ac.linha.status, 'confirmada');
  assert.ok(Number(ac.linha.latencia_s) > 0);
  assert.ok(Number(ac.linha.gas_used) > 100_000);
});

test('aceite por quem não é o tomador falha na estimativa com NotEligibleBorrower (A)', async (t) => {
  if (!pronto) return t.skip('rede fora do ar');
  const id = await criarOferta();
  const r = await ex.executar({ conta: c.tomadoresT2[0], endereco: impl.CreditInterbankOffer, abi: abis.oferta, funcao: 'acceptOffer', args: [id] }, base);
  assert.equal(r.linha.status, 'falha');
  assert.equal(r.linha.etapa_erro, 'estimativa');
  assert.equal(r.linha.categoria_falha, 'A');
  assert.equal(r.linha.nome_erro, 'NotEligibleBorrower');
  assert.equal(r.linha.tx_hash, undefined);
});

test('revert dentro do bloco é lido do recibo e classificado pelo nome', async (t) => {
  if (!pronto) return t.skip('rede fora do ar');
  const id = await criarOferta();
  // Gas fixo pula a estimativa; sem approve, o aceite reverte no bloco por falta de allowance.
  await ex.executar({ conta: c.ofertante, endereco: impl.BRLToken, abi: abis.brl, funcao: 'approve', args: [impl.CreditInterbankOffer, 0n] }, base);
  const r = await ex.executar({ conta: c.tomador, endereco: impl.CreditInterbankOffer, abi: abis.oferta, funcao: 'acceptOffer', args: [id], gas: 300_000n }, base);
  assert.equal(r.linha.status, 'falha');
  assert.equal(r.linha.etapa_erro, 'recibo');
  assert.equal(r.linha.categoria_falha, 'A');
  assert.equal(r.linha.nome_erro, 'ERC20InsufficientAllowance');
  assert.ok(r.linha.tx_hash);
});
