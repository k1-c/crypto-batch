# Crypto Batch
> crypto fowarding batches

## Requirements
- installation of [golang](https://golang.org/)
- [signer tool](https://github.com/blockcypher/btcutils/tree/master/signer)
> compile and place binary at ~/go/bin/signer or any

## How to use
```bash
# installation of signer tool
cd btcutils/signer
go build
mv signer ~/go/bin/signer

# execute
poetry shell
poetry install
python btc.py
```
