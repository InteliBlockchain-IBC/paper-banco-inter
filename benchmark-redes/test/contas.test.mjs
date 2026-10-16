// Derivação das contas a partir da PRIVATE_KEY da carteira com faucet.
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { privateKeyToAccount } from 'viem/accounts';
import { contas } from '../src/lib/comum.mjs';

const CHAVE = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d'; // chave pública de teste do Anvil

function comChave(fn, extra = {}) {
  const antes = { ...process.env };
  delete process.env.MNEMONIC;
  for (const k of Object.keys(process.env)) if (k.endsWith('PRIVATE_KEY')) delete process.env[k];
  Object.assign(process.env, { PRIVATE_KEY: CHAVE, N_TOMADORES_T2: '10', ...extra });
  try {
    return fn();
  } finally {
    process.env = antes;
  }
}

test('a PRIVATE_KEY é o admin e as outras 12 contas são derivadas dela', () => {
  comChave(() => {
    const c = contas('sepolia');
    assert.equal(c.origem, 'PRIVATE_KEY');
    assert.equal(c.admin.address, privateKeyToAccount(CHAVE).address);
    const enderecos = c.todas().map((a) => a.address);
    assert.equal(enderecos.length, 13);
    assert.equal(new Set(enderecos).size, 13);
    assert.equal(c.chaveAdmin(), CHAVE);
  });
});

test('a derivação é determinística: mesma chave, mesmas contas em todas as execuções', () => {
  const a = comChave(() => contas('fuji').todas().map((x) => x.address));
  const b = comChave(() => contas('fuji').todas().map((x) => x.address));
  assert.deepEqual(a, b);
});

test('chave específica da rede tem prioridade sobre a geral', () => {
  const outra = '0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a';
  comChave(() => {
    assert.equal(contas('monad').admin.address, privateKeyToAccount(outra).address);
    assert.equal(contas('fuji').admin.address, privateKeyToAccount(CHAVE).address);
  }, { MONAD_PRIVATE_KEY: outra });
});
