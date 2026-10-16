// Classificação de falhas da seção 5 do roteiro: a categoria sai do NOME do erro,
// não do momento em que ele aparece.
//   A  erro do contrato ou do token         (fora de C1)
//   B  erro do cliente de teste             (fora de C1)
//   C  rejeição do provedor de RPC          (fora de C1)
//   D  falha da rede: hash recebido, sem recibo no tempo limite (conta em C1)
//   X  não reconhecida: precisa de revisão manual antes da análise
import { BaseError, ContractFunctionRevertedError, decodeErrorResult } from 'viem';

// Erros definidos no código do time (seção 5, categoria A) [R13].
export const ERROS_CONTRATO = new Set([
  'InsufficientLimit', 'OfferHasExpired', 'InvalidOfferStatus', 'NotEligibleBorrower',
  'NotOfferOwner', 'NotRegisteredInstitution', 'InvalidOfferParameters', 'InvalidValidityWindow',
  'InvalidCounterparty', 'OfferNotFound', 'OfferNotYetExpired', 'ZeroAddress',
  'ERC20InsufficientAllowance', 'ERC20InsufficientBalance', 'ReentrancyGuardReentrantCall',
  'AccessControlUnauthorizedAccount',
]);

const PADROES_CLIENTE = [
  /nonce too low/i, /nonce too high/i, /invalid nonce/i, /replacement transaction underpriced/i,
  /already known/i, /known transaction/i, /insufficient funds/i, /intrinsic gas too low/i,
  /gas too low/i, /out of gas/i, /invalid signature/i, /invalid sender/i, /max fee per gas less than block base fee/i,
  /transaction underpriced/i, /fee cap less than block base fee/i, /exceeds block gas limit/i,
];

const PADROES_RPC = [
  /429/, /too many requests/i, /rate limit/i, /limit exceeded/i, /request limit/i, /capacity/i,
  /fetch failed/i, /ECONNRESET/, /ECONNREFUSED/, /ETIMEDOUT/, /socket hang up/i, /502/, /503/, /504/,
  /The request took too long/i,
];

function mensagens(err) {
  const partes = [];
  let e = err;
  for (let i = 0; e && i < 10; i++) {
    for (const campo of ['shortMessage', 'details', 'message']) if (typeof e[campo] === 'string') partes.push(e[campo]);
    if (e.status) partes.push(String(e.status));
    e = e.cause;
  }
  return partes.join(' | ');
}

function nomeRevert(err, abiErros) {
  if (err instanceof BaseError) {
    const revert = err.walk((e) => e instanceof ContractFunctionRevertedError);
    if (revert?.data?.errorName) return revert.data.errorName;
    // Alguns nós devolvem o revert como dado bruto em vez de erro decodificado.
    const comDados = err.walk((e) => typeof e?.data === 'string' && e.data.startsWith('0x') && e.data.length >= 10);
    if (comDados && abiErros) {
      try {
        return decodeErrorResult({ abi: abiErros, data: comDados.data }).errorName;
      } catch {
        /* segue para os padrões de texto */
      }
    }
  }
  const texto = mensagens(err);
  for (const nome of ERROS_CONTRATO) if (texto.includes(nome)) return nome;
  return null;
}

/**
 * Classifica uma exceção lançada na estimativa ou no envio.
 * @returns {{ categoria: 'A'|'B'|'C'|'X', nome: string }}
 */
export function classificarErro(err, abiErros) {
  const nome = nomeRevert(err, abiErros);
  if (nome) return { categoria: 'A', nome };
  const texto = mensagens(err);
  const curto = (texto.split(' | ')[0] || String(err)).slice(0, 160);
  if (PADROES_CLIENTE.some((p) => p.test(texto))) return { categoria: 'B', nome: curto };
  if (PADROES_RPC.some((p) => p.test(texto))) return { categoria: 'C', nome: curto };
  if (/execution reverted/i.test(texto)) return { categoria: 'A', nome: 'execution reverted (sem nome)' };
  return { categoria: 'X', nome: curto };
}

/** Recibo com status `reverted`: categoria A, ou B se o gas acabou (o limite foi baixo demais). */
export function classificarRecibo({ gasUsed, gasLimit, nome }) {
  if (nome) return { categoria: 'A', nome };
  if (gasLimit && gasUsed >= gasLimit) return { categoria: 'B', nome: 'out of gas' };
  return { categoria: 'A', nome: 'revert sem nome (recibo)' };
}

export const FALHA_TEMPO_LIMITE = Object.freeze({ categoria: 'D', nome: 'sem recibo no tempo limite' });
