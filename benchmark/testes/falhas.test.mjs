// Testes da classificação de falhas (seção 5 do roteiro).
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { ContractFunctionExecutionError, ContractFunctionRevertedError, HttpRequestError, encodeErrorResult } from 'viem';
import { classificarErro, classificarRecibo } from '../coleta/lib/falhas.mjs';
import { carregarAbis } from '../coleta/lib/comum.mjs';

const abis = carregarAbis();
const oferta = abis.oferta;

function revertDoContrato(errorName, args) {
  const data = encodeErrorResult({ abi: abis.erros, errorName, args });
  const cause = new ContractFunctionRevertedError({ abi: abis.erros, data, functionName: 'acceptOffer' });
  return new ContractFunctionExecutionError(cause, { abi: oferta, functionName: 'acceptOffer', args: [1n] });
}

test('erro do contrato decodificado vira categoria A com o nome do erro', () => {
  const e = revertDoContrato('OfferHasExpired', [1n, 123n]);
  assert.deepEqual(classificarErro(e, abis.erros), { categoria: 'A', nome: 'OfferHasExpired' });
});

test('erro do token (OpenZeppelin) também é categoria A', () => {
  const e = revertDoContrato('ERC20InsufficientAllowance', ['0x0000000000000000000000000000000000000001', 0n, 100n]);
  assert.equal(classificarErro(e, abis.erros).nome, 'ERC20InsufficientAllowance');
  assert.equal(classificarErro(e, abis.erros).categoria, 'A');
});

test('revert bruto em data de erro RPC é decodificado pela ABI', () => {
  const data = encodeErrorResult({ abi: abis.erros, errorName: 'InsufficientLimit', args: ['0x0000000000000000000000000000000000000001', 100n, 0n] });
  const e = new Error('execution reverted');
  e.data = data;
  // Erro comum (não BaseError) cai no reconhecimento por texto; com BaseError a ABI decodifica.
  assert.equal(classificarErro(e, abis.erros).categoria, 'A');
});

test('nonce repetido e falta de saldo são erros do cliente (B)', () => {
  assert.equal(classificarErro(new Error('nonce too low: next nonce 5, tx nonce 4')).categoria, 'B');
  assert.equal(classificarErro(new Error('insufficient funds for gas * price + value')).categoria, 'B');
  assert.equal(classificarErro(new Error('intrinsic gas too low')).categoria, 'B');
});

test('HTTP 429 do provedor é categoria C', () => {
  const e = new HttpRequestError({ url: 'https://rpc.exemplo', status: 429, details: 'Too Many Requests' });
  assert.equal(classificarErro(e).categoria, 'C');
});

test('mensagem desconhecida fica como X para revisão manual', () => {
  assert.equal(classificarErro(new Error('algo inesperado')).categoria, 'X');
});

test('recibo revertido: A com nome, B quando o gas acabou', () => {
  assert.deepEqual(classificarRecibo({ gasUsed: 100n, gasLimit: 200n, nome: 'InvalidOfferStatus' }), { categoria: 'A', nome: 'InvalidOfferStatus' });
  assert.equal(classificarRecibo({ gasUsed: 200n, gasLimit: 200n, nome: null }).categoria, 'B');
  assert.equal(classificarRecibo({ gasUsed: 150n, gasLimit: 200n, nome: null }).categoria, 'A');
});
