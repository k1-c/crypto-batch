## DO THIS ON AN OFFLINE MACHINE, NOT YOUR WEBSERVER
import os
import sys
import csv
from bitmerchant.wallet import Wallet
import requests
import json
import subprocess
from subprocess import PIPE

def sign(tosign, priv_key):
	proc = subprocess.run("~/go/bin/signer " + str(tosign) + " " + str(priv_key), shell=True, stdout=PIPE, stderr=PIPE, text=True)
	signature = proc.stdout
	return signature

""" customs """
fee = 10000
wallet_name = 'xet'
output_address = '1KZXZCH6G5tvSshdHYTFnrxyNxAnHNYTA5'
token = '10e4ce7ef8994b9faa41a573f4bfd4dd'
my_wallet = Wallet.from_master_secret(seed='address alter walk later record visa organ hair pear stumble genuine fan')
""" ======= """

baseurl = 'https://api.blockcypher.com/v1/btc/main/'

# 残高のあるアドレス一覧の取得
get_wallet_url = baseurl + 'wallets/hd/' + wallet_name + '?token=' + token + '&zerobalance=false'
wallet = requests.get(get_wallet_url).json()
childs = wallet['chains'][0]['chain_addresses']

# デバッグ用
# print(wallet_list)
# print(path_list)

# 合計額集計用
total_amount = 0

result = []

request_json = {
	"inputs": [],
	"outputs": [{"addresses": [output_address], "value": 0}],
	"fees": fee
}

for child in childs:
	tar_address = child['address']
	info = requests.get(baseurl + 'addrs/' + tar_address + '/balance' + '?token=' + token).json()
	print(info)
	total_amount += info['balance']
	request_json["inputs"].append({"addresses": [tar_address]})

print(total_amount)
print(request_json)

request_json['outputs'][0]['value'] = total_amount - fee

tx = requests.post("https://api.blockcypher.com/v1/btc/main/txs/new", data=json.dumps(request_json)).json()
print(tx)
inputs = tx['tx']['inputs']
tosigns = tx['tosign']

path_list = []
signature_list = []
pubkey_list = []

for inp in inputs:
	print(inp['addresses'][0])
	paths = [x['path'] for x in childs if x['address'] == inp['addresses'][0]]
	path = paths[0] if len(paths) else ''
	# 先頭"m/0/"を抜いて格納
	path_list.append(path[4:])

path_index = 0

for tosign in tosigns:
	key_base = my_wallet.get_child_for_path(path="m/44'/0'/0'/0/" + str(path_list[path_index]))
	path_index += 1
	# print(key_base.to_address())
	print(tosign)
	priv_key = str(key_base.private_key.get_key())[1:].strip("'")
	print(priv_key)
	pub_key = str(key_base.get_public_key_hex())[1:].strip("'")
	pubkey_list.append(pub_key)
	print(pub_key)
	signature = sign(tosign=tosign, priv_key=priv_key).strip("\n")
	signature_list.append(signature)
	print(signature)

print(signature_list)
print(pubkey_list)

tx['signatures'] = signature_list
tx['pubkeys'] = pubkey_list

print('\n\n\n\n')
print(json.dumps(tx))