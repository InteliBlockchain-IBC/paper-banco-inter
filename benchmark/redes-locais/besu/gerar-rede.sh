#!/usr/bin/env bash
# Gera uma rede Besu QBFT local com 4 validadores (mínimo para tolerância bizantina [R1])
# e sobe os nós com Docker Compose. Gas grátis: zeroBaseFee no gênesis + --min-gas-price=0.
#   ./gerar-rede.sh          gera chaves e gênesis (só na primeira vez) e sobe a rede
#   ./gerar-rede.sh --limpar apaga a rede e começa do zero (implantação nova, decisão B)
set -euo pipefail
cd "$(dirname "$0")"
IMAGEM="${BESU_IMAGEM:-hyperledger/besu:26.8.1}"

if [[ "${1:-}" == "--limpar" ]]; then
  docker compose down -v 2>/dev/null || true
  rm -rf rede
fi

if [[ ! -f rede/genesis.json ]]; then
  rm -rf rede && mkdir -p rede
  docker run --rm -u "$(id -u):$(id -g)" -v "$PWD:/w" "$IMAGEM" \
    operator generate-blockchain-config \
    --config-file=/w/qbftConfigFile.json --to=/w/rede/gerado --private-key-file-name=key
  cp rede/gerado/genesis.json rede/genesis.json
  i=1
  for dir in rede/gerado/keys/*/; do
    mkdir -p "rede/no$i/data"
    cp "$dir/key" "$dir/key.pub" "rede/no$i/data/"
    i=$((i + 1))
  done
fi

PUB=$(sed 's/^0x//' rede/no1/data/key.pub)
echo "BOOTNODE=enode://${PUB}@172.16.239.11:30303" > .env
echo "BESU_IMAGEM=${IMAGEM}" >> .env
docker compose up -d
echo "Aguardando o RPC em http://127.0.0.1:8545 ..."
for _ in $(seq 1 60); do
  if curl -s -X POST -H 'content-type: application/json' \
       --data '{"jsonrpc":"2.0","method":"qbft_getValidatorsByBlockNumber","params":["latest"],"id":1}' \
       http://127.0.0.1:8545 | grep -q result; then
    curl -s -X POST -H 'content-type: application/json' \
      --data '{"jsonrpc":"2.0","method":"qbft_getValidatorsByBlockNumber","params":["latest"],"id":1}' http://127.0.0.1:8545
    echo; echo "Rede no ar."; exit 0
  fi
  sleep 2
done
echo "A rede não respondeu em 120 s; veja 'docker compose logs'." >&2
exit 1
