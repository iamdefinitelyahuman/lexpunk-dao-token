#!/usr/bin/python3

from brownie import LeXpunK, MerkleDistributor, accounts


def main():
    deployer = accounts.load('deployer')
    admin = "0x8a7dbC2824AcaC4d272289a33b255C3F1f3cdf32"
    mint_address = deployer.get_deployment_address(deployer.nonce + 1)
    token = LeXpunK.deploy(admin, mint_address, {'from': deployer})
    minter = MerkleDistributor.deploy(deployer, token, {"from": deployer})
    assert minter == mint_address
