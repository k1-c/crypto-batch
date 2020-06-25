## DO THIS ON AN OFFLINE MACHINE, NOT YOUR WEBSERVER
import os
from os.path import join, dirname
from dotenv import load_dotenv
from bitmerchant.wallet import Wallet
import requests
import json
import subprocess
from subprocess import PIPE


load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


def sign(tosign, priv_key):
	proc = subprocess.run("~/go/bin/signer " + str(tosign) + " " + str(priv_key), shell=True, stdout=PIPE, stderr=PIPE, text=True)
	signature = proc.stdout
	return signature


""" config """
fee = int(os.environ.get('FEE'))
output_address = os.environ.get('OUTPUT_ADDRESS')
token = os.environ.get('BC_TOKEN')
master = Wallet.from_master_secret(seed=os.environ.get('SEED'))
crypto_url = os.environ.get('CRYPTO_URL')
""" ======= """


print(fee)
print(output_address)
print(token)
print(master.get_child(1, is_prime=False))

baseurl = 'https://api.blockcypher.com/v1/btc/main/'
childs = requests.get(crypto_url).json()

wallet_base = master.get_child(0, is_prime=True)

total_amount = 0
request_json = {
	"inputs": [],
	"outputs": [{"addresses": [output_address], "value": 0}],
	"fees": fee
}

for child in childs:
	if child['network'] == "BTC":
		tar_address = child['address']
		info = requests.get(baseurl + 'addrs/' + tar_address + '/balance' + '?token=' + token).json()
		print(info)
		if info['balance'] > 0:
			total_amount += info['balance']
			request_json["inputs"].append({"addresses": [tar_address]})

request_json['outputs'][0]['value'] = total_amount - fee

print(total_amount)
print(request_json)

tx = requests.post("https://api.blockcypher.com/v1/btc/main/txs/new", data=json.dumps(request_json)).json()
print(tx)
inputs = tx['tx']['inputs']
tosigns = tx['tosign']

path_list = []
signature_list = []
pubkey_list = []

for inp in inputs:
	print(inp['addresses'][0])
	paths = [x['path_index'] for x in childs if x['address'] == inp['addresses'][0]]
	path = paths[0] if len(paths) else ''
	# 先頭"m/0/"を抜いて格納
	path_list.append(path)

path_index = 0

for tosign in tosigns:
	key_base = wallet_base.get_child(path_list[path_index], is_prime=False)
	path_index += 1
# 	# print(key_base.to_address())
	priv_key = str(key_base.private_key.get_key())[1:].strip("'")
	pub_key = str(key_base.get_public_key_hex())[1:].strip("'")
	pubkey_list.append(pub_key)
	signature = sign(tosign=tosign, priv_key=priv_key).strip("\n")
	signature_list.append(signature)


tx['signatures'] = signature_list
tx['pubkeys'] = pubkey_list


print(json.dumps(tx))
