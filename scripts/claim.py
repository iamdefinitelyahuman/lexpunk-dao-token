import json
import click
from brownie import Contract, accounts, network

def main():
    network.priority_fee('2 gwei')
    
    user = accounts.load(click.prompt("account", type=click.Choice(accounts.load())))
    
    merkle = Contract('0x0E31C3cA624C39E3f93AA2903290C0CA94125941', owner=user)
    lex = Contract('0x31337D24283390166ed1153E83182a615AA927cC')
    
    claims = json.load(open('lexpunk-claims.json'))['claims']
    
    if user not in claims:
        raise ValueError('no claim found')
    
    if merkle.isClaimed(0, claims[user]['index']):
        raise ValueError('already claimed')

    claim = claims[user]
    merkle.claim(0, claim['index'], claim['amount'], claim['proof'])

    print(f'{lex.balanceOf(user) / 1e18} L3X')
