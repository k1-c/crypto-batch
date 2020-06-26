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
master = Wallet.from_master_secret(seed=os.environ.get('OLD_SEED'))
crypto_url = os.environ.get('CRYPTO_URL')
""" ======= """


baseurl = 'https://api.blockcypher.com/v1/btc/main/'


addresses = [
	"1NPniCp3hMm9ckVvwpoaBiCCefXVPRREjY",
	"14Ju84DKiJ3VEu2RQGD9WDY6eBec3jD95g",
	"1B686RfBzoRshrYYX3XFLUzUCofuk8sHvz",
	"1CER1F29KLwLg5K1KCJwWCamMNN2YUGmBM",
	"18b61DAQJDh9y8SK8PxWdzA4zrtFNBms8J",
	"1KxrJyJ1XA2HeNFGVSd4Dmts7rLTpupK4H",
	"1G6yBDSttN5B2H4fJBLbFCk61NFhFDBwyZ",
	"1MCXDgfQ2cXmQ9ndwPgk7BbFhwC2oqsomk",
	"1HTFzbXxruCiN6vLVkXwm7G78jjwG3FuU1",
	"12LtjxU7NvTBund7ZYjXYFi3FS9uMoSvnM",
	"1En2WDNa9hUgCFX5LApubzMjhEAigXH6v3",
	"1BoKkeA5rwWEMcQb8EsFpwQSkVwArS85mZ"
]


wallet_base = master.get_child(0, is_prime=True)
print(wallet_base.serialize_b58(private=False))

LENGTH = 50
childs = []

for i in range(LENGTH):
	addr = wallet_base.get_child(i, is_prime=False).to_address()
	if addr in addresses:
		print('hit')
		childs.append({
			"address": addr,
			"path_index": i
		})


total_amount = 0
request_json = {
	"inputs": [],
	"outputs": [{"addresses": [output_address], "value": 0}],
	"fees": fee
}

for child in childs:
	tar_address = child['address']
	info = requests.get(baseurl + 'addrs/' + tar_address + '/balance' + '?token=' + token).json()
	print(info)
	if info['balance'] > 0:
		total_amount += info['balance']
		request_json["inputs"].append({"addresses": [tar_address]})


request_json['outputs'][0]['value'] = total_amount - fee


print(total_amount)
print(request_json)


tx = requests.post(baseurl + "txs/new", data=json.dumps(request_json)).json()
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
res = requests.post(baseurl + "txs/send?token=" + token, data=json.dumps(tx)).json()
print(res)
