import json
import click
from brownie import Contract, accounts, network

def main():
    network.priority_fee('2 gwei')
    
    user = accounts.load(click.prompt("account", type=click.Choice(accounts.load())))
    
    merkle = Contract('0xcefc24e997807c0808D0F93a05ef21Db8Bb1cC42', owner=user)
    
    claims = json.load(open('lexpunk-claims.json'))['claims']
    
    if user not in claims:
        raise ValueError('no claim found')
    
    if merkle.isClaimed(0, claims[user]['index']):
        raise ValueError('already claimed')

    claim = claims[user]
    click.secho(f'claiming {claim["amount"] / 1e18:,.0f} L3X', fg='green')
    
    tx = merkle.claim(0, claim['index'], user, claim['amount'], claim['proof'])
    tx.info()
