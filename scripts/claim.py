import json
import click
from brownie import Contract, accounts, network
from brownie.network.web3 import _resolve_address

def main():
    network.priority_fee('2 gwei')
    
    signer = accounts.load(click.prompt('signer', type=click.Choice(accounts.load())))
    merkle = Contract('0xcefc24e997807c0808D0F93a05ef21Db8Bb1cC42', owner=signer)
    claims = json.load(open('lexpunk-claims.json'))['claims']
    recipient = click.prompt('claim for', default=str(signer), value_proc=_resolve_address)
    
    if recipient not in claims:
        raise ValueError('no claim found')
    
    if merkle.isClaimed(0, claims[recipient]['index']):
        raise ValueError('already claimed')

    claim = claims[recipient]
    click.secho(f'claiming {claim["amount"] / 1e18:,.0f} L3X', fg='green')
    
    tx = merkle.claim(0, claim['index'], recipient, claim['amount'], claim['proof'])
    tx.info()
