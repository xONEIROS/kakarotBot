from web3 import Web3, Account
import json
import os
from dotenv import load_dotenv
from prompt_toolkit import prompt
import time

# Function to write private key to .env file
def save_private_key_to_env(private_key):
    with open('.env', 'w') as env_file:
        env_file.write(f'PRIVATE_KEYS=\'["{private_key}"]\'')

# Load environment variables
def load_env():
    load_dotenv()

# Constants
RPC_URL = 'https://sepolia-rpc.kakarot.org'
CHAIN_ID = 1802203764

def generate_random_address():
    return Web3.to_checksum_address(Web3.keccak(os.urandom(20))[:20].hex())

def display_header():
    header = r"""
     ____ ____ ____ ____ ____ ____ ____ 
    ||O |||N |||E |||I |||R |||O |||S ||
    ||__|||__|||__|||__|||__|||__|||__||
    |/__\|/__\|/__\|/__\|/__\|/__\|/__\|
    """
    twitter_link = "\033[92mhttps://x.com/0xOneiros\033[0m"
    print(header)
    print(twitter_link)

def get_valid_input(prompt_text, input_type=int):
    while True:
        try:
            return input_type(prompt(prompt_text))
        except ValueError:
            print(f"Please enter a valid {input_type.__name__}")

def main():
    display_header()

    # Get private key from user
    private_key = prompt('Please enter your private key: ')
    save_private_key_to_env(private_key)
    load_env()

    private_keys = json.loads(os.getenv('PRIVATE_KEYS', '[]'))

    provider = Web3(Web3.HTTPProvider(RPC_URL))
    wallets = []
    for private_key in private_keys:
        wallets.append(Account.from_key(private_key.strip()))

    if not wallets:
        print('No wallets found')
        return

    amount_to_send = get_valid_input('How much ETH do you want to send (in ETH): ', float)
    num_addresses = get_valid_input('How many addresses do you want to send to: ', int)

    amount_in_wei = Web3.to_wei(amount_to_send, 'ether')
    gas_price = provider.eth.gas_price

    delay_between_transactions = 5

    for wallet in wallets:
        balance = provider.eth.get_balance(wallet.address)
        balance_in_eth = Web3.from_wei(balance, 'ether')
        print(f'Wallet {wallet.address} balance: {balance_in_eth} ETH')

        if balance <= 0:
            print(f'Wallet {wallet.address} Insufficient balance. Skipping transactions for this wallet.')
            continue

        for _ in range(num_addresses):
            random_address = generate_random_address()
            tx = {
                'to': random_address,
                'value': amount_in_wei,
                'gas': 21000,
                'gasPrice': gas_price,
                'nonce': provider.eth.get_transaction_count(wallet.address),
                'chainId': CHAIN_ID
            }

            try:
                signed_tx = wallet.sign_transaction(tx)
                tx_hash = provider.eth.send_raw_transaction(signed_tx.raw_transaction)
                print(f'Sent {amount_to_send} ETH from {wallet.address} to {random_address}')
                print(f'Tx Hash: {tx_hash.hex()}')
            except Exception as e:
                print(f'Failed to send transaction from {wallet.address} to {random_address}:', e)

            if _ < num_addresses - 1:
                time.sleep(delay_between_transactions)

        if wallet != wallets[-1]:
            time.sleep(delay_between_transactions)

if __name__ == '__main__':
    main()
