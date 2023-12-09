from web3 import Web3
from hexbytes import HexBytes
from eth_account.messages import encode_defunct

w3 = Web3(Web3.HTTPProvider(""))


def get_address_by_sig_code(sig_code):
    try:
        message = encode_defunct(text="Signature code")
        sig_address = w3.eth.account.recover_message(message, signature=HexBytes(sig_code))
        print(sig_address)
    except Exception as e:
        print(e)