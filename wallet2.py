# Import dependencies
import subprocess
import json
import os
from dotenv import load_dotenv
load_dotenv()

# Import constants.py and necessary functions from bit and web3
from constants import *

# for BITTEST
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI

# #Python Ethereum 
from web3 import Web3
from getpass import getpass
from eth_account import Account
from pathlib import Path

#w3 provider
from web3 import Account
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

from web3.gas_strategies.time_based import medium_gas_price_strategy
w3.eth.setGasPriceStrategy(medium_gas_price_strategy)

from web3.middleware import geth_poa_middleware
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# set mnemonic environment variables
mnemonic = os.getenv('mnemonic', 'universe noble narrow cricket birth vendor camp tackle source right gown auction')

# Create a function called `derive_wallets`
def derive_wallets(coin, mnemonic, numderive=3):  
    command = f'php derive -g --coin={coin} --format=json --numderive={numderive} --mnemonic="{mnemonic}"'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    return json.loads(output)

# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = {}
coin_type = [BTC, ETH, BTCTEST]
for x in coin_type:
    coins[x] = derive_wallets(x, mnemonic)
    
# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, priv_key):  
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    elif coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)
    
# Set Privates keys for both eth & btctest
priv_key_eth = coins['eth'][0]['privkey']
priv_key_btctest = coins['btc-test'][0]['privkey']

# Set eth account
account_eth = priv_key_to_account(ETH, priv_key_eth)
print(account_eth.address)

# set btctest account
account_btctest = priv_key_to_account(BTCTEST, priv_key_btctest)
print(account_btctest.address)

# eth address to send transactions
address_eth = coins['eth'][0]['address']
print(address_eth)

# btctest address to send transactions
address_btctest = coins['btc-test'][1]['address']
print(address_btctest)

# New eth account to be pre-funded
address_eth2 = coins['eth'][1]['address']
print(address_eth2)

# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, to, amount):
    if coin == ETH:
        gasEstimate = w3.eth.estimateGas(
            {"from": account, "to": to, "value": amount}
        )

        return {
            "from": account,
            "to": to,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(account),
            "chainId": w3.eth.chain_id
        }
    elif coin==BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account, [(to, amount, BTC)])

# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account, to, amount): 
    raw_tx = create_tx(coin, account.address, to, amount)
    signed_tx = account.sign_transaction(raw_tx)
    
    if coin == ETH:
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print(result.hex())
        return result.hex()
    elif coin == BTCTEST:        
        result = NetworkAPI.broadcast_tx_testnet(signed_tx)
        return result
