import os
from flask import Flask, render_template, request
from solana.publickey import PublicKey
from solana.rpc.async_api import AsyncClient
from asgiref.sync import async_to_sync

app = Flask(__name__)

async def get_solana_balance(wallet_address: str):
    async with AsyncClient("https://api.mainnet-beta.solana.com") as client:
        pubkey = PublicKey(wallet_address)
        balance = await client.get_balance(pubkey)
        sol_balance = balance['result']['value'] / 1e9  # перевод лампортов в SOL
        return sol_balance

def is_valid_solana_address(address: str) -> bool:
    try:
        PublicKey(address)
        return True
    except ValueError:
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/balance', methods=['POST'])
def balance():
    addresses = request.form['addresses'].splitlines()
    balances = {}
    for address in addresses:
        address = address.strip()
        if address and is_valid_solana_address(address):
            try:
                sol_balance = async_to_sync(get_solana_balance)(address)
                balances[address] = sol_balance
            except Exception as e:
                balances[address] = f"Error: {str(e)}"
        else:
            balances[address] = "Invalid address"
    return render_template('index.html', balances=balances)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))



