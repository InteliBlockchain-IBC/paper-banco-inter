// Classificação de falhas da Canton (mesmas categorias da seção 5).
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { classificarCanton } from '../src/coletar-canton.mjs';

test('asserção do modelo Daml vira categoria A com o nome do erro do Solidity', () => {
  const corpo = { code: 'DAML_INTERPRETATION_ERROR', cause: 'Interpretation error: Error: User abort: InsufficientLimit' };
  assert.deepEqual(classificarCanton(400, corpo), { categoria: 'A', nome: 'InsufficientLimit' });
});

test('contrato já consumido (disputa) é regra do ledger, categoria A', () => {
  assert.equal(classificarCanton(404, { code: 'CONTRACT_NOT_FOUND' }).categoria, 'A');
});

test('sobrecarga do participante é categoria C', () => {
  assert.equal(classificarCanton(429, { code: 'PARTICIPANT_BACKPRESSURE' }).categoria, 'C');
});

test('tempo limite de sequenciamento é falha da rede (D)', () => {
  assert.equal(classificarCanton(504, { code: 'SUBMISSION_TIMEOUT' }).categoria, 'D');
});

test('token inválido é erro do cliente (B)', () => {
  assert.equal(classificarCanton(401, { code: 'UNAUTHENTICATED' }).categoria, 'B');
});
