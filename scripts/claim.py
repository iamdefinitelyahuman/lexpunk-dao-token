import json
import click
from brownie import Contract, accounts, network

def main():
    network.priority_fee('2 gwei')
    
    user = accounts.load(click.prompt("account", type=click.Choice(accounts.load())))
    
    merkle = Contract('0xcefc24e997807c0808D0F93a05ef21Db8Bb1cC42', owner=user)
    lex = Contract('0x1337C30c27FA619e66449BC95a69d2b1916124Dd')
    
    claims = json.load(open('lexpunk-claims.json'))['claims']
    
    if user not in claims:
        raise ValueError('no claim found')
    
    if merkle.isClaimed(0, claims[user]['index']):
        raise ValueError('already claimed')

    claim = claims[user]
    merkle.claim(0, claim['index'], claim['amount'], claim['proof'])

    print(f'{lex.balanceOf(user) / 1e18} L3X')
